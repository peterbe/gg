import json
import getpass
import urllib.parse

import click
import requests

from gg.utils import error_out, success_out, info_out
from gg.state import read, update, remove
from gg.main import cli, pass_config

BUGZILLA_URL = "https://bugzilla.mozilla.org"


@cli.group()
@click.option(
    "-u",
    "--bugzilla-url",
    default=BUGZILLA_URL,
    help=f"URL to Bugzilla instance (default: {BUGZILLA_URL})",
)
@pass_config
def bugzilla(config, bugzilla_url):
    """General tool for connecting to Bugzilla. The default URL
    is that for bugzilla.mozilla.org but you can override that.
    Once you're signed in you can use those credentials to automatically
    fetch bug summaries even of private bugs.
    """
    config.bugzilla_url = bugzilla_url


@bugzilla.command()
@click.argument("api_key", default="")
@pass_config
def login(config, api_key=""):
    """Store your Bugzilla API Key"""
    if not api_key:
        info_out(
            "If you don't have an API Key, go to:\n"
            "https://bugzilla.mozilla.org/userprefs.cgi?tab=apikey\n"
        )
        api_key = getpass.getpass("API Key: ")

    # Before we store it, let's test it.
    url = urllib.parse.urljoin(config.bugzilla_url, "/rest/whoami")
    assert url.startswith("https://"), url
    response = requests.get(url, params={"api_key": api_key})
    if response.status_code == 200:
        if response.json().get("error"):
            error_out(f"Failed - {response.json()}")
        else:
            update(
                config.configfile,
                {
                    "BUGZILLA": {
                        "bugzilla_url": config.bugzilla_url,
                        "api_key": api_key,
                        # "login": login,
                    }
                },
            )
            success_out("Yay! It worked!")
    else:
        error_out(f"Failed - {response.status_code} ({response.json()})")


@bugzilla.command()
@pass_config
def logout(config):
    """Remove and forget your Bugzilla credentials"""
    state = read(config.configfile)
    if state.get("BUGZILLA"):
        remove(config.configfile, "BUGZILLA")
        success_out("Forgotten")
    else:
        error_out("No stored Bugzilla credentials")


def get_summary(config, bugnumber):
    params = {"ids": bugnumber, "include_fields": "summary,id"}
    # If this function is called from a plugin, we don't have
    # config.bugzilla_url this time.
    base_url = getattr(config, "bugzilla_url", BUGZILLA_URL)
    state = read(config.configfile)

    credentials = state.get("BUGZILLA")
    if credentials:
        # cool! let's use that
        base_url = credentials["bugzilla_url"]
        params["api_key"] = credentials["api_key"]

    url = urllib.parse.urljoin(base_url, "/rest/bug/")
    assert url.startswith("https://"), url
    response = requests.get(url, params=params)
    response.raise_for_status()
    if response.status_code == 200:
        data = response.json()
        bug = data["bugs"][0]

        bug_url = urllib.parse.urljoin(base_url, f"/show_bug.cgi?id={bug['id']}")
        return bug["summary"], bug_url
    return None, None


@bugzilla.command()
@click.option(
    "-b", "--bugnumber", type=int, help="Optionally test fetching a specific bug"
)
@pass_config
def test(config, bugnumber):
    """Test your saved Bugzilla API Key."""
    state = read(config.configfile)
    credentials = state.get("BUGZILLA")
    if not credentials:
        error_out("No API Key saved. Run: gg bugzilla login")
    if config.verbose:
        info_out(f"Using: {credentials['bugzilla_url']}")

    if bugnumber:
        summary, _ = get_summary(config, bugnumber)
        if summary:
            info_out("It worked!")
            success_out(summary)
        else:
            error_out("Unable to fetch")
    else:
        url = urllib.parse.urljoin(credentials["bugzilla_url"], "/rest/whoami")
        assert url.startswith("https://"), url

        response = requests.get(url, params={"api_key": credentials["api_key"]})
        if response.status_code == 200:
            if response.json().get("error"):
                error_out(f"Failed! - {response.json()}")
            else:
                success_out(json.dumps(response.json(), indent=2))
        else:
            error_out(f"Failed to query - {response.status_code} ({response.json()})")
