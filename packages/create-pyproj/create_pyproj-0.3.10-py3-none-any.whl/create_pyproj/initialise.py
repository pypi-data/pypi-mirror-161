"""
Module Description.


"""
import logging
import os
from pathlib import Path

CWD = Path.cwd()
logger = logging.getLogger(__name__)


def initialise(projectname: str, no_init: bool, no_install: bool) -> None:
    PROJDIR = CWD.absolute() / projectname
    os.chdir(PROJDIR)

    # Whether to install in Pipenv
    if not no_install:
        os.system('pipenv install -d')

    # Whether to init the git repo
    if not no_init:
        git_init = ['git init', 'git add -A', 'git commit -m "first commit"']
        for cmd in git_init:
            os.system(cmd)
