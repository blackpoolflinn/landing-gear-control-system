import json
import tempfile
import unittest
import logging

from config_loader import load_config

class TestConfigLoader(unittest.TestCase):
    def test_loads_values_from_json(self):
        """Test that values are correctly loaded from JSON file.
        
        Validates Requirements:
        - REQ-007: Configuration Loading (loads timings, interlocks, and logging config from JSON)
        """
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
        """Test that missing values fall back to defaults.
        
        Validates Requirements:
        - REQ-007: Configuration Loading (applies default values when config is missing)
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({}, f)
            path = f.name

        cfg = load_config(path)

        self.assertEqual(cfg.timings.deploy_time_s, 2.5)
        self.assertEqual(cfg.timings.retract_time_s, 2.5)
        self.assertEqual(cfg.logging.level, "INFO")

    def test_logs_config_loading(self):
        """Test that loading config produces log output.
        
        Validates Requirements:
        - REQ-007: Configuration Loading (logging support during config load)
        """
        data = {
            "timings": {"deploy_time_s": 1.5, "retract_time_s": 2.0},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f)
            path = f.name

        logger = logging.getLogger('config_loader')
        logger.handlers = []
        handler = logging.FileHandler(tempfile.gettempdir() + '/test_config.log')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        cfg = load_config(path)

        self.assertEqual(cfg.timings.deploy_time_s, 1.5)
        self.assertEqual(cfg.timings.retract_time_s, 2.0)


if __name__ == "__main__":
    unittest.main()
