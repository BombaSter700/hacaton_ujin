"""Shared value and reference validation. No automatic rule execution here."""
import math
from fastapi import HTTPException
from app.models.device import Device
from app.api.v1.schemas.scenario import SignalCondition


def validate_value(signal, value, check_range=True):
    value_type = signal.value_type
    if value_type == "number":
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"{signal.name}: expected a finite number")
        if check_range:
            if signal.min_value is not None and value < signal.min_value:
                raise ValueError(f"{signal.name}: value below minimum {signal.min_value}")
            if signal.max_value is not None and value > signal.max_value:
                raise ValueError(f"{signal.name}: value above maximum {signal.max_value}")
    elif value_type == "boolean" and type(value) is not bool:
        raise ValueError(f"{signal.name}: expected true or false")
    elif value_type == "string" and not isinstance(value, str):
        raise ValueError(f"{signal.name}: expected text")


def validate_definition(db, definition):
    """Reject stale signals, cross-object references and unavailable commands."""
    refs = [c for c in definition.conditions if isinstance(c, SignalCondition)] + definition.actions
    ids = {ref.device_id for ref in refs}
    devices = {device.id: device for device in db.query(Device).filter(Device.id.in_(ids)).all()}
    try:
        for ref in refs:
            device = devices.get(ref.device_id)
            if not device or device.object_id != definition.object_id:
                raise ValueError("Every device must belong to the selected object")
            signal = next((s for s in device.signals if s.id == ref.signal_id), None)
            if signal is None:
                raise ValueError("Signal does not belong to the selected device")
            is_condition = isinstance(ref, SignalCondition)
            if not is_condition and not signal.is_writable:
                raise ValueError(f"{signal.name}: signal is read-only")
            if is_condition and signal.value_type != "number" and ref.operator not in ("eq", "ne"):
                raise ValueError("Only numeric signals support ordered comparisons")
            # Thresholds may be outside the hardware command range.
            validate_value(signal, ref.value, check_range=not is_condition)
    except ValueError as error:
        raise HTTPException(422, str(error)) from None
