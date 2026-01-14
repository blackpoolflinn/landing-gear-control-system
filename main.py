from enum import Enum, auto

class GearState(Enum):
    """States of the landing gear system."""
    UP_LOCKED = auto()
    TRANSITIONING_DOWN = auto()
    TRANSITIONING_UP = auto()
    DOWN_LOCKED = auto()

class GearLeg:
    """
    Gear leg with time-based transitions.
    Commands start motion; tick(dt) completes it once enough time has passed.
    """
    def __init__(self, name: str, deploy_time_s: float = 2.5, retract_time_s: float = 2.5):
        self.name = name
        self.state = GearState.UP_LOCKED
        self.deploy_time_s = deploy_time_s
        self.retract_time_s = retract_time_s
        self.timer_s = 0.0

    def command_down(self) -> bool:
        """Sends command to lower the gear leg and returns True if command accepted."""
        if self.state != GearState.UP_LOCKED:
            return False
        self.state = GearState.TRANSITIONING_DOWN
        self.timer_s = 0.0
        return True

    def command_up(self) -> bool:
        """Sends command to raise the gear leg and returns True if command accepted."""
        if self.state != GearState.DOWN_LOCKED:
            return False
        self.state = GearState.TRANSITIONING_UP
        self.timer_s = 0.0
        return True

    def tick(self, dt_s: float) -> None:
        """Advances the state by dt_s seconds."""
        if self.state == GearState.TRANSITIONING_DOWN:
            self.timer_s += dt_s
            if self.timer_s >= self.deploy_time_s:
                self.state = GearState.DOWN_LOCKED

        elif self.state == GearState.TRANSITIONING_UP:
            self.timer_s += dt_s
            if self.timer_s >= self.retract_time_s:
                self.state = GearState.UP_LOCKED


class LandingGearController:
    def __init__(self):
        self.legs = [GearLeg("nose"), GearLeg("left"), GearLeg("right")]

    def log_leg(self, leg: GearLeg, message: str) -> None:
        print(f"[{leg.name.upper()} | {leg.state.name}] {message}")

    def command_all_down(self) -> None:
        """Sends command to lower all landing gear legs."""
        for leg in self.legs:
            ok = leg.command_down()
            self.log_leg(leg, "DOWN command accepted" if ok else "DOWN command rejected")

    def command_all_up(self) -> None:
        """Sends command to raise all landing gear legs."""
        for leg in self.legs:
            ok = leg.command_up()
            self.log_leg(leg, "UP command accepted" if ok else "UP command rejected")

    def tick(self, dt_s: float) -> None:
        """Advances the state of all legs by dt_s seconds."""
        for leg in self.legs:
            before = leg.state
            leg.tick(dt_s)
            if leg.state != before:
                self.log_leg(leg, f"Transition complete: {before.name} -> {leg.state.name}")


if __name__ == "__main__":
    lgcs = LandingGearController()

    lgcs.command_all_down()
    for _ in range(6):  # 6 x 0.5s = 3.0s simulated
        lgcs.tick(0.5)

    lgcs.command_all_up()
    for _ in range(6):
        lgcs.tick(0.5)
