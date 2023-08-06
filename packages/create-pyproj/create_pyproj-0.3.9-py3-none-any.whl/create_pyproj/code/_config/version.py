# -*- coding: utf-8 -*-
"""
Module Description.


"""
import configparser
from pathlib import Path

DIR = Path(__file__).parent.absolute()


def getVersionFromSetup():
    """Get version from setup.cfg file."""
    config = configparser.ConfigParser()
    config.read(DIR.parent.parent / 'setup.cfg')
    return config.get('metadata', 'version')


def getVersion():
    """Get version from VERSION file."""
    with open(DIR.parent.parent / 'VERSION', 'r') as f:
        VERSION = f.read().strip()
    return VERSION
