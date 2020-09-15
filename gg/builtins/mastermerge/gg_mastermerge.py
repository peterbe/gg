from gg.utils import error_out, success_out
from gg.state import read
from gg.main import cli, pass_config


@cli.command()
@pass_config
def mastermerge(config):
    """Merge the origin_name/default_branch into the the current branch"""
    repo = config.repo

    state = read(config.configfile)
    default_branch = state.get("DEFAULT_BRANCH", "master")

    active_branch = repo.active_branch
    if active_branch.name == default_branch:
        error_out(f"You're already on the {default_branch} branch.")
    active_branch_name = active_branch.name

    if repo.is_dirty():
        error_out(
            'Repo is "dirty". ({})'.format(
                ", ".join([repr(x.b_path) for x in repo.index.diff(None)])
            )
        )

    origin_name = state.get("ORIGIN_NAME", "origin")
    upstream_remote = None
    for remote in repo.remotes:
        if remote.name == origin_name:
            upstream_remote = remote
            break
    if not upstream_remote:
        error_out(f"No remote called {origin_name!r} found")

    repo.heads[default_branch].checkout()
    repo.remotes[origin_name].pull(default_branch)

    repo.heads[active_branch_name].checkout()

    repo.git.merge(default_branch)
    success_out(f"Merged against {origin_name}/{default_branch}")
