import os
from urllib.parse import urlparse

import click
import git


def get_repo(here='.'):
    if os.path.abspath(here) == '/':  # hit rock bottom
        raise git.InvalidGitRepositoryError('Unable to find repo root')
    if os.path.isdir(os.path.join(here, '.git')):
        return git.Repo(here)
    return get_repo(os.path.join(here, '..'))


def get_repo_name():
    repo = get_repo()
    return os.path.basename(repo.working_dir)


def error_out(msg, raise_abort=True):
    click.echo(click.style(msg, fg='red'))
    if raise_abort:
        raise click.Abort


def success_out(msg):
    click.echo(click.style(msg, fg='green'))


def info_out(msg):
    click.echo(msg)


def is_github(data):
    if data.get('bugnumber') and data.get('url'):
        return 'github' in urlparse(data['url']).netloc
    return False


def is_bugzilla(data):
    if data.get('bugnumber') and data.get('url'):
        return 'bugzilla' in urlparse(data['url']).netloc
    return False
