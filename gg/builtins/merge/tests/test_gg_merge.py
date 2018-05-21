import json
import os
import tempfile
import shutil

import pytest
from click.testing import CliRunner

# By doing this import we make sure that the plugin is made available
# but the entry points loading inside gg.main.
# An alternative would we to set `PYTHONPATH=. py.test` (or something)
# but then that wouldn't test the entry point loading.
from gg.main import Config
from gg.testing import Response

from gg.builtins.merge.gg_merge import merge


@pytest.yield_fixture
def temp_configfile():
    tmp_dir = tempfile.mkdtemp("gg-merge")
    fp = os.path.join(tmp_dir, "state.json")
    with open(fp, "w") as f:
        json.dump({}, f)
    yield fp
    shutil.rmtree(tmp_dir)


class MockDiff:

    def __init__(self, path, deleted_file=False):
        self.b_path = path
        self.deleted_file = deleted_file


def test_merge(temp_configfile, mocker):
    rget = mocker.patch("requests.get")

    def mocked_get(url, params, headers):
        assert url.endswith("/peterbe/gg-example/pulls")
        assert headers["Authorization"] == "token somelongapitokenhere"
        return Response([])

    rget.side_effect = mocked_get

    mocked_git = mocker.patch("git.Repo")
    mocked_git().working_dir = "gg-commit-test"
    branch1 = mocker.MagicMock()
    branch1.name = "this-branch"

    mocked_git().active_branch.name = branch1.name

    mocked_remote = mocker.MagicMock()
    mocked_remote.name = "origin"
    mocked_git().remotes.__iter__.return_value = [mocked_remote]
    mocked_git().is_dirty.return_value = False

    mocked_git().heads.__iter__.return_value = [branch1]

    my_remote = mocker.MagicMock()
    origin_remote = mocker.MagicMock()
    origin_remote.url = "git@github.com:peterbe/gg-example.git"
    my_pushinfo = mocker.MagicMock()
    my_pushinfo.flags = 0
    my_remote.push.return_value = [my_pushinfo]
    # first we have to fake some previous information
    state = json.load(open(temp_configfile))
    state["gg-commit-test:my-topic-branch"] = {
        "description": "Some description",
        "bugnumber": None,
    }
    # state["FORK_NAME"] = "myusername"
    state["GITHUB"] = {
        "token": "somelongapitokenhere",
        "github_url": "https://example.com",
    }
    with open(temp_configfile, "w") as f:
        json.dump(state, f)

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    result = runner.invoke(merge, [], input="\n\n", obj=config)
    if result.exception:
        # print(mocked_git.mock_calls)
        # print(result.output)
        # print(result.exception)
        raise result.exception
    assert result.exit_code == 0

    mocked_git().git.merge.assert_called_with("this-branch")
    mocked_git().git.branch.assert_called_with("-d", "this-branch")
