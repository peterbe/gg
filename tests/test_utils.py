import tempfile

import click
import pytest
import git

from gg import utils


def test_get_repo(mocker):
    this_repo = utils.get_repo()
    assert isinstance(this_repo, git.Repo)


def test_get_repo_never_found(mocker):
    with pytest.raises(git.InvalidGitRepositoryError):
        utils.get_repo(tempfile.gettempdir())


def test_get_repo_name():
    this_repo_name = utils.get_repo_name()
    assert this_repo_name == "gg"


def test_error_out(capsys):
    with pytest.raises(click.Abort):
        utils.error_out("Blarg")
    out, err = capsys.readouterr()
    assert not err
    assert out == "Blarg\n"


def test_error_out_no_raise(capsys):
    utils.error_out("Blarg", False)
    out, err = capsys.readouterr()
    assert not err
    assert out == "Blarg\n"


def test_is_github():
    good_data = {"bugnumber": 123, "url": "https://github.com/peterbe/gg/issues/1"}
    assert utils.is_github(good_data)

    not_good_data = {"bugnumber": 123, "url": "https://issuetracker.example.com/1234"}
    assert not utils.is_github(not_good_data)

    not_good_data = {"bugnumber": None, "url": "https://github.com/peterbe/gg/issues/1"}
    assert not utils.is_github(not_good_data)


def test_is_bugzilla():
    good_data = {
        "bugnumber": 123,
        "url": "https://bugzilla.mozilla.org/show_bug.cgi?id=12345678",
    }
    assert utils.is_bugzilla(good_data)

    good_data = {
        "bugnumber": 123,
        "url": "https://bugzilla.redhat.com/show_bug.cgi?id=12345",
    }
    assert utils.is_bugzilla(good_data)

    not_good_data = {"bugnumber": 123, "url": "https://issuetracker.example.com/1234"}
    assert not utils.is_bugzilla(not_good_data)

    not_good_data = {
        "bugnumber": None,
        "url": "https://bugzilla.mozilla.org/show_bug.cgi?id=12345678",
    }
    assert not utils.is_bugzilla(not_good_data)
