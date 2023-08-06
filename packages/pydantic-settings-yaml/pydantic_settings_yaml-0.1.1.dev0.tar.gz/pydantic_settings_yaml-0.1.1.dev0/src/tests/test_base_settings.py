from pathlib import Path
from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from pydantic_settings_yaml import YamlBaseSettings
from pydantic_settings_yaml.base_settings import (
    replace_secrets,
    yaml_config_settings_source,
)


def test_replace_secrets():
    data = """
        database:
            password: <file:database_password>
            username: <file:database_username>
    """
    data = replace_secrets(Path("src/tests/data"), data)

    assert (
        data
        == """
        database:
            password: dummy_database_password
            username: dummy_database_username
    """
    )


def test_replace_two_secrets_on_one_line():
    data = """
        database_conn_str: <file:database_username>:<file:database_password>
    """
    data = replace_secrets(Path("src/tests/data"), data)

    assert (
        data
        == """
        database_conn_str: dummy_database_username:dummy_database_password
    """
    )


def test_missing_secret_file_error():
    data = """
        database_conn_str: <file:missing_secret>
    """
    with pytest.raises(FileNotFoundError):
        replace_secrets(Path("src/tests/data"), data)


@pytest.fixture()
def mocked_yamlbasesettings():
    settings = Mock()
    settings.__config__ = Mock()
    settings.__config__.yaml_file = "src/tests/data/config.yaml"
    settings.__config__.secrets_dir = "src/tests/data"
    return settings


def test_yaml_config_settings_source(mocked_yamlbasesettings):
    data = yaml_config_settings_source(mocked_yamlbasesettings)
    assert data == {
        "database": {
            "password": "dummy_database_password",
            "username": "dummy_database_username",
        }
    }


def test_yaml_config_settings_source_no_files(mocked_yamlbasesettings):
    mocked_yamlbasesettings.__config__.yaml_file = ""
    with pytest.raises(AssertionError):
        yaml_config_settings_source(mocked_yamlbasesettings)

    mocked_yamlbasesettings.__config__.yaml_file = (
        "/src/tests/data/not_existing_config.yaml"
    )
    with pytest.raises(FileNotFoundError):
        yaml_config_settings_source(mocked_yamlbasesettings)

    mocked_yamlbasesettings.__config__.yaml_file = "/src/tests/data/config.yaml"
    mocked_yamlbasesettings.__config__.secrets_dir = None
    with pytest.raises(AssertionError):
        yaml_config_settings_source(mocked_yamlbasesettings)


class Database(BaseModel):
    username: str
    password: str


class Settings(YamlBaseSettings):
    database: Database

    class Config:
        secrets_dir = "src/tests/data"
        yaml_file = "src/tests/data/config.yaml"


def test_yaml_base_settings():
    s = Settings()
    assert s.dict() == {
        "database": {
            "password": "dummy_database_password",
            "username": "dummy_database_username",
        }
    }
