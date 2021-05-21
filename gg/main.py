import os
from pkg_resources import iter_entry_points

import click
import git

from . import state
from .utils import error_out, get_repo


DEFAULT_CONFIGFILE = os.path.expanduser("~/.gg.json")


class Config:
    def __init__(self):
        self.verbose = False  # default
        self.configfile = DEFAULT_CONFIGFILE
        try:
            self.repo = get_repo()
        except git.InvalidGitRepositoryError as exception:
            error_out(f"{exception.args[0]} is not a git repository")


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option("-v", "--verbose", is_flag=True)
@click.option(
    "-c",
    "--configfile",
    default=DEFAULT_CONFIGFILE,
    help=f"Path to the config file (default: {DEFAULT_CONFIGFILE})",
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
from .builtins import bugzilla  # noqa
from .builtins import github  # noqa
from .builtins import config as _  # noqa
from .builtins.commit import gg_commit  # noqa
from .builtins.pr import gg_pr  # noqa
from .builtins.merge import gg_merge  # noqa
from .builtins.mastermerge import gg_mastermerge  # noqa
from .builtins.start import gg_start  # noqa
from .builtins.push import gg_push  # noqa
from .builtins.getback import gg_getback  # noqa
from .builtins.rebase import gg_rebase  # noqa
from .builtins.branches import gg_branches  # noqa
from .builtins.cleanup import gg_cleanup  # noqa

# Simply loading all installed packages that have this entry_point
# will be enough. Each plugin automatically registers itself with the
# cli click group.
for entry_point in iter_entry_points(group="gg.plugin", name=None):
    entry_point.load()
