import logging
from logging.config import dictConfig
from pathlib import Path

import yaml

DIR = Path(__file__).parent.absolute()
LOGPATH = DIR.parent.parent.parent / 'logs'


def removeExistingLogs():
    """
    Remove old logs, so one clean log per run.
    """
    try:
        Path(LOGPATH / 'debug.log').unlink(missing_ok=True)
        Path(LOGPATH / 'debug.log.1').unlink(missing_ok=True)
        Path(LOGPATH / 'main.log').unlink(missing_ok=True)
    except Exception as e:
        print(e)


def configureLogging(clearLogs: bool = False):
    """."""
    if clearLogs:
        removeExistingLogs()

    Path(LOGPATH).mkdir(exist_ok=True, parents=True)
    mainfilename = LOGPATH / 'main.log'
    debugfilename = LOGPATH / 'debug.log'

    with open(DIR / 'logging.yaml', 'r') as f:
        log_cfg = yaml.full_load(f)

    log_cfg['handlers']['file_handler']['filename'] = mainfilename
    log_cfg['handlers']['rotating_handler']['filename'] = debugfilename

    dictConfig(log_cfg)

    # Set ERROR level logging on verbose modules
    modules = []
    for module in modules:
        logging.getLogger(module).setLevel(logging.ERROR)
