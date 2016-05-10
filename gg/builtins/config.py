import click

from gg.utils import success_out, info_out
from gg.state import update, read
from gg.main import cli, pass_config


@cli.command()
@click.option(
    '-f', '--fork-name',
    default='',
    help=(
        'Name of the remote which is the fork where you push your '
        'branches.'
    )
)
@pass_config
def config(config, fork_name):
    """Setting various configuration options"""
    state = read(config.configfile)
    if fork_name:
        update(config.configfile, {
            'FORK_NAME': fork_name
        })
        success_out('fork-name set to: {}'.format(fork_name))
    elif state.get('FORK_NAME'):
        info_out(
            'Fork-name: {}'.format(state['FORK_NAME'])
        )
