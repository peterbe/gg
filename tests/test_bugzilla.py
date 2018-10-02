import json

from click.testing import CliRunner

from gg.main import Config
from gg.builtins import bugzilla


def test_login(temp_configfile, mocker, requestsmock):
    getpass = mocker.patch("getpass.getpass")
    getpass.return_value = "secret"

    requestsmock.get(
        "https://example.com/rest/whoami?api_key=secret",
        content=json.dumps(
            {
                "real_name": "Peter Bengtsson [:peterbe]",
                "name": "peterbe@example.com",
                "id": 1,
            }
        ).encode("utf-8"),
    )

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    config.bugzilla_url = "https://example.com"
    result = runner.invoke(bugzilla.login, [], input="myusername", obj=config)
    if result.exception:
        raise result.exception
    assert result.exit_code == 0
    assert not result.exception

    with open(temp_configfile) as f:
        saved = json.load(f)
        assert "BUGZILLA" in saved
        assert saved["BUGZILLA"]["api_key"] == "secret"
        assert saved["BUGZILLA"]["bugzilla_url"] == "https://example.com"


def test_test(temp_configfile, mocker, requestsmock):
    with open(temp_configfile, "w") as f:
        saved = {
            "BUGZILLA": {"api_key": "secret", "bugzilla_url": "https://example.com"}
        }
        json.dump(saved, f)

    requestsmock.get(
        "https://example.com/rest/whoami?api_key=secret",
        content=json.dumps(
            {"real_name": "John Doe", "name": "peterbe@example.com", "id": 1}
        ).encode("utf-8"),
    )

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    config.bugzilla_url = "https://example.com"
    result = runner.invoke(bugzilla.test, [], obj=config)
    if result.exception:
        raise result.exception
    assert result.exit_code == 0
    assert not result.exception
    assert "John Doe" in result.output


def test_logout(temp_configfile, mocker):

    with open(temp_configfile, "w") as f:
        saved = {"BUGZILLA": {"api_key": "secret"}}
        json.dump(saved, f)

    runner = CliRunner()
    config = Config()
    config.configfile = temp_configfile
    config.bugzilla_url = "https://example.com"
    result = runner.invoke(bugzilla.logout, [], obj=config)
    assert result.exit_code == 0
    assert not result.exception

    with open(temp_configfile) as f:
        saved = json.load(f)
        assert "BUGZILLA" not in saved


def test_get_summary(temp_configfile, mocker, requestsmock):

    requestsmock.get(
        "https://bugs.example.com/rest/bug/",
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
                        "id": 123456789,
                        "status": "RESOLVED",
                        "summary": "This is the summary",
                    }
                ],
                "faults": [],
            }
        ).encode("utf-8"),
    )

    config = Config()
    config.configfile = temp_configfile
    config.bugzilla_url = "https://bugs.example.com"

    summary, url = bugzilla.get_summary(config, "123456789")
    assert summary == "This is the summary"
    assert url == "https://bugs.example.com/show_bug.cgi?id=123456789"


def test_get_summary_with_token(temp_configfile, requestsmock):
    requestsmock.get(
        "https://privatebugs.example.com/rest/bug/",
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
                        "id": 123456789,
                        "status": "NEW",
                        "summary": "This is a SECRET!",
                    }
                ],
                "faults": [],
            }
        ).encode("utf-8"),
    )

    with open(temp_configfile, "w") as f:
        saved = {
            "BUGZILLA": {
                "api_key": "secret",
                "bugzilla_url": "https://privatebugs.example.com",
            }
        }
        json.dump(saved, f)
    config = Config()
    config.configfile = temp_configfile
    config.bugzilla_url = "https://bugs.example.com"

    summary, url = bugzilla.get_summary(config, "123456789")
    assert summary == "This is a SECRET!"
    assert url == "https://privatebugs.example.com/show_bug.cgi?id=123456789"
