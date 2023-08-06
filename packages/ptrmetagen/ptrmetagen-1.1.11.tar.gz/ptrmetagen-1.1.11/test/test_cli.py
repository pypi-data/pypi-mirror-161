import pytest
from click.testing import CliRunner
from metagen.config.cli import config

def test_register_show():
    runner = CliRunner()
    result = runner.invoke(config, input=True)
    assert result.exit_code == 0
    assert result.output == 'Hello World!\n'
