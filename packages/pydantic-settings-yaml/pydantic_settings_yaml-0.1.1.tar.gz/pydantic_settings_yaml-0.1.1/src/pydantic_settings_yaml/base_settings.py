import os
import re
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseSettings


def replace_secrets(secrets_dir: Path, data: str) -> str:
    """
    Replace "<file:xxxx>" secrets in given data
    """
    pattern = re.compile(r"\<file\:([^>]*)\>")

    for match in pattern.findall(data):
        relpath = Path(match)
        path = secrets_dir / relpath

        if not path.exists():
            raise FileNotFoundError(
                f"Secret file referenced in yaml file not found: {path}"
            )

        data = data.replace(f"<file:{match}>", path.read_text("utf-8"))
    return data


def yaml_config_settings_source(settings: "YamlBaseSettings") -> Dict[str, Any]:
    """Loads settings from a YAML file at `Config.yaml_file`

    "<file:xxxx>" patterns are replaced with the contents of file xxxx. The root path
    were to find the files is configured with `secrets_dir`.
    """
    yaml_file = getattr(settings.__config__, "yaml_file", "")
    secrets_dir = settings.__config__.secrets_dir

    assert yaml_file, "Settings.yaml_file not properly configured"
    assert secrets_dir, "Settings.secrets_dir not properly configured"

    path = Path(yaml_file)
    secrets_path = Path(secrets_dir)

    if not path.exists():
        raise FileNotFoundError(f"Could not open yaml settings file at: {path}")

    return yaml.safe_load(replace_secrets(secrets_path, path.read_text("utf-8")))


class YamlBaseSettings(BaseSettings):
    """Allows to specificy a 'yaml_file' path in the Config section.

    The secrets injection is done differently than in BaseSettings, allowing also
    partial secret replacement (such as "postgres://user:<file:path-to-password>@...").

    Field value priority:

    1. Arguments passed to the Settings class initialiser.
    2. Variables from Config.yaml_file (reading secrets at "<file:xxxx>" entries)
    3. Environment variables
    4. Variables loaded from a dotenv (.env) file (if Config.env_file is set)

    Default paths:

    - secrets_dir: "/etc/secrets" or env.SETTINGS_SECRETS_DIR
    - yaml_file: "/etc/config/config.yaml" or env.SETTINGS_YAML_FILE

    See also:

      https://pydantic-docs.helpmanual.io/usage/settings/
    """

    class Config:
        secrets_dir = os.environ.get("SETTINGS_SECRETS_DIR", "/etc/secrets")
        yaml_file = os.environ.get("SETTINGS_YAML_FILE", "/etc/config/config.yaml")

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                yaml_config_settings_source,
                env_settings,
            )


__ALL__ = (YamlBaseSettings,)
