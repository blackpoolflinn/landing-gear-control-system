import json
import tempfile
import unittest

from config_loader import load_config


class TestConfigLoader(unittest.TestCase):
    def test_loads_values_from_json(self):
        data = {
            "timings": {"deploy_time_s": 1.0, "retract_time_s": 1.5},
            "interlocks": {"allow_down_from": ["UP_LOCKED"], "allow_up_from": ["DOWN_LOCKED"]},
            "logging": {"level": "DEBUG"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f)
            path = f.name

        cfg = load_config(path)

        self.assertEqual(cfg.timings.deploy_time_s, 1.0)
        self.assertEqual(cfg.timings.retract_time_s, 1.5)
        self.assertEqual(cfg.logging.level, "DEBUG")

    def test_defaults_when_missing(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({}, f)
            path = f.name

        cfg = load_config(path)

        self.assertEqual(cfg.timings.deploy_time_s, 2.5)
        self.assertEqual(cfg.timings.retract_time_s, 2.5)
        self.assertEqual(cfg.logging.level, "INFO")


if __name__ == "__main__":
    unittest.main()
