import configparser
from logging import Logger


def load(path: str, logger: Logger) -> dict:
    logger.info(f"Loading config from {path}")
    try:
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(path)
    except Exception:
        logger.error("Failed to load config")
    return config
