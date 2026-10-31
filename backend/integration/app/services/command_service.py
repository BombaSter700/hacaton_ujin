import logging
import uuid
import json
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.device import Device, Signal
from app.models.command_log import CommandLog, CommandStatus
from app.api.v1.schemas.command import CommandRequest, CommandResponse
from app.integrations.ujin.client import UjinClient
from app.services.analytics import analytics

logger = logging.getLogger(__name__)


class CommandService:
    def __init__(self, ujin_client: UjinClient):
        self.ujin = ujin_client

    async def process_command(
        self, db: Session, device: Device, cmd_in: CommandRequest, user_id: UUID
    ) -> CommandResponse:

        # защита от двойного клика
        if cmd_in.idempotency_key:
            existing_cmd = (
                db.query(CommandLog)
                .filter(CommandLog.idempotency_key == cmd_in.idempotency_key)
                .first()
            )

            if existing_cmd:
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signal not found for this device",
            )

        if not signal.is_writable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This signal is read-only",
            )

        # Проверка границ (min/max), если это число
        if isinstance(cmd_in.value, (int, float)):
            if signal.min_value is not None and cmd_in.value < signal.min_value:
                raise HTTPException(
                    status_code=400, detail=f"Value below minimum {signal.min_value}"
                )
            if signal.max_value is not None and cmd_in.value > signal.max_value:
                raise HTTPException(
                    status_code=400, detail=f"Value above maximum {signal.max_value}"
                )

        # Создаем запись в логе
        db_cmd = CommandLog(
            user_id=user_id,
            device_id=device.id,
            signal_id=signal.id,
            value={"value": cmd_in.value},  # JSON требует dict или list, оборачиваем
            idempotency_key=cmd_in.idempotency_key,
            status=CommandStatus.PENDING,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        db.add(db_cmd)
        db.commit()
        db.refresh(db_cmd)

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
        # Отправка в Ujin
        try:
            # Формируем payload для Ujin, nзависит от их API
            payload = {"signal_id": signal.external_signal_id, "value": cmd_in.value}

            # Вызов клиента
            await self.ujin.send_command(
            device_external_id=device.external_id, 
            signal_name=signal.external_signal_id, 
            value=cmd_in.value
            )

            # Успешное выполнение
            db_cmd.status = CommandStatus.SUCCESS
            db_cmd.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(db_cmd)

            analytics.log_event(
                table="audit_events",
                data={
                    "event_id": uuid.uuid4(),
                    "source_service": "integration",
                    "event_type": "command_success",
                    "severity": "info",
                    "occurred_at": datetime.now(timezone.utc),
                    "actor_id": str(user_id),
                    "actor_type": "user",
                    "entity_type": "device",
                    "entity_id": str(device.id),
                    "context": json.dumps({"command_id": str(db_cmd.id)})
                }
            )

            return CommandResponse(
                command_id=db_cmd.id,
                status=db_cmd.status.value,
                created_at=db_cmd.created_at,
                completed_at=db_cmd.completed_at,
            )

        except Exception as e:
            # Обработка ошибки внешней платформы
            logger.error(f"Failed to send command to Ujin: {e}")

            db_cmd.status = CommandStatus.FAILED
            db_cmd.error_message = str(e)
            db_cmd.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(db_cmd)

            analytics.log_event(
                table="audit_events",
                data={
                    "event_id": uuid.uuid4(),
                    "source_service": "integration",
                    "event_type": "command_failed",
                    "severity": "error",
                    "occurred_at": datetime.now(timezone.utc),
                    "actor_id": str(user_id),
                    "actor_type": "user",
                    "entity_type": "device",
                    "entity_id": str(device.id),
                    "context": json.dumps({"command_id": str(db_cmd.id), "error": str(e)})
                }
            )
            # Возвращаем ответ, но со статусом FAILED.
            return CommandResponse(
                command_id=db_cmd.id,
                status=db_cmd.status.value,
                message=f"External platform error: {str(e)}",
                created_at=db_cmd.created_at,
                completed_at=db_cmd.completed_at,
            )
