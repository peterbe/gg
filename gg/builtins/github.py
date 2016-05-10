import re
import json
import getpass
import urllib.parse

import click
import requests

from gg.utils import error_out, success_out, info_out
from gg.state import read, update, remove
from gg.main import cli, pass_config

GITHUB_URL = 'https://api.github.com'


@cli.group()
@click.option(
    '-u', '--github-url',
    default=GITHUB_URL,
    help='URL to GitHub instance (default: {})'.format(
        GITHUB_URL
    )
)
@pass_config
def github(config, github_url):
    """For setting up a GitHub API token."""
    config.github_url = github_url


@github.command()
@click.argument('token', default='')
@pass_config
def token(config, token):
    """Store and fetch a GitHub access token"""
    if not token:
        if config.verbose:
            info_out(
                'To generate a personal API token, go to:\n\n\t'
                'https://github.com/settings/tokens\n\n'
                'To read more about it, go to:\n\n\t'
                'https://help.github.com/articles/creating-an-access'
                '-token-for-command-line-use/\n\n'
                'Remember to enable "repo" in the scopes.'
            )
        token = getpass.getpass('GitHub API Token: ').strip()
    url = urllib.parse.urljoin(config.github_url, '/user')
    assert url.startswith('https://'), url
    response = requests.get(
        url,
        headers={
            'Authorization': 'token {}'.format(token)
        }
    )
    if response.status_code == 200:
        update(config.configfile, {
            'GITHUB': {
                'github_url': config.github_url,
                'token': token,
                'login': response.json()['login'],
            }
        })
        name = response.json()['name'] or response.json()['login']
        success_out('Hi! {}'.format(name))
    else:
        error_out(
            'Failed - {} ({})'.format(
                response.status_code,
                response.content
            )
        )


@github.command()
@pass_config
def burn(config):
    """Remove and forget your GitHub credentials"""
    state = read(config.configfile)
    if state.get('GITHUB'):
        remove(config.configfile, 'GITHUB')
        success_out('Forgotten')
    else:
        error_out('No stored GitHub credentials')


def get_title(config, org, repo, number):
    base_url = GITHUB_URL
    headers = {}
    state = read(config.configfile)
    credentials = state.get('GITHUB')
    if credentials:
        base_url = state['GITHUB']['github_url']
        headers['Authorization'] = 'token {}'.format(
            credentials['token']
        )
        if config.verbose:
            info_out('Using API token: {}'.format(
                credentials['token'][:10] + '…'
            ))
    url = urllib.parse.urljoin(
        base_url,
        '/repos/{}/{}/issues/{}'.format(
            org, repo, number
        )
    )
    if config.verbose:
        info_out('GitHub URL: {}'.format(url))
    assert url.startswith('https://'), url
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['title'], data['html_url']
    if config.verbose:
        info_out('GitHub Response: {}'.format(response))
    return None, None


@github.command()
@click.option(
    '-i', '--issue-url',
    help='Optionally test fetching a specific issue'
)
@pass_config
def test(config, issue_url):
    """Test your saved GitHub API Token."""
    state = read(config.configfile)
    credentials = state.get('GITHUB')
    if not credentials:
        error_out('No credentials saved. Run: gg github token')
    if config.verbose:
        info_out('Using: {}'.format(credentials['github_url']))

    if issue_url:
        github_url_regex = re.compile(
            'https://github.com/([^/]+)/([^/]+)/issues/(\d+)'
        )
        org, repo, number = github_url_regex.search(issue_url).groups()
        title, _ = get_title(config, org, repo, number)
        if title:
            info_out('It worked!')
            success_out(title)
        else:
            error_out('Unable to fetch')
    else:
        url = urllib.parse.urljoin(
            credentials['github_url'],
            '/user'
        )
        assert url.startswith('https://'), url
        response = requests.get(url, headers={
            'Authorization': 'token {}'.format(
                credentials['token']
            )
        })
        if response.status_code == 200:
            success_out(json.dumps(response.json(), indent=2))
        else:
            error_out('Failed to query - {} ({})'.format(
                response.status_code,
                response.json()
            ))
