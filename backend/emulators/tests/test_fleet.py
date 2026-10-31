import json
from pathlib import Path
import tempfile
import unittest

from backend.emulators.fleet import load_config


class FleetConfigTest(unittest.TestCase):
    def load(self, devices):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fleet.json"
            path.write_text(json.dumps(devices), encoding="utf-8")
            return load_config(path, 8098)

    def test_default_fleet_contains_all_families(self):
        from backend.emulators.devices import REGISTRY
        path = Path(__file__).parents[1] / "fleet.json"
        devices = load_config(path, 8098)
        self.assertEqual({d["family"] for d in devices}, set(REGISTRY))

    def test_port_conflicts_and_duplicate_identity_are_rejected(self):
        first = {"family": "leak", "serial": "one", "port": 8099}
        for second in (
            {"family": "fire", "serial": "two", "port": 8099},
            {"family": "fire", "serial": "one", "port": 8100},
            {"family": "fire", "serial": "two", "port": 8098},
        ):
            with self.subTest(second=second), self.assertRaises(ValueError):
                self.load([first, second])

    def test_invalid_device_configuration_is_rejected(self):
        for devices in ([], [{"family": "unknown", "serial": "one", "port": 8099}],
                        [{"family": "leak", "serial": "", "port": 8099}],
                        [{"family": "leak", "serial": "one", "port": -1}]):
            with self.subTest(devices=devices), self.assertRaises(ValueError):
                self.load(devices)
