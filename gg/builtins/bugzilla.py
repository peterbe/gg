import json
import getpass
import urllib.parse

import click
import requests

from gg.utils import error_out, success_out, info_out
from gg.state import read, update, remove
from gg.main import cli, pass_config

BUGZILLA_URL = 'https://bugzilla.mozilla.org'


@cli.group()
@click.option(
    '-u', '--bugzilla-url',
    default=BUGZILLA_URL,
    help='URL to Bugzilla instance (default: {})'.format(
        BUGZILLA_URL
    )
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
@pass_config
def login(config):
    """Go fetch a Bugzilla cookie"""
    state = read(config.configfile)
    default = getpass.getuser()
    if state.get('BUGZILLA'):
        if state['BUGZILLA'].get('login'):
            default = state['BUGZILLA']['login']

    login = input(
        'Username/Email [{}]: '.format(default)
    ).strip() or default
    password = getpass.getpass(
        'Password (Will never be stored!): '
    )
    if not password:
        error_out('No password :(')

    url = urllib.parse.urljoin(config.bugzilla_url, '/rest/login')
    assert url.startswith('https://'), url
    response = requests.get(url, params={
        'login': login,
        'password': password,
    })

    if response.status_code == 200:
        token = response.json()['token']
        update(config.configfile, {
            'BUGZILLA': {
                'bugzilla_url': config.bugzilla_url,
                'login': login,
                'token': token,
            }
        })
        success_out('Yay! It worked!')
    else:
        error_out('Failed - {} ({})'.format(
            response.status_code,
            response.json()
        ))


@bugzilla.command()
@pass_config
def logout(config):
    """Remove and forget your Bugzilla credentials"""
    state = read(config.configfile)
    if state.get('BUGZILLA'):
        remove(config.configfile, 'BUGZILLA')
        success_out('Forgotten')
    else:
        error_out('No stored Bugzilla credentials')


def get_summary(config, bugnumber):
    params = {
        'ids': bugnumber,
        'include_fields': 'summary'
    }
    base_url = config.bugzilla_url
    state = read(config.configfile)

    credentials = state.get('BUGZILLA')
    if credentials:
        # cool! let's use that
        base_url = credentials['bugzilla_url']
        params['token'] = credentials['token']

    url = urllib.parse.urljoin(
        base_url,
        '/rest/bug/'
    )
    assert url.startswith('https://'), url
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        bug = data['bugs'][0]

        bug_url = urllib.parse.urljoin(
            base_url,
            '/show_bug.cgi?id={}'.format(bug['id'])
        )
        return bug['summary'], bug_url
    return None, None


@bugzilla.command()
@click.option(
    '-b', '--bugnumber',
    type=int,
    help='Optionally test fetching a specific bug'
)
@pass_config
def test(config, bugnumber):
    """Test your saved Bugzilla credentials."""
    state = read(config.configfile)
    credentials = state.get('BUGZILLA')
    if not credentials:
        error_out('No credentials saved. Run: gg bugzilla login')
    if config.verbose:
        info_out('Using: {}'.format(credentials['bugzilla_url']))

    if bugnumber:
        summary, _ = get_summary(config, bugnumber)
        if summary:
            info_out('It worked!')
            success_out(summary)
        else:
            error_out('Unable to fetch')
    else:
        url = urllib.parse.urljoin(
            credentials['bugzilla_url'],
            '/rest/whoami'
        )
        assert url.startswith('https://'), url
        response = requests.get(url, params={
            'token': credentials['token'],
        })
        if response.status_code == 200:
            success_out(json.dumps(response.json(), indent=2))
        else:
            error_out('Failed to query - {} ({})'.format(
                response.status_code,
                response.json()
            ))
