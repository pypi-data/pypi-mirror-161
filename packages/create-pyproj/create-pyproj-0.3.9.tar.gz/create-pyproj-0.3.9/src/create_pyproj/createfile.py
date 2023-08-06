"""
Module Description.


"""
import logging
import shutil
from pathlib import Path

from .figlet import figletise
from .templater import writeTemplate

DIR = Path(__file__).parent.absolute()
logger = logging.getLogger(__name__)


def copyTemplates(projectname: str, cli: bool):
    """
    Copy templates into folder structure.

    Args:
        projectname (str): The project name.
        cli (bool, optional): True if this is intended as a cli application. Defaults to False.
    """
    # Set the path for the main code repo
    PROJECT_ROOT = Path.cwd() / projectname
    PROJECT_PATH = PROJECT_ROOT / 'src' / projectname.replace('-', '_')
    PROJECT_PATH.mkdir(exist_ok=True, parents=True)
    (PROJECT_ROOT / 'src' / '__init__.py').touch(exist_ok=True)
    for file in (DIR / 'code').iterdir():
        if file.stem == 'scripts':
            shutil.copytree(file, PROJECT_ROOT / file.stem)
        elif file.stem == 'test':
            shutil.copytree(file, PROJECT_ROOT / file.stem)
        elif file.stem == '_config':
            shutil.copytree(file, PROJECT_ROOT / 'src' / file.stem)
        elif file.stem == 'main.py':
            data = {'projectname': projectname, 'cli': cli}
            writeTemplate('main.py', PROJECT_ROOT / 'src', data=data, templatepath=DIR / 'code')
        else:
            if not file.is_dir():
                shutil.copy(file, PROJECT_PATH / file.name)


def createFiles(projectname: str, cli: bool, python_version: str):
    PROJECT_ROOT = Path.cwd() / projectname
    data = {
        'projectname': projectname,
        'python_version': python_version,
        'figleted': figletise(projectname),
        'cli': cli,
        'author': None,
        'author_email': None,
        'description': None,
        'hashes': '##'
    }

    standard = [
        '.env',
        '.flake8',
        '.gitignore',
        '.gitlab-ci.yml',
        '.style.yapf',
        'deploy.sh',
        'Pipfile',
        'README.md',
        'VERSION',
        'pytest.ini',
    ]

    for tmpl in standard:
        writeTemplate(tmpl, PROJECT_ROOT, data=data)

    writeTemplate('settings.json', PROJECT_ROOT / '.vscode', data=data)
    writeTemplate('extensions.json', PROJECT_ROOT / '.vscode', data=data)

    pkg_tmpl = ['LICENSE', 'setup.cfg', 'pyproject.toml', 'MANIFEST.in']
    for tmpl in pkg_tmpl:
        writeTemplate(tmpl, PROJECT_ROOT, data=data)
