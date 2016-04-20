import os
import click

# from .lib import config
# from .commands import start


DEFAULT_CONFIG_FILE = os.path.expanduser('~/.gg.json')

class Config(object):
    def __init__(self):
        self.verbose = False  # default
        self.config_file = DEFAULT_CONFIG_FILE

pass_config = click.make_pass_decorator(Config, ensure=True)

# @click.command()
@click.group()
@click.option(
    '-v', '--verbose',
    is_flag=True
)
@click.option(
    '--configfile',
    default=DEFAULT_CONFIG_FILE,
    help='Path to the config file'
)
@pass_config
def cli(config, configfile, verbose):
    """A glorious command line tool to make your life with git, GitHub
    and Bugzilla much easier."""
    config.verbose = verbose
    config.configfile = configfile


# cli.add_command(config.initdb)
# cli.add_command(start.start)

# replace this with some entry_point loading magic
from .commands import start
