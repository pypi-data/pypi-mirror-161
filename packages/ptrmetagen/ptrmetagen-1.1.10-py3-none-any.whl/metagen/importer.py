from pydantic import BaseModel, validator, AnyUrl
from pathlib import Path
import subprocess
from requests import post
from abc import ABC, abstractmethod

from metagen.pipes import path_check


class ImportError(Exception):
    pass


class ImporterABC(BaseModel, ABC):

    @abstractmethod
    def run(self, fixtutres: dict) -> dict:
        pass


class Importer(ImporterABC):
    path: Path
    instance_url: AnyUrl
    host: AnyUrl

    @validator('path', pre=True)
    def set_pat(cls, value):
        return path_check(value)

    def run(self, fixtutres: dict) -> dict:
        self.server_start()
        report = self.import_fixtures(fixtutres)
        self.server_stop()
        return report

    def server_start(self):
        """Start importer node server"""
        subprocess.run(f'node {self.path / "server"} start')

    def server_stop(self):
        """Start importer node server"""
        subprocess.run(f'node {self.path / "server"} stop')

    def import_fixtures(self, fixtures: dict):
        response = post(url=f'{self.host}/metadata', data=fixtures)
        if response.status_code == 200:
            return response.json()
        else:
            raise ImportError(f'Import of fixtures failed '
                              f'\n status: {response.status_code} '
                              f'\n message: {response.content}')

