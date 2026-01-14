from enum import Enum, auto

class GearState(Enum):
    """States of the landing gear system."""
    UP_LOCKED = auto()
    TRANSITIONING_DOWN = auto()
    TRANSITIONING_UP = auto()
    DOWN_LOCKED = auto()

class GearLeg:
    """Represents a single landing gear leg."""
    def __init__(self, name: str):
        self.name = name
        self.state = GearState.UP_LOCKED

    def command_down(self) -> bool:
        if self.state != GearState.UP_LOCKED:
            return False
        self.state = GearState.TRANSITIONING_DOWN
        self.state = GearState.DOWN_LOCKED
        return True

    def command_up(self) -> bool:
        if self.state != GearState.DOWN_LOCKED:
            return False
        self.state = GearState.TRANSITIONING_UP
        self.state = GearState.UP_LOCKED
        return True


class LandingGearController:
    """Controls three independent legs (nose/left/right)."""
    def __init__(self):
        self.legs = {
            "nose": GearLeg("nose"),
            "left": GearLeg("left"),
            "right": GearLeg("right"),
        }

    def log_leg(self, leg: GearLeg, message: str) -> None:
        print(f"[{leg.name.upper()} | {leg.state.name}] {message}")

    def command_gear_down(self) -> None:
        """Sends command to lower all landing gear legs."""
        for leg in self.legs.values():
            ok = leg.command_down()
            self.log_leg(leg, "DOWN command accepted" if ok else "DOWN command rejected")

    def command_gear_up(self) -> None:
        """Sends command to raise all landing gear legs."""
        for leg in self.legs.values():
            ok = leg.command_up()
            self.log_leg(leg, "UP command accepted" if ok else "UP command rejected")


if __name__ == "__main__":
    lgcs = LandingGearController()
    lgcs.command_gear_down()
    lgcs.command_gear_up()
