import os
from pkg_resources import iter_entry_points

import click

from . import state

DEFAULT_CONFIGFILE = os.path.expanduser('~/.gg.json')


class Config(object):
    def __init__(self):
        self.verbose = False  # default
        self.configfile = DEFAULT_CONFIGFILE


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option(
    '-v', '--verbose',
    is_flag=True
)
@click.option(
    '-c', '--configfile',
    default=DEFAULT_CONFIGFILE,
    help='Path to the config file (default: {})'.format(DEFAULT_CONFIGFILE)
)
@pass_config
def cli(config, configfile, verbose):
    """A glorious command line tool to make your life with git, GitHub
    and Bugzilla much easier."""
    config.verbose = verbose
    config.configfile = configfile
    if not os.path.isfile(configfile):
        state.write(configfile, {})


# load in the builtin apps
from .builtins import bugzilla  # NOQA
from .builtins import github  # NOQA
from .builtins import config as _  # NOQA

# Simply loading all installed packages that have this entry_point
# will be enough. Each plugin automatically registers itself with the
# cli click group.
for entry_point in iter_entry_points(group='gg.plugin', name=None):
    entry_point.load()
