import configparser
from pathlib import Path

import tomli

DIR = Path(__file__).parent
ROOT = DIR.parent


def pipfile_to_config():
    """
    Add dependencies from Pipfile to setup.cfg 'install_requires'.
    """
    with open(DIR.parent / "Pipfile", "rb") as f:
        pipfile = tomli.load(f)
    packages = pipfile["packages"]
    python_version = pipfile["requires"]["python_version"]

    config = configparser.ConfigParser()
    config.read(ROOT / "setup.cfg")
    config.sections()

    install_requires = set(
        x for x in config['options']["install_requires"].replace('\n', ',').split(',') if x)

    for package in packages:
        install_requires.add(package)

    newline = '\n'
    config['options']["install_requires"] = f'\n{newline.join(install_requires)}'
    config['options']['python_requires'] = f'>={python_version}'

    with open(ROOT / "setup.cfg", "w") as f:
        config.write(f)

    print("Updated setup.cfg")


if __name__ == '__main__':
    pipfile_to_config()
