import click

from gg.utils import error_out, info_out, get_default_branch
from gg.state import read
from gg.main import cli, pass_config
from gg.builtins.branches.gg_branches import find


@cli.command()
@click.option("-f", "--force", is_flag=True, default=False)
@click.argument("searchstring")
@pass_config
def cleanup(config, searchstring, force=False):
    """Deletes a found branch locally and remotely."""
    repo = config.repo

    state = read(config.configfile)
    origin_name = state.get("ORIGIN_NAME", "origin")
    # default_branch = state.get("DEFAULT_BRANCH", "master")
    default_branch = get_default_branch(repo, origin_name)

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
    upstream_remote = None
    fork_remote = None

    origin_name = state.get("ORIGIN_NAME", "origin")
    for remote in repo.remotes:
        if remote.name == origin_name:
            # remote.pull()
            upstream_remote = remote
            break
    if not upstream_remote:
        error_out("No remote called {!r} found".format(origin_name))

    # Check out default branch
    repo.heads[default_branch].checkout()
    upstream_remote.pull(repo.heads[default_branch])

    # Is this one of the merged branches?!
    # XXX I don't know how to do this "nativly" with GitPython.
    merged_branches = [
        x.strip()
        for x in repo.git.branch("--merged").splitlines()
        if x.strip() and not x.strip().startswith("*")
    ]
    was_merged = branch_name in merged_branches
    certain = was_merged or force
    if not certain:
        # Need to ask the user.
        # XXX This is where we could get smart and compare this branch
        # with the default branch.
        certain = (
            input("Are you certain {} is actually merged? [Y/n] ".format(branch_name))
            .lower()
            .strip()
            != "n"
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
