import tempfile

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
    assert this_repo_name == 'gg'
