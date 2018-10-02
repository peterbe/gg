import json

from click.testing import CliRunner

from gg.main import Config
from gg.builtins import config


def test_config(temp_configfile, mocker):
    # rget = mocker.patch('requests.get')
    getpass = mocker.patch("getpass.getpass")
    getpass.return_value = "somelongapitokenhere"

    runner = CliRunner()
    config_ = Config()
    config_.configfile = temp_configfile
    result = runner.invoke(config.config, ["-f", "myown"], obj=config_)
    assert result.exit_code == 0
    assert not result.exception

    with open(temp_configfile) as f:
        saved = json.load(f)
        assert "FORK_NAME" in saved
        assert saved["FORK_NAME"] == "myown"
