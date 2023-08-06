"""Configuration for tasks3."""

import click

from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from ruamel.yaml import YAML

__package_name__ = __package__.split(".")[0]

APP_DIR: str = click.get_app_dir(__package_name__)
DEFAULT_CONFIG_FILE_PATH: Path = Path(APP_DIR) / "config.yml"
DEFAULT_DATA_FOLDER_PATH: Path = Path(APP_DIR)


class DBBackend(Enum):
    """Supported database backends"""

    sqlite = "sqlite"
    mysql = "mysql"
    postgresql = "postgresql"


class OutputFormat(Enum):
    """Supported output formats"""

    oneline = "oneline"
    short = "short"
    yaml = "yaml"
    json = "json"


@dataclass
class Config:
    db: str = str(DEFAULT_DATA_FOLDER_PATH / "tasks.db")
    backend: str = DBBackend.sqlite.value
    search_output_format: str = OutputFormat.oneline.value
    show_output_format: str = OutputFormat.short.value

    @property
    def db_backend(self) -> DBBackend:
        return DBBackend(self.backend)

    @db_backend.setter
    def db_backend(self, backend: str) -> None:
        try:
            DBBackend(backend)
        except ValueError:
            raise ValueError(f"Unsupported database backend: {backend}")
        self.backend = backend

    @property
    def db_path(self) -> Path:
        return Path(self.db)

    @db_path.setter
    def db_path(self, path: Path) -> None:
        self.db = str(path.absolute())

    @property
    def db_uri(self) -> str:
        return f"{self.db_backend.value}:///{self.db_path.absolute()}"

    @classmethod
    def from_yaml(cls, file_path: Path) -> "Config":
        config = YAML().load(file_path)
        return cls(**config)

    def to_yaml(self, file_path: Path) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        YAML().dump(asdict(self), file_path)


def load_config(config_file_path: Path = DEFAULT_CONFIG_FILE_PATH) -> Config:
    """
    Load configuration settings from a config file (yaml)

    :param config_file_path: pathlib.Path object to the config file.
    :returns: Config object
    """
    if config_file_path.exists():
        config = Config.from_yaml(config_file_path)
    else:
        config = Config()
        config.to_yaml(config_file_path)
    return config


config: Config = load_config(DEFAULT_CONFIG_FILE_PATH)
