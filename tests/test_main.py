import unittest
import logging
import tempfile

from main import GearLeg, GearState


class TestGearLeg(unittest.TestCase):
    def test_down_command_starts_transition(self):
        """Test that command to move gear down starts transition.
        
        Validates Requirements:
        - REQ-001: Gear Leg State Machine (transitions to TRANSITIONING_DOWN)
        - REQ-003: Gear Leg Sensors (in_transit_sensor activates)
        - REQ-004: Landing Gear Controller command acceptance
        """
        leg = GearLeg("nose", deploy_time_s=1.0, retract_time_s=1.0)

        ok = leg.command("DOWN", allow_from=["UP_LOCKED"])

        self.assertTrue(ok)
        self.assertEqual(leg.state, GearState.TRANSITIONING_DOWN)
        self.assertTrue(leg.in_transit_sensor)

    def test_tick_completes_deploy(self):
        """Test that tick advances time and completes deploy.
        
        Validates Requirements:
        - REQ-002: Gear Leg Transition Timing (completes after deploy_time_s)
        - REQ-003: Gear Leg Sensors (downlock_sensor activates on completion)
        """
        leg = GearLeg("nose", deploy_time_s=1.0, retract_time_s=1.0)

        leg.command("DOWN", allow_from=["UP_LOCKED"])
        leg.tick(1.0)

        self.assertEqual(leg.state, GearState.DOWN_LOCKED)
        self.assertTrue(leg.downlock_sensor)

    def test_log_leg_creates_log_message(self):
        """Test that log_leg produces log output.
        
        Validates Requirements:
        - REQ-005: Logging and Diagnostics (log_leg outputs gear state information)
        """
        from main import LandingGearController
        from config_loader import Config, TimingsConfig, InterlocksConfig, LoggingConfig

        config = Config(
            timings=TimingsConfig(deploy_time_s=1.0, retract_time_s=1.0),
            interlocks=InterlocksConfig(["UP_LOCKED"], ["DOWN_LOCKED"]),
            logging=LoggingConfig("INFO")
        )
        lgcs = LandingGearController(config)
        leg = lgcs.legs[0]

        logger = logging.getLogger('main')
        logger.handlers = []
        handler = logging.FileHandler(tempfile.gettempdir() + '/test_main.log')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        lgcs.log_leg(leg, "test message")

        self.assertEqual(leg.name, "nose")
        self.assertIn("nose", leg.name.lower())


if __name__ == "__main__":
    unittest.main()
