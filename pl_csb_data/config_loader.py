import configparser

def load() -> dict:
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read("pl-csb-data/config.ini")
    return config
