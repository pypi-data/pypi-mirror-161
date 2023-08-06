import pytest
from pathlib import Path

from metagen.pipes import PathCheck


def test_path_check():
    cwd = str(Path.cwd())
    pathchek = PathCheck()
    path = pathchek(cwd)
    assert isinstance(path, Path)