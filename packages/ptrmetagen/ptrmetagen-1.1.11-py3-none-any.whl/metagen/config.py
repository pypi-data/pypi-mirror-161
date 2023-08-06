from pydantic import BaseModel
import yaml
from typing import Literal
from pathlib import Path


class Config(BaseModel):
    registerName: Literal['pandas', 'dict']


def load_config(path: str) -> Config:
    with open(path, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        return Config(**data)


config = load_config(Path(__file__).parent.parent / 'config.yaml')