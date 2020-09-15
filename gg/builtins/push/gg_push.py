import git
import click

from gg.utils import error_out, info_out, success_out
from gg.state import read
from gg.main import cli, pass_config


@cli.command()
@click.option("-f", "--force", is_flag=True, default=False)
@pass_config
def push(config, force=False):
    """Create push the current branch."""
    repo = config.repo

    state = read(config.configfile)
    default_branch = state.get("DEFAULT_BRANCH", "master")

    active_branch = repo.active_branch
    if active_branch.name == default_branch:
        error_out(
            f"Can't commit when on the {default_branch} branch. "
            "You really ought to do work in branches."
        )

    if not state.get("FORK_NAME"):
        info_out("Can't help you push the commit. Please run: gg config --help")
        return 0

    try:
        repo.remotes[state["FORK_NAME"]]
    except IndexError:
        error_out("There is no remote called '{}'".format(state["FORK_NAME"]))

    destination = repo.remotes[state["FORK_NAME"]]
    if force:
        (pushed,) = destination.push(force=True)
        info_out(pushed.summary)
    else:
        (pushed,) = destination.push()
        print("PUSHED...")
        # print(pushed)
        # print(pushed.flags)
    for enum_name in [
        "DELETED",
        "ERROR",
        "FAST_FORWARD",
        "NEW_HEAD",
        "NEW_TAG",
        "NO_MATCH",
        "REMOTE_FAILURE",
    ]:
        print(f"{enum_name}?:", pushed.flags & getattr(git.remote.PushInfo, enum_name))

    if pushed.flags & git.remote.PushInfo.FORCED_UPDATE:
        success_out(f"Successfully force pushed to {destination}")
    elif (
        pushed.flags & git.remote.PushInfo.REJECTED
        or pushed.flags & git.remote.PushInfo.REMOTE_REJECTED
    ):
        error_out('The push was rejected ("{}")'.format(pushed.summary), False)

        try_force_push = input("Try to force push? [Y/n] ").lower().strip()
        if try_force_push not in ("no", "n"):
            (pushed,) = destination.push(force=True)
            info_out(pushed.summary)
        else:
            return 0
    elif pushed.flags & git.remote.PushInfo.UP_TO_DATE:
        info_out(f"{destination} already up-to-date")
    else:
        success_out(f"Successfully pushed to {destination}")

    return 0
