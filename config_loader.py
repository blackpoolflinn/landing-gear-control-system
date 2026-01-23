import json
import logging
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)

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
    logger.info(f"Loading configuration from {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    timings_raw = raw.get("timings", {})
    interlocks_raw = raw.get("interlocks", {})
    logging_raw = raw.get("logging", {})

    # verify and set timings
    try:
        deploy_time = float(timings_raw.get("deploy_time_s", 2.5))
    except (TypeError, ValueError):
        logger.warning("Invalid deploy_time_s, falling back to 2.5s")
        deploy_time = 2.5

    try:
        retract_time = float(timings_raw.get("retract_time_s", 2.5))
    except (TypeError, ValueError):
        logger.warning("Invalid retract_time_s, falling back to 2.5s")
        retract_time = 2.5

    logger.info(f"Deploy time set to {deploy_time}s")
    logger.info(f"Retract time set to {retract_time}s")

    # verify and set interlocks
    allow_down_from = interlocks_raw.get("allow_down_from", ["UP_LOCKED"])
    allow_up_from = interlocks_raw.get("allow_up_from", ["DOWN_LOCKED"])

    if not isinstance(allow_down_from, list):
        logger.warning("allow_down_from invalid, using default ['UP_LOCKED']")
        allow_down_from = ["UP_LOCKED"]

    if not isinstance(allow_up_from, list):
        logger.warning("allow_up_from invalid, using default ['DOWN_LOCKED']")
        allow_up_from = ["DOWN_LOCKED"]

    log_level = logging_raw.get("level", "INFO")

    logger.info(f"Logging level set to {log_level}")

    return Config(
        timings=TimingsConfig(deploy_time_s=deploy_time, retract_time_s=retract_time),
        interlocks=InterlocksConfig(allow_down_from, allow_up_from),
        logging=LoggingConfig(log_level),
    )

