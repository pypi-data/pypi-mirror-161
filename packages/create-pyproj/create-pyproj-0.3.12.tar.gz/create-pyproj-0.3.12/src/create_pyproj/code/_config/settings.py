# -*- coding: utf-8 -*-
"""
Module Description.


"""
from pathlib import Path

import yaml
from pydantic import BaseSettings as PyBaseSettings

DIR = Path(__file__).parent.parent
SETTINGS_PATH = Path(DIR).absolute()


def saveSettings(settings: dict,
                 settings_file_name: str = 'settings',
                 settings_path: Path = SETTINGS_PATH,
                 sort_keys: bool = False) -> None:
    settings_path.mkdir(exist_ok=True, parents=True)
    with open(settings_path / f'{settings_file_name}.yaml', 'w') as f:
        yaml.dump(settings, f, sort_keys=sort_keys)


def loadSettings(settings_file_name: str = 'settings', settings_path: Path = SETTINGS_PATH) -> dict:
    if (not (settings_path / f'{settings_file_name}.yaml').exists()):
        saveSettings({})
    with open(settings_path / f'{settings_file_name}.yaml', 'r') as f:
        settings = yaml.full_load(f)
    return settings


class BaseSettings(PyBaseSettings):
    """
    An extension of Pydantic with a custom yaml loader

    https://pydantic-docs.helpmanual.io/usage/settings/#adding-sources

    Args:
        PyBaseSettings (BaseSettings): Pydantic basesettings
    """
    class Config:
        env_file_encoding = 'utf-8'

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                env_settings,
                loadSettings,
                file_secret_settings,
            )
