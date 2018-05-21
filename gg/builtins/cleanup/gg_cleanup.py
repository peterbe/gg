import click
import git

from gg.utils import error_out, get_repo, info_out
from gg.state import read
from gg.main import cli, pass_config
from gg.builtins.branches.gg_branches import find


@cli.command()
@click.argument("searchstring")
@pass_config
def cleanup(config, searchstring):
    """Deletes a found branch locally and remotely."""
    try:
        repo = get_repo()
    except git.InvalidGitRepositoryError as exception:
        error_out('"{}" is not a git repository'.format(exception.args[0]))

    branches_ = list(find(repo, searchstring))
    if not branches_:
        error_out("No branches found")
    elif len(branches_) > 1:
        error_out(
            "More than one branch found.{}".format(
                "\n\t".join([""] + [x.name for x in branches_])
            )
        )

    assert len(branches_) == 1
    branch_name = branches_[0].name
    active_branch = repo.active_branch
    if branch_name == active_branch.name:
        error_out("Can't clean up the current active branch.")
    # branch_name = active_branch.name

    # Check out master
    # repo.heads.master.checkout()
    # Is this one of the merged branches?!
    # XXX I don't know how to do this "nativly" with GitPython.
    merged_branches = [
        x.strip()
        for x in repo.git.branch("--merged").splitlines()
        if x.strip() and not x.strip().startswith("*")
    ]
    was_merged = branch_name in merged_branches
    certain = was_merged
    if not certain:
        # Need to ask the user.
        # XXX This is where we could get smart and compare this branch
        # with the master.
        certain = (
            input("Are you certain it's actually merged? [Y/n] ").lower().strip() != "n"
        )
    if not certain:
        return 1

    if was_merged:
        repo.git.branch("-d", branch_name)
    else:
        repo.git.branch("-D", branch_name)

    fork_remote = None
    state = read(config.configfile)
    for remote in repo.remotes:
        if remote.name == state.get("FORK_NAME"):
            fork_remote = remote
            break
    if fork_remote:
        fork_remote.push(":" + branch_name)
        info_out("Remote branch on fork deleted too.")