import unittest

from main import GearLeg, GearState


class TestGearLeg(unittest.TestCase):
    def test_down_command_starts_transition(self):
        leg = GearLeg("nose", deploy_time_s=1.0, retract_time_s=1.0)

        ok = leg.command("DOWN", allow_from=["UP_LOCKED"])

        self.assertTrue(ok)
        self.assertEqual(leg.state, GearState.TRANSITIONING_DOWN)
        self.assertTrue(leg.in_transit_sensor)

    def test_tick_completes_deploy(self):
        leg = GearLeg("nose", deploy_time_s=1.0, retract_time_s=1.0)

        leg.command("DOWN", allow_from=["UP_LOCKED"])
        leg.tick(1.0)

        self.assertEqual(leg.state, GearState.DOWN_LOCKED)
        self.assertTrue(leg.downlock_sensor)


if __name__ == "__main__":
    unittest.main()
