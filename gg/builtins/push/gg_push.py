import git
import click

from gg.utils import error_out, get_repo, info_out
from gg.state import read
from gg.main import cli, pass_config


@cli.command()
@click.option("-f", "--force", is_flag=True, default=False)
@pass_config
def push(config, force=False):
    """Create push the current branch."""
    try:
        repo = get_repo()
    except git.InvalidGitRepositoryError as exception:
        error_out('"{}" is not a git repository'.format(exception.args[0]))

    active_branch = repo.active_branch
    if active_branch.name == "master":
        error_out(
            "Can't commit when on the master branch. "
            "You really ought to do work in branches."
        )

    state = read(config.configfile)

    if not state.get("FORK_NAME"):
        info_out("Can't help you push the commit. Please run: gg config --help")
        return 0

    try:
        repo.remotes[state["FORK_NAME"]]
    except IndexError:
        error_out("There is no remote called '{}'".format(state["FORK_NAME"]))

    destination = repo.remotes[state["FORK_NAME"]]
    if force:
        pushed, = destination.push(force=True)
        info_out(pushed.summary)
    else:
        pushed, = destination.push()
        # Was it rejected?
        if (
            pushed.flags & git.remote.PushInfo.REJECTED
            or pushed.flags & git.remote.PushInfo.REMOTE_REJECTED
        ):
            error_out('The push was rejected ("{}")'.format(pushed.summary), False)

            try_force_push = input("Try to force push? [Y/n] ").lower().strip()
            if try_force_push not in ("no", "n"):
                pushed, = destination.push(force=True)
                info_out(pushed.summary)
            else:
                return 0
