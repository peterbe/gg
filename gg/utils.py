import os
import subprocess

import click


def call_and_error(seq):
    """Use Popen to execute `seq` and return stdout."""
    if isinstance(seq, str):
        seq = seq.split()
    out, err = subprocess.Popen(
        seq,
        stdout=subprocess.PIPE,
        # stderr=and_print and subprocess.STDOUT or subprocess.PIPE
        stderr=subprocess.PIPE
    ).communicate()
    return out.decode('utf-8'), err.decode('utf-8')


def call(seq):
    return call_and_error(seq)[0]


def get_repo_name():
    d = call('git rev-parse --show-toplevel').strip()
    return os.path.split(d)[-1].strip()


def get_branches():
    return call(['git', 'branch'])


def error_out(msg):
    click.echo(click.style(msg, fg='red'))
    raise click.Abort


def success_out(msg):
    click.echo(click.style(msg, fg='green'))


def info_out(msg):
    click.echo(msg)
