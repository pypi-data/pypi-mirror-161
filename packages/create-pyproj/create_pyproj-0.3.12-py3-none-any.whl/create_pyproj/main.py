"""
Module Description.


"""
import argparse
import logging
import textwrap

from ._config import configureLogging
from .createfile import copyTemplates, createFiles
from .figlet import figletise
from .initialise import initialise

configureLogging()
logger = logging.getLogger(__name__)


def create_pyproj(args: argparse.Namespace):
    logger.info(f'Making new project...{figletise(args.projectname)}')

    try:
        copyTemplates(args.projectname, args.cli)
        createFiles(args.projectname, args.cli, args.python_version)
        initialise(args.projectname, args.no_init, args.no_install)
        logger.info(f'Install complete!\ncd into {args.projectname} and get developing...')
    except FileExistsError:
        logger.error(
            'The destination project already exists, please remove or choose another name.')


def main():
    parser = argparse.ArgumentParser(prog='create-pyproj',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
    Create a new python skeleton project.
    --------------------------------
    The project has a number of development tools
    and convenince functions to get you started quickly!

    usage:
    create-pyproj <projectname> [options]

    The project structure will be copied to a folder ./<projectname>, the modules installed with Pipenv and a git repo initiated.

    This basic version starts with:
        - a settings manager to save, load and update using yaml.
        - a logging setup with console and file handlers.
        - a version manager, to keep the version file easily asccessible for CI/CD

    Project structure:
        - .vscode
            - settings.json
            - extensions.json
        - src
            - _config
                - logging.py
                - logging.yaml
                - settings.py
                - version.py
            - main.py
            - settings.yaml
        - .env
        - .flake8
        - .style.yapf
        - .gitignore
        - Pipfile
        - README.md
        - VERSION


        '''))
    parser.add_argument('projectname', help='The name of the project you want to start.')
    parser.add_argument('--python_version',
                        action='store',
                        type=str,
                        default="3.10",
                        choices=['3.8', '3.9', '3.10'],
                        help='Select the python version. Defaults to 3.10.')
    parser.add_argument('--cli',
                        action='store_const',
                        const=True,
                        default=False,
                        help='Select this option if this is intended to run on the command line.')
    parser.add_argument('--no-init',
                        action='store_const',
                        const=True,
                        default=False,
                        help='Select this option to not initialise a git repo.')
    parser.add_argument('--no-install',
                        action='store_const',
                        const=True,
                        default=False,
                        help='Select this option to not install the packages.')

    args = parser.parse_args()
    create_pyproj(args)


if __name__ == "__main__":
    main()
