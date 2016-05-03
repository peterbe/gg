import json

from click.testing import CliRunner

from gg.main import Config
from gg.builtins import bugzilla

from gg.testing import Response


def test_login(temp_configfile, mocker):
    rget = mocker.patch('requests.get')
    getpass = mocker.patch('getpass.getpass')
    getpass.return_value = 'secret'

    def mocked_get(url, params):
        assert url == 'https://example.com/rest/login'
        assert params['login'] == 'myusername'
        assert params['password'] == 'secret'
        return Response({
            'token': 'MYTOKEN'
        })

    rget.side_effect = mocked_get

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    config.bugzilla_url = 'https://example.com'
    result = runner.invoke(
        bugzilla.login,
        [],
        input='myusername',
        obj=config,
    )
    assert result.exit_code == 0
    assert not result.exception

    with open(temp_configfile) as f:
        saved = json.load(f)
        assert 'BUGZILLA' in saved
        assert saved['BUGZILLA']['login'] == 'myusername'
        assert saved['BUGZILLA']['token'] == 'MYTOKEN'
        assert saved['BUGZILLA']['bugzilla_url'] == 'https://example.com'


def test_test(temp_configfile, mocker):
    with open(temp_configfile, 'w') as f:
        saved = {
            'BUGZILLA': {
                'token': 'mytoken',
                'login': 'myusername',
                'bugzilla_url': 'https://example.com',
            }
        }
        json.dump(saved, f)
    rget = mocker.patch('requests.get')

    def mocked_get(url, params):
        assert url == 'https://example.com/rest/whoami'
        assert params['token'] == 'mytoken'
        return Response({
            'id': 123456,
            'real_name': 'John Doe',
            'name': 'peterbe@example.com'
        })

    rget.side_effect = mocked_get

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    config.bugzilla_url = 'https://example.com'
    result = runner.invoke(
        bugzilla.test,
        [],
        obj=config,
    )
    assert result.exit_code == 0
    assert not result.exception
    assert 'John Doe' in result.output


def test_logout(temp_configfile, mocker):

    with open(temp_configfile, 'w') as f:
        saved = {
            'BUGZILLA': {
                'token': 'mytoken',
            }
        }
        json.dump(saved, f)

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    config.bugzilla_url = 'https://example.com'
    result = runner.invoke(
        bugzilla.logout,
        [],
        obj=config,
    )
    assert result.exit_code == 0
    assert not result.exception

    with open(temp_configfile) as f:
        saved = json.load(f)
        assert 'BUGZILLA' not in saved
