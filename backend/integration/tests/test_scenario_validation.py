import unittest
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import MagicMock
from fastapi import HTTPException
from pydantic import ValidationError
from app.api.v1.schemas.device_definition import DeviceDefinition
from app.api.v1.schemas.scenario import ScenarioCreate, TimeCondition
from app.services.scenario_validation import validate_definition, validate_value


class ScenarioValidationTests(unittest.TestCase):
    def setUp(self):
        self.object_id, self.device_id, self.signal_id = uuid4(), uuid4(), uuid4()
        self.signal = SimpleNamespace(id=self.signal_id, name="Target", value_type="number", min_value=16, max_value=30, is_writable=True)
        self.device = SimpleNamespace(id=self.device_id, object_id=self.object_id, signals=[self.signal])
        self.db = MagicMock()
        self.db.query.return_value.filter.return_value.all.return_value = [self.device]
        self.payload = dict(object_id=self.object_id, name="Day mode", conditions=[dict(kind="time", start_time="08:00", end_time="22:00", timezone="Europe/Moscow")], actions=[dict(device_id=self.device_id, signal_id=self.signal_id, value=24)])

    def test_timezones_and_clock_values_are_validated(self):
        for start, zone in [("25:00", "UTC"), ("08:00", "Unknown/Zone")]:
            with self.assertRaises(ValidationError):
                TimeCondition(kind="time", start_time=start, end_time="22:00", timezone=zone)
        TimeCondition(kind="time", start_time="22:00", end_time="06:00", timezone="UTC")

    def test_empty_rules_and_extra_fields_are_rejected(self):
        for changes in ({"conditions": []}, {"actions": []}, {"execute_now": True}, {"name": "   "}):
            with self.assertRaises(ValidationError):
                ScenarioCreate(**(self.payload | changes))

    def test_values_are_strict_and_finite(self):
        for value in ("24", True, float("nan"), float("inf"), 31):
            with self.assertRaises(ValueError):
                validate_value(self.signal, value)
        validate_value(self.signal, 24)
        self.signal.value_type = "boolean"
        validate_value(self.signal, False)
        with self.assertRaises(ValueError):
            validate_value(self.signal, 0)

    def test_cross_object_and_unknown_signals_are_rejected(self):
        for changes in ({"object_id": uuid4()}, {"actions": [dict(device_id=self.device_id, signal_id=uuid4(), value=24)]}):
            with self.assertRaises(HTTPException) as exc:
                validate_definition(self.db, ScenarioCreate(**(self.payload | changes)))
            self.assertEqual(exc.exception.status_code, 422)

    def test_read_only_actions_rejected(self):
        self.signal.is_writable = False
        with self.assertRaises(HTTPException):
            validate_definition(self.db, ScenarioCreate(**self.payload))

    def test_threshold_does_not_use_command_range(self):
        self.payload["conditions"] = [dict(kind="signal", device_id=self.device_id, signal_id=self.signal_id, operator="gt", value=100)]
        validate_definition(self.db, ScenarioCreate(**self.payload))
        self.signal.value_type = "string"
        self.payload["conditions"][0]["value"] = "hot"
        self.payload["actions"][0]["value"] = "cool"
        with self.assertRaises(HTTPException):
            validate_definition(self.db, ScenarioCreate(**self.payload))

    def test_definition_duplicate_ids_and_bad_ranges_rejected(self):
        signal = dict(id=self.signal_id, name="Target", value_type="number", is_writable=True, min_value=30, max_value=16)
        with self.assertRaises(ValidationError):
            DeviceDefinition(name="Thermostat", signals=[signal])
        signal.update(min_value=16, max_value=30)
        with self.assertRaises(ValidationError):
            DeviceDefinition(name="Thermostat", signals=[signal, signal])
        signal["value_type"] = "boolean"
        with self.assertRaises(ValidationError):
            DeviceDefinition(name="Thermostat", signals=[signal])


if __name__ == "__main__":
    unittest.main()
