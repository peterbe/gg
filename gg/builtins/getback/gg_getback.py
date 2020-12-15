import click

from gg.utils import error_out, info_out, get_default_branch
from gg.state import read
from gg.main import cli, pass_config


@cli.command()
@click.option("-f", "--force", is_flag=True, default=False)
@pass_config
def getback(config, force=False):
    """Goes back to the default branch, deletes the current branch locally
    and remotely."""
    repo = config.repo

    state = read(config.configfile)
    origin_name = state.get("ORIGIN_NAME", "origin")
    default_branch = get_default_branch(repo, origin_name)
    active_branch = repo.active_branch
    if active_branch.name == default_branch:
        error_out(f"You're already on the {default_branch} branch.")

    if repo.is_dirty():
        error_out(
            'Repo is "dirty". ({})'.format(
                ", ".join([repr(x.b_path) for x in repo.index.diff(None)])
            )
        )

    branch_name = active_branch.name

    upstream_remote = None
    fork_remote = None
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
    # XXX I don't know how to do this "natively" with GitPython.
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
    for remote in repo.remotes:
        if remote.name == state.get("FORK_NAME"):
            fork_remote = remote
            break
    if fork_remote:
        fork_remote.push(":" + branch_name)
        info_out("Remote branch on fork deleted too.")
