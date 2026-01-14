from enum import Enum, auto
from dataclasses import dataclass
import time

class GearState(Enum):
    """States of a landing gear leg."""
    UP_LOCKED = auto()
    TRANSITIONING_DOWN = auto()
    DOWN_LOCKED = auto()
    TRANSITIONING_UP = auto()

@dataclass
class GearLeg:
    """Represents a single landing gear leg with state and timing."""
    name: str
    deploy_time_s: float = 2.5
    retract_time_s: float = 2.5
    state: GearState = GearState.UP_LOCKED
    timer_s: float = 0.0

    @property
    def uplock_sensor(self) -> bool:
        """Indicates if the gear is locked in the UP position."""
        return self.state == GearState.UP_LOCKED

    @property
    def downlock_sensor(self) -> bool:
        """Indicates if the gear is locked in the DOWN position."""
        return self.state == GearState.DOWN_LOCKED

    @property
    def in_transit_sensor(self) -> bool:
        """Indicates if the gear is currently transitioning."""
        return self.state in (GearState.TRANSITIONING_DOWN, GearState.TRANSITIONING_UP)

    def command(self, direction: str) -> bool:
        """
        direction: "DOWN" or "UP"
        Starts a transition if allowed, does NOT complete it instantly.
        """
        if direction == "DOWN" and self.state == GearState.UP_LOCKED:
            self.state = GearState.TRANSITIONING_DOWN
            self.timer_s = 0.0
            return True

        if direction == "UP" and self.state == GearState.DOWN_LOCKED:
            self.state = GearState.TRANSITIONING_UP
            self.timer_s = 0.0
            return True

        return False

    def tick(self, dt_s: float) -> None:
        """
        Advances simulated time and completes transitions once duration is reached.
        """
        if self.state == GearState.TRANSITIONING_DOWN:
            self.timer_s += dt_s
            if self.timer_s >= self.deploy_time_s:
                self.state = GearState.DOWN_LOCKED

        elif self.state == GearState.TRANSITIONING_UP:
            self.timer_s += dt_s
            if self.timer_s >= self.retract_time_s:
                self.state = GearState.UP_LOCKED


class LandingGearController:
    """Controls all landing gear legs and manages their states."""
    def __init__(self):
        self.legs = [GearLeg("nose"), GearLeg("left"), GearLeg("right")]

    def log_leg(self, leg: GearLeg, msg: str) -> None:
        """Logs the state of a leg with a message."""
        print(
            f"[{leg.name.upper()}] {msg} | {leg.state.name} "
            f"(uplock={leg.uplock_sensor}, downlock={leg.downlock_sensor}, transit={leg.in_transit_sensor})"
        )

    def command_all(self, direction: str) -> None:
        """Sends command to all legs and logs the result."""
        for leg in self.legs:
            ok = leg.command(direction)
            self.log_leg(leg, f"{direction} command accepted" if ok else f"{direction} command rejected")

    def tick(self, dt_s: float) -> None:
        """Advances time for all legs and logs state changes."""
        for leg in self.legs:
            before = leg.state
            leg.tick(dt_s)
            if leg.state != before:
                self.log_leg(leg, f"Transition complete: {before.name} -> {leg.state.name}")


if __name__ == "__main__":
    lgcs = LandingGearController()

    lgcs.command_all("DOWN")
    for _ in range(6):
        lgcs.tick(0.5)
        time.sleep(0.5)

    lgcs.command_all("UP")
    for _ in range(6):
        lgcs.tick(0.5)
        time.sleep(0.5)
