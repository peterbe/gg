import json
import os
import tempfile
import shutil

from git.remote import PushInfo
import pytest
import requests_mock
from click.testing import CliRunner

# By doing this import we make sure that the plugin is made available
# but the entry points loading inside gg.main.
# An alternative would we to set `PYTHONPATH=. py.test` (or something)
# but then that wouldn't test the entry point loading.
from gg.main import Config

from gg.builtins.push.gg_push import push


@pytest.fixture(autouse=True)
def requestsmock():
    """Return a context where requests are all mocked.
    Usage::

        def test_something(requestsmock):
            requestsmock.get(
                'https://example.com/path'
                content=b'The content'
            )
            # Do stuff that involves requests.get('http://example.com/path')
    """
    with requests_mock.mock() as m:
        yield m


@pytest.yield_fixture
def temp_configfile():
    tmp_dir = tempfile.mkdtemp("gg-start")
    fp = os.path.join(tmp_dir, "state.json")
    with open(fp, "w") as f:
        json.dump({}, f)
    yield fp
    shutil.rmtree(tmp_dir)


def test_push(temp_configfile, mocker):
    mocked_git = mocker.patch("git.Repo")
    mocked_git().working_dir = "gg-start-test"
    mocked_git().remotes.__getitem__().push.return_value = [
        PushInfo(0, "All is well", None, None, "origin")
    ]

    state = json.load(open(temp_configfile))
    state["FORK_NAME"] = "peterbe"
    with open(temp_configfile, "w") as f:
        json.dump(state, f)

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    result = runner.invoke(push, [], obj=config)
    if result.exception:
        raise result.exception
    assert result.exit_code == 0
    assert not result.exception

    mocked_git().remotes.__getitem__().push.assert_called_with()
