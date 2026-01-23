from enum import Enum, auto
from dataclasses import dataclass
from config_loader import load_config, Config
import time
import logging

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
    deploy_time_s: float
    retract_time_s: float
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

    def command(self, direction: str, allow_from: list[str]) -> bool:
        """
        direction: "DOWN" or "UP"
        Starts a transition if allowed, does NOT complete it instantly.
        """
        if self.state.name not in allow_from:
            return False

        if direction == "DOWN":
            self.state = GearState.TRANSITIONING_DOWN
            self.timer_s = 0.0
            return True

        if direction == "UP":
            self.state = GearState.TRANSITIONING_UP
            self.timer_s = 0.0
            return True

        return False

    def tick(self, dt_s: float) -> None:
        if self.state == GearState.TRANSITIONING_DOWN:
            self.timer_s += dt_s
            if self.timer_s >= self.deploy_time_s:
                self.state = GearState.DOWN_LOCKED

        elif self.state == GearState.TRANSITIONING_UP:
            self.timer_s += dt_s
            if self.timer_s >= self.retract_time_s:
                self.state = GearState.UP_LOCKED


class LandingGearController:
    def __init__(self, config: Config):
        self.config = config
        t = config.timings
        self.legs = [
            GearLeg("nose", t.deploy_time_s, t.retract_time_s),
            GearLeg("left", t.deploy_time_s, t.retract_time_s),
            GearLeg("right", t.deploy_time_s, t.retract_time_s),
        ]

    def log_leg(self, leg: GearLeg, msg: str) -> None:
        """Logs the state of a leg with a message."""
        logger = logging.getLogger(__name__)
        logger.info(
            f"[{leg.name.upper()}] {msg} | {leg.state.name} "
            f"(uplock={leg.uplock_sensor}, downlock={leg.downlock_sensor}, transit={leg.in_transit_sensor})"
        )

    def command_all(self, direction: str) -> None:
        interlocks = self.config.interlocks
        allow_from = interlocks.allow_down_from if direction == "DOWN" else interlocks.allow_up_from
        allow_from = allow_from or []

        for leg in self.legs:
            ok = leg.command(direction, allow_from)
            self.log_leg(leg, f"{direction} command accepted" if ok else f"{direction} command rejected")

    def tick(self, dt_s: float) -> None:
        """Advances time for all legs and logs state changes."""
        for leg in self.legs:
            before = leg.state
            leg.tick(dt_s)
            if leg.state != before:
                self.log_leg(leg, f"Transition complete: {before.name} -> {leg.state.name}")


def print_status(lgcs):
    """Prints a neat status line for all legs."""
    status_strs = []
    for leg in lgcs.legs:
        # Simple state indicators
        state_sym = " [ ]"  # Default
        if leg.state == GearState.DOWN_LOCKED:
            state_sym = " [G]"  # Green/Down
        elif leg.state == GearState.UP_LOCKED:
            state_sym = " [ ]"  # Up
        else:
            state_sym = " [!]"  # Transit/Red

        status_strs.append(f"{leg.name.upper()}:{state_sym} {leg.state.name}")
    print(" | ".join(status_strs))


def run_cockpit():
    """Interactive CLI for landing gear control."""
    config = load_config("configs/config.json")
    lgcs = LandingGearController(config)

    print("\n--- LANDING GEAR COCKPIT ---")
    print("Commands: [d]own, [u]p, [q]uit")
    print("Press [Enter] to advance time (0.5s step)\n")

    while True:
        print_status(lgcs)

        try:
            cmd = input("CMD > ").strip().lower()
        except KeyboardInterrupt:
            break

        if cmd == "q":
            print("Exiting cockpit.")
            break
        elif cmd == "d":
            print(">> COMMAND: GEAR DOWN")
            lgcs.command_all("DOWN")
        elif cmd == "u":
            print(">> COMMAND: GEAR UP")
            lgcs.command_all("UP")

        # Advance simulation time
        lgcs.tick(0.5)


if __name__ == "__main__":
    config = load_config("configs/config.json")

    # Configure logging to write to file
    logging.basicConfig(
        level=getattr(logging, config.logging.level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='landing_gear.log',
        filemode='a'
    )

    run_cockpit()