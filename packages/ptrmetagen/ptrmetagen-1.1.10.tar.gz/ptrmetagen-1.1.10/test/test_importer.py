from pathlib import Path
import pytest
from pydantic import AnyUrl

from metagen.main import CONFIG
from metagen.importer import Importer


def test_importer_init():
    try:
        importer = Importer(**CONFIG.importer_setting.dict())
    except Exception as e:
        assert False

    assert isinstance(importer.path, Path)
    assert isinstance(importer.instance_url, AnyUrl)