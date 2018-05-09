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

from gg.builtins.commit.gg_commit import commit, humanize_seconds


@pytest.yield_fixture
def temp_configfile():
    tmp_dir = tempfile.mkdtemp("gg-commit")
    fp = os.path.join(tmp_dir, "state.json")
    with open(fp, "w") as f:
        json.dump({}, f)
    yield fp
    shutil.rmtree(tmp_dir)


def test_commit(temp_configfile, mocker):
    rget = mocker.patch("requests.get")

    def mocked_get(url, params, headers):
        assert url.endswith("/peterbe/gg-example/pulls")
        assert headers["Authorization"] == "token somelongapitokenhere"
        return Response([])

    rget.side_effect = mocked_get

    mocked_git = mocker.patch("git.Repo")
    mocked_git().working_dir = "gg-commit-test"
    mocked_git().active_branch.name = "my-topic-branch"
    mocked_git().index.entries.keys.return_value = [("foo.txt", 0)]

    my_remote = mocker.MagicMock()
    origin_remote = mocker.MagicMock()
    origin_remote.url = "git@github.com:peterbe/gg-example.git"
    mocked_git().remotes = {"myusername": my_remote, "origin": origin_remote}
    my_pushinfo = mocker.MagicMock()
    my_pushinfo.flags = 0
    my_remote.push.return_value = [my_pushinfo]
    # first we have to fake some previous information
    state = json.load(open(temp_configfile))
    state["gg-commit-test:my-topic-branch"] = {
        "description": "Some description", "bugnumber": None
    }
    state["FORK_NAME"] = "myusername"
    state["GITHUB"] = {
        "token": "somelongapitokenhere", "github_url": "https://example.com"
    }
    with open(temp_configfile, "w") as f:
        json.dump(state, f)

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    result = runner.invoke(commit, [], input="\n\n", obj=config)

    assert result.exit_code == 0
    assert not result.exception
    pr_url = (
        "https://github.com/peterbe/gg-example/compare/peterbe:master..."
        "myusername:my-topic-branch?expand=1"
    )
    assert pr_url in result.output


def test_commit_without_github(temp_configfile, mocker):
    mocked_git = mocker.patch("git.Repo")
    mocked_git().working_dir = "gg-commit-test"
    mocked_git().active_branch.name = "my-topic-branch"
    mocked_git().index.entries.keys.return_value = [("foo.txt", 0)]

    # first we have to fake some previous information
    state = json.load(open(temp_configfile))
    state["gg-commit-test:my-topic-branch"] = {
        "description": "Some description", "bugnumber": None
    }
    state["FORK_NAME"] = "myusername"
    with open(temp_configfile, "w") as f:
        json.dump(state, f)

    my_remote = mocker.MagicMock()
    origin_remote = mocker.MagicMock()
    origin_remote.url = "git@github.com:peterbe/gg-example.git"
    mocked_git().remotes = {"myusername": my_remote, "origin": origin_remote}
    my_pushinfo = mocker.MagicMock()
    my_pushinfo.flags = 0
    my_remote.push.return_value = [my_pushinfo]

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    result = runner.invoke(commit, [], input="\n\n", obj=config)
    assert result.exit_code == 0
    assert not result.exception


def test_commit_no_fork_name(temp_configfile, mocker):
    mocked_git = mocker.patch("git.Repo")
    mocked_git().working_dir = "gg-commit-test"
    mocked_git().active_branch.name = "my-topic-branch"
    mocked_git().index.entries.keys.return_value = [("foo.txt", 0)]

    # first we have to fake some previous information
    state = json.load(open(temp_configfile))
    state["gg-commit-test:my-topic-branch"] = {
        "description": "Some description", "bugnumber": None
    }
    with open(temp_configfile, "w") as f:
        json.dump(state, f)

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    result = runner.invoke(commit, [], input="\n", obj=config)
    assert result.exit_code == 0
    assert not result.exception
    assert "Can't help you push the commit" in result.output


def test_commit_no_files_to_add(temp_configfile, mocker):
    mocked_git = mocker.patch("git.Repo")
    mocked_git().working_dir = "gg-commit-test"
    mocked_git().active_branch.name = "my-topic-branch"
    mocked_git().index.entries.keys.return_value = []

    # first we have to fake some previous information
    # print(repr(temp_configfile))
    state = json.load(open(temp_configfile))
    state["gg-commit-test:my-topic-branch"] = {
        "description": "Some description", "bugnumber": None
    }
    with open(temp_configfile, "w") as f:
        json.dump(state, f)

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    result = runner.invoke(commit, [], input="\n", obj=config)
    assert result.exit_code > 0
    assert result.exception
    assert "No files to add" in result.output


def test_commit_without_start(temp_configfile, mocker):
    mocked_git = mocker.patch("git.Repo")
    mocked_git().working_dir = "gg-commit-test"

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    result = runner.invoke(commit, [], input='foo "bar"\n', obj=config)
    assert result.exit_code > 0
    assert result.exception
    assert "You're in a branch that was not created with gg." in result.output


def test_humanize_seconds():
    assert humanize_seconds(1) == "1 second"
    assert humanize_seconds(45) == "45 seconds"
    assert humanize_seconds(45 + 60) == "1 minute 45 seconds"
    assert humanize_seconds(45 + 60 * 2) == "2 minutes 45 seconds"
    assert humanize_seconds(60 * 60) == "1 hour"
    assert humanize_seconds(60 * 60 * 2) == "2 hours"
    assert humanize_seconds(60 * 60 * 24) == "1 day"
    assert humanize_seconds(60 * 60 * 24 * 2) == "2 days"
    assert humanize_seconds(60 * 60 * 24 * 7) == "1 week"
    assert humanize_seconds(60 * 60 * 24 * 14) == "2 weeks"
    assert humanize_seconds(60 * 60 * 24 * 28) == "1 month"
    assert humanize_seconds(60 * 60 * 24 * 28 * 2) == "2 months"
    assert humanize_seconds(60 * 60 * 24 * 28 * 12) == "1 year"
    assert humanize_seconds(60 * 60 * 24 * 28 * 12 * 2) == "2 years"
