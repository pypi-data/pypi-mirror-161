import configparser
from pathlib import Path

CFGPATH = Path(__file__).parent.parent.parent


def getVersionFromSetup():
    config = configparser.ConfigParser()
    config.read(CFGPATH / 'setup.cfg')
    return config.get('metadata', 'version')
