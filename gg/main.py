import os
from pkg_resources import iter_entry_points

import click

from . import state

DEFAULT_CONFIG_FILE = '~/.gg.json'


class Config(object):
    def __init__(self):
        self.verbose = False  # default
        # The reason for making this depend on possible an OS
        # environment variable is so that tests of plugins can
        # override the default.
        self.config_file = os.path.expanduser(os.environ.get(
            'GG_DEFAULT_CONFIG_FILE',
            DEFAULT_CONFIG_FILE
        ))


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option(
    '-v', '--verbose',
    is_flag=True
)
@click.option(
    '-c', '--configfile',
    default=DEFAULT_CONFIG_FILE,
    help='Path to the config file'
)
@pass_config
def cli(config, configfile, verbose):
    """A glorious command line tool to make your life with git, GitHub
    and Bugzilla much easier."""
    config.verbose = verbose
    config.configfile = configfile
    if not os.path.isfile(configfile):
        state.write(configfile, {})


# Simply loading all installed packages that have this entry_point
# will be enough. Each plugin automatically registers itself with the
# cli click group.
for entry_point in iter_entry_points(group='gg.plugin', name=None):
    entry_point.load()
