import logging
import uuid
import json
import asyncio
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.device import Device, Signal
from app.models.command_log import CommandLog, CommandStatus
from app.api.v1.schemas.command import CommandRequest, CommandResponse
from app.integrations.emulator.client import EmulatorAdapter
from app.services.analytics import analytics
from app.core.config import settings

logger = logging.getLogger(__name__)


class CommandService:
    async def process_command(
        self, db: Session, device: Device, cmd_in: CommandRequest, user_id: int
    ) -> CommandResponse:

        # Защита от двойного клика 
        if cmd_in.idempotency_key:
            existing_cmd = (
                db.query(CommandLog)
                .filter(
                    CommandLog.user_id == user_id, 
                    CommandLog.idempotency_key == cmd_in.idempotency_key
                )
                .first()
            )

            if existing_cmd:
                if existing_cmd.device_id != device.id or existing_cmd.signal_id != cmd_in.signal_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Idempotency key used for different command payload"
                    )
                
                logger.info(f"Idempotent hit for key: {cmd_in.idempotency_key}")
                return CommandResponse(
                    command_id=existing_cmd.id,
                    status=existing_cmd.status.value,
                    message=existing_cmd.error_message or "Command already processed",
                    created_at=existing_cmd.created_at,
                    completed_at=existing_cmd.completed_at,
                )

        # Валидация сигнала
        signal = (
            db.query(Signal)
            .filter(Signal.id == cmd_in.signal_id, Signal.device_id == device.id)
            .first()
        )

        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found for this device")

        if not signal.is_writable:
            raise HTTPException(status_code=400, detail="This signal is read-only")

        if isinstance(cmd_in.value, (int, float)):
            if signal.min_value is not None and cmd_in.value < signal.min_value:
                raise HTTPException(status_code=400, detail=f"Value below minimum {signal.min_value}")
            if signal.max_value is not None and cmd_in.value > signal.max_value:
                raise HTTPException(status_code=400, detail=f"Value above maximum {signal.max_value}")

        # Создаем запись в логе 
        db_cmd = CommandLog(
            user_id=user_id,
            device_id=device.id,
            signal_id=signal.id,
            value={"value": cmd_in.value},
            idempotency_key=cmd_in.idempotency_key,
            status=CommandStatus.PENDING,
            created_at=datetime.now(timezone.utc)
        )
        
        try:
            db.add(db_cmd)
            db.commit()
            db.refresh(db_cmd)
        except IntegrityError:
            # Защита от Race Condition
            db.rollback()
            existing = db.query(CommandLog).filter_by(user_id=user_id, idempotency_key=cmd_in.idempotency_key).first()
            return CommandResponse(
                command_id=existing.id, status=existing.status.value, message="Concurrent request handled"
            )

        # Click House
        analytics.log_event(
            table="audit_events",
            data={
                "event_id": uuid.uuid4(),
                "source_service": "integration",
                "event_type": "command_pending",
                "severity": "info",
                "occurred_at": datetime.now(timezone.utc),
                "actor_id": str(user_id),
                "actor_type": "user",
                "entity_type": "device",
                "entity_id": str(device.id),
                "trace_id": None,
                "context": json.dumps({"command_id": str(db_cmd.id), "signal_id": str(signal.id), "value": str(cmd_in.value)})
            }
        )

        # Отправка в эмулятор и ПОДТВЕРЖДЕНИЕ
        if not device.base_url:
            db_cmd.status = CommandStatus.FAILED
            db_cmd.error_message = "Device has no base_url configured"
            db.commit()
            return CommandResponse(command_id=db_cmd.id, status=db_cmd.status.value, message=db_cmd.error_message)

        adapter = EmulatorAdapter(base_url=device.base_url)
        confirmed = False

        try:
            sent = await adapter.send_command(signal.external_signal_id, cmd_in.value)
            if not sent:
                raise RuntimeError("Adapter rejected the command (HTTP error)")

            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < settings.command_confirmation_timeout:
                await asyncio.sleep(settings.command_confirmation_poll_interval)
                state = await adapter.get_state()
                
                current_val = state.get("signals", {}).get(signal.external_signal_id)
                if str(current_val).lower() == str(cmd_in.value).lower():
                    confirmed = True
                    break

            if not confirmed:
                db_cmd.status = CommandStatus.TIMEOUT
                db_cmd.error_message = "Command sent but state was not confirmed in time"
            else:
                db_cmd.status = CommandStatus.SUCCESS

        except Exception as e:
            logger.error(f"Error sending command: {e}")
            db_cmd.status = CommandStatus.FAILED
            db_cmd.error_message = str(e)

        db_cmd.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_cmd)

        # Click House 
        analytics.log_event(
            table="audit_events",
            data={
                "event_id": uuid.uuid4(),
                "source_service": "integration",
                "event_type": f"command_{db_cmd.status.value}",
                "severity": "info" if confirmed else "error",
                "occurred_at": datetime.now(timezone.utc),
                "actor_id": str(user_id),
                "actor_type": "user",
                "entity_type": "device",
                "entity_id": str(device.id),
                "context": json.dumps({"command_id": str(db_cmd.id), "status": db_cmd.status.value, "error": db_cmd.error_message})
            }
        )

        return CommandResponse(
            command_id=db_cmd.id,
            status=db_cmd.status.value,
            message=db_cmd.error_message,
            created_at=db_cmd.created_at,
            completed_at=db_cmd.completed_at,
        )