from enum import Enum, auto

class GearState(Enum):
    """States of the landing gear system."""
    UP_LOCKED = auto()
    TRANSITIONING_DOWN = auto()
    TRANSITIONING_UP = auto()
    DOWN_LOCKED = auto()

class LandingGearController:
    """A simple landing gear control system."""
    def __init__(self):
        self.state = GearState.UP_LOCKED
    
    def log(self, message):
        """Log the current state and message."""
        print(f"[{self.state.name}] {message}")

    def command_gear_down(self):
        """Command to lower the landing gear."""
        if self.state == GearState.UP_LOCKED:
            self.state = GearState.TRANSITIONING_DOWN
            self.log("Gear deploying")
            self.state = GearState.DOWN_LOCKED
            self.log("Gear locked down")
        else:
            self.log("Command rejected")
    
    def command_gear_up(self):
        """Command to raise the landing gear."""
        if self.state == GearState.DOWN_LOCKED:
            self.state = GearState.TRANSITIONING_UP
            self.log("Gear retracting")
            self.state = GearState.UP_LOCKED
            self.log("Gear locked up")
        else:
            self.log("Command rejected")

# Example usage
controller = LandingGearController()
controller.command_gear_down()
controller.command_gear_up()