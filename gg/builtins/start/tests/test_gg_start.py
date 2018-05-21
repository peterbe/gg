import json
import os
import tempfile
import shutil

import git
import pytest
import requests_mock
from click.testing import CliRunner

# By doing this import we make sure that the plugin is made available
# but the entry points loading inside gg.main.
# An alternative would we to set `PYTHONPATH=. py.test` (or something)
# but then that wouldn't test the entry point loading.
from gg.main import Config

from gg.builtins.start.gg_start import start, parse_remote_url


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


def test_start(temp_configfile, mocker):
    mocked_git = mocker.patch("git.Repo")
    mocked_git().working_dir = "gg-start-test"

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    result = runner.invoke(start, [""], input='foo "bar"\n', obj=config)
    assert result.exit_code == 0
    assert not result.exception

    mocked_git().create_head.assert_called_with("foo-bar")
    mocked_git().create_head().checkout.assert_called_with()

    with open(temp_configfile) as f:
        saved = json.load(f)

        assert "gg-start-test:foo-bar" in saved
        assert saved["gg-start-test:foo-bar"]["description"] == 'foo "bar"'
        assert saved["gg-start-test:foo-bar"]["date"]


def test_start_weird_description(temp_configfile, mocker):
    mocked_git = mocker.patch("git.Repo")
    mocked_git().working_dir = "gg-start-test"

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    summary = "  a!@#$%^&*()_+{}[/]-= ;:   --> ==>  ---  `foo`   ,. <bar>     "
    result = runner.invoke(start, [""], input=summary + "\n", obj=config)
    assert result.exit_code == 0
    assert not result.exception

    expected_branchname = "a_+-foo-bar"
    mocked_git().create_head.assert_called_with(expected_branchname)
    mocked_git().create_head().checkout.assert_called_with()

    with open(temp_configfile) as f:
        saved = json.load(f)

        key = "gg-start-test:" + expected_branchname
        assert key in saved
        assert saved[key]["description"] == summary.strip()


def test_start_not_a_git_repo(temp_configfile, mocker):
    mocked_git = mocker.patch("git.Repo")

    mocked_git.side_effect = git.InvalidGitRepositoryError("/some/place")

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    result = runner.invoke(start, [""], obj=config)
    assert result.exit_code == 1
    assert '"/some/place" is not a git repository' in result.output
    assert "Aborted!" in result.output
    assert result.exception


def test_start_a_digit(temp_configfile, mocker, requestsmock):
    mocked_git = mocker.patch("git.Repo")
    mocked_git().working_dir = "gg-start-test"

    remotes = []

    class Remote:

        def __init__(self, name, url):
            self.name = name
            self.url = url

    remotes.append(Remote("origin", "git@github.com:myorg/myrepo.git"))
    remotes.append(Remote("other", "https://github.com/o/ther.git"))
    mocked_git().remotes.__iter__.return_value = remotes

    # rget = mocker.patch("requests.get")
    requestsmock.get(
        "https://bugzilla.mozilla.org/rest/bug/",
        content=json.dumps(
            {
                "bugs": [
                    {
                        "assigned_to": "nobody@mozilla.org",
                        "assigned_to_detail": {
                            "email": "nobody@mozilla.org",
                            "id": 1,
                            "name": "nobody@mozilla.org",
                            "real_name": "Nobody; OK to take it and work on it",
                        },
                        "id": 1234,
                        "status": "NEW",
                        "summary": "This is the summary",
                    }
                ],
                "faults": [],
            }
        ).encode("utf-8"),
    )
    requestsmock.get(
        "https://api.github.com/repos/myorg/myrepo/issues/1234",
        content=json.dumps(
            {
                "id": 1234,
                "title": "Issue Title Here",
                "html_url": ("https://api.github.com/repos/myorg/myrepo/issues/123"),
            }
        ).encode("utf-8"),
    )
    requestsmock.get(
        "https://api.github.com/repos/o/ther/issues/1234",
        status_code=404,
        content=json.dumps({"not": "found"}).encode("utf-8"),
    )

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    result = runner.invoke(start, ["1234"], obj=config)
    assert "Input is ambiguous" in result.output
    assert "Issue Title Here" in result.output
    assert "This is the summary" in result.output
    assert result.exit_code == 1


def test_start_github_issue(temp_configfile, mocker, requestsmock):

    requestsmock.get(
        "https://api.github.com/repos/peterbe/gg-start/issues/7",
        content=json.dumps(
            {
                "title": "prefix branch name differently for github issues",
                "html_url": "https://github.com/peterbe/gg-start/issues/7",
            }
        ).encode("utf-8"),
    )
    mocked_git = mocker.patch("git.Repo")
    mocked_git().working_dir = "gg-start-test"

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    result = runner.invoke(
        start,
        ["https://github.com/peterbe/gg-start/issues/7"],
        input='foo "bar"\n',
        obj=config,
    )
    if result.exception:
        raise result.exception
    assert result.exit_code == 0
    assert not result.exception

    mocked_git().create_head.assert_called_with("issue-7-foo-bar")
    mocked_git().create_head().checkout.assert_called_with()

    with open(temp_configfile) as f:
        saved = json.load(f)

        key = "gg-start-test:issue-7-foo-bar"
        assert key in saved
        assert saved[key]["description"] == 'foo "bar"'
        assert saved[key]["date"]


def test_start_bugzilla_url(temp_configfile, mocker, requestsmock):
    requestsmock.get(
        "https://bugzilla.mozilla.org/rest/bug/?ids=123456&include_fields=summary%2Cid",
        content=json.dumps(
            {
                "bugs": [
                    {
                        "assigned_to": "nobody@mozilla.org",
                        "id": 1234,
                        "status": "NEW",
                        "summary": "This is the summary",
                    }
                ],
                "faults": [],
            }
        ).encode("utf-8"),
    )
    mocked_git = mocker.patch("git.Repo")
    mocked_git().working_dir = "gg-start-test"

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    result = runner.invoke(
        start,
        ["https://bugzilla.mozilla.org/show_bug.cgi?id=123456"],
        input='foo "bar"\n',
        obj=config,
    )
    if result.exception:
        raise result.exception
    assert result.exit_code == 0
    assert not result.exception

    mocked_git().create_head.assert_called_with("bug-123456-foo-bar")
    mocked_git().create_head().checkout.assert_called_with()

    with open(temp_configfile) as f:
        saved = json.load(f)

        key = "gg-start-test:bug-123456-foo-bar"
        assert key in saved
        assert saved[key]["description"] == 'foo "bar"'
        assert saved[key]["date"]


def test_parse_remote_url():
    org, repo = parse_remote_url("git@github.com:org/repo.git")
    assert org == "org"
    assert repo == "repo"
    org, repo = parse_remote_url("https://github.com/org/repo.git")
    assert org == "org"
    assert repo == "repo"
