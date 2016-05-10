import json

from click.testing import CliRunner

from gg.main import Config
from gg.builtins import github

from gg.testing import Response


def test_token(temp_configfile, mocker):
    rget = mocker.patch('requests.get')
    getpass = mocker.patch('getpass.getpass')
    getpass.return_value = 'somelongapitokenhere'

    def mocked_get(url, headers):
        assert url == 'https://example.com/user'
        assert headers['Authorization'] == 'token somelongapitokenhere'
        return Response({
            'name': 'Peter',
            'login': 'peterbe',
        })

    rget.side_effect = mocked_get

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    config.github_url = 'https://example.com'
    result = runner.invoke(
        github.token,
        [],
        obj=config,
    )
    assert result.exit_code == 0
    assert not result.exception

    with open(temp_configfile) as f:
        saved = json.load(f)
        assert 'GITHUB' in saved
        assert saved['GITHUB']['login'] == 'peterbe'
        assert saved['GITHUB']['token'] == 'somelongapitokenhere'
        assert saved['GITHUB']['github_url'] == 'https://example.com'


def test_token_argument(temp_configfile, mocker):
    rget = mocker.patch('requests.get')

    def mocked_get(url, headers):
        assert url == 'https://example.com/user'
        assert headers['Authorization'] == 'token somelongapitokenhere'
        return Response({
            'name': 'Peter',
            'login': 'peterbe',
        })

    rget.side_effect = mocked_get

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    config.github_url = 'https://example.com'
    result = runner.invoke(
        github.token,
        ['somelongapitokenhere'],
        obj=config,
    )
    assert result.exit_code == 0
    assert not result.exception

    with open(temp_configfile) as f:
        saved = json.load(f)
        assert 'GITHUB' in saved
        assert saved['GITHUB']['login'] == 'peterbe'
        assert saved['GITHUB']['token'] == 'somelongapitokenhere'
        assert saved['GITHUB']['github_url'] == 'https://example.com'


def test_test(temp_configfile, mocker):
    with open(temp_configfile, 'w') as f:
        saved = {
            'GITHUB': {
                'token': 'somelongapitokenhere',
                'login': 'peterbe',
                'github_url': 'https://example.com',
            }
        }
        json.dump(saved, f)
    rget = mocker.patch('requests.get')

    def mocked_get(url, headers):
        assert url == 'https://example.com/user'
        assert headers['Authorization'] == 'token somelongapitokenhere'
        return Response({
            'id': 123456,
            'name': 'Peter Bengtsson',
            'login': 'peterbe'
        })

    rget.side_effect = mocked_get

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    config.github_url = 'https://example.com'
    result = runner.invoke(
        github.test,
        [],
        obj=config,
    )
    assert result.exit_code == 0
    assert not result.exception
    assert 'Peter Bengtsson' in result.output


def test_test_issue_url(temp_configfile, mocker):
    with open(temp_configfile, 'w') as f:
        saved = {
            'GITHUB': {
                'token': 'somelongapitokenhere',
                'login': 'peterbe',
                'github_url': 'https://example.com',
            }
        }
        json.dump(saved, f)
    rget = mocker.patch('requests.get')

    def mocked_get(url, headers):
        assert url == 'https://example.com/repos/peterbe/gg/issues/123'
        assert headers['Authorization'] == 'token somelongapitokenhere'
        return Response({
            'id': 123456,
            'title': 'Issue Title Here',
            'html_url': 'https://api.github.com/repos/peterbe/gg/issues/123',
        })

    rget.side_effect = mocked_get

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    config.github_url = 'https://example.com'
    result = runner.invoke(
        github.test,
        ['-i', 'https://github.com/peterbe/gg/issues/123'],
        obj=config,
    )
    assert result.exit_code == 0
    assert not result.exception
    assert 'Issue Title Here' in result.output


def test_burn(temp_configfile, mocker):

    with open(temp_configfile, 'w') as f:
        saved = {
            'GITHUB': {
                'token': 'somelongapitokenhere',
                'login': 'peterbe',
            }
        }
        json.dump(saved, f)

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    config.github_url = 'https://example.com'
    result = runner.invoke(
        github.burn,
        [],
        obj=config,
    )
    assert result.exit_code == 0
    assert not result.exception

    with open(temp_configfile) as f:
        saved = json.load(f)
        assert 'GITHUB' not in saved


def test_get_title(temp_configfile, mocker):
    rget = mocker.patch('requests.get')

    def mocked_get(url, headers):
        assert url == 'https://api.github.com/repos/peterbe/gg/issues/1'
        # assert 'token' not in params
        return Response({
            'html_url': 'https://github.com/peterbe/gg/issues/1',
            'id': 85565047,
            'number': 1,
            'title': 'This is the title',
        })

    rget.side_effect = mocked_get

    config = Config()
    config.configfile = temp_configfile
    # config.bugzilla_url = 'https://bugs.example.com'

    title, url = github.get_title(
        config, 'peterbe', 'gg', 1
    )
    assert title == 'This is the title'
    assert url == 'https://github.com/peterbe/gg/issues/1'
