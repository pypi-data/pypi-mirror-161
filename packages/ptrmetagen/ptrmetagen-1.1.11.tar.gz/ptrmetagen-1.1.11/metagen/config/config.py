from pydantic import BaseModel, Field, AnyUrl
import yaml
from typing import Literal, Optional
from pathlib import Path

BASE_CONFIG_FILE = Path(__file__).parent / 'config.yaml'


class RegisterConfig(BaseModel):
    registerName: Literal['pandas', 'dict']


class ImporterConfig(BaseModel):
    path: Optional[Path]
    instance_url: Optional[AnyUrl]
    host: Optional[AnyUrl]


class Config(BaseModel):
    register_setting: RegisterConfig = Field(default_factory=RegisterConfig)
    importer_setting: ImporterConfig = Field(default_factory=ImporterConfig)


def load_yaml(path: str) -> dict:
    with open(path, 'r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def dump_yaml(path: Path, data: dict) -> None:
    with open(path, 'w') as file:
        file.write(yaml.dump(data, Dumper=yaml.Dumper))


