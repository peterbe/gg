from gg.utils import error_out, success_out
from gg.state import read
from gg.main import cli, pass_config


@cli.command()
@pass_config
def mastermerge(config):
    """Merge the origin/master into the the current branch"""
    repo = config.repo

    active_branch = repo.active_branch
    if active_branch.name == "master":
        error_out("You're already on the master branch.")
    active_branch_name = active_branch.name

    if repo.is_dirty():
        error_out(
            'Repo is "dirty". ({})'.format(
                ", ".join([repr(x.b_path) for x in repo.index.diff(None)])
            )
        )

    state = read(config.configfile)
    origin_name = state.get("ORIGIN_NAME", "origin")
    upstream_remote = None
    for remote in repo.remotes:
        if remote.name == origin_name:
            upstream_remote = remote
            break
    if not upstream_remote:
        error_out("No remote called {!r} found".format(origin_name))

    repo.heads.master.checkout()
    repo.remotes[origin_name].pull("master")

    repo.heads[active_branch_name].checkout()

    repo.git.merge("master")
    success_out("Merged against {}/master".format(origin_name))
