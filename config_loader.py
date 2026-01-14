import json
from dataclasses import dataclass
from typing import List, Optional

def log(msg: str) -> None:
    print(f"[CONFIG] {msg}")

@dataclass(frozen=True)
class TimingsConfig:
    deploy_time_s: float = 2.5
    retract_time_s: float = 2.5

@dataclass(frozen=True)
class InterlocksConfig:
    allow_down_from: Optional[List[str]] = None
    allow_up_from: Optional[List[str]] = None

@dataclass(frozen=True)
class LoggingConfig:
    level: str = "INFO"

@dataclass(frozen=True)
class Config:
    timings: TimingsConfig = TimingsConfig()
    interlocks: InterlocksConfig = InterlocksConfig(["UP_LOCKED"], ["DOWN_LOCKED"])
    logging: LoggingConfig = LoggingConfig()

def load_config(path: str = "configs/config.json") -> Config:
    log(f"Loading configuration from {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    timings_raw = raw.get("timings", {})
    interlocks_raw = raw.get("interlocks", {})
    logging_raw = raw.get("logging", {})

    # verify and set timings
    try:
        deploy_time = float(timings_raw.get("deploy_time_s", 2.5))
    except (TypeError, ValueError):
        log("Invalid deploy_time_s, falling back to 2.5s")
        deploy_time = 2.5

    try:
        retract_time = float(timings_raw.get("retract_time_s", 2.5))
    except (TypeError, ValueError):
        log("Invalid retract_time_s, falling back to 2.5s")
        retract_time = 2.5

    log(f"Deploy time set to {deploy_time}s")
    log(f"Retract time set to {retract_time}s")

    # verify and set interlocks
    allow_down_from = interlocks_raw.get("allow_down_from", ["UP_LOCKED"])
    allow_up_from = interlocks_raw.get("allow_up_from", ["DOWN_LOCKED"])

    if not isinstance(allow_down_from, list):
        log("allow_down_from invalid, using default ['UP_LOCKED']")
        allow_down_from = ["UP_LOCKED"]

    if not isinstance(allow_up_from, list):
        log("allow_up_from invalid, using default ['DOWN_LOCKED']")
        allow_up_from = ["DOWN_LOCKED"]

    log_level = logging_raw.get("level", "INFO")

    log(f"Logging level set to {log_level}")

    return Config(
        timings=TimingsConfig(deploy_time_s=deploy_time, retract_time_s=retract_time),
        interlocks=InterlocksConfig(allow_down_from, allow_up_from),
        logging=LoggingConfig(log_level),
    )

