import os

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


def error_out(msg):
    click.echo(click.style(msg, fg='red'))
    raise click.Abort


def success_out(msg):
    click.echo(click.style(msg, fg='green'))


def info_out(msg):
    click.echo(msg)
