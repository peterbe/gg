from gg.utils import error_out, info_out, success_out
from gg.state import read
from gg.main import cli, pass_config


@cli.command()
@pass_config
def merge(config):
    """Merge the current branch into master."""
    repo = config.repo

    active_branch = repo.active_branch
    if active_branch.name == "master":
        error_out("You're already on the master branch.")

    if repo.is_dirty():
        error_out(
            'Repo is "dirty". ({})'.format(
                ", ".join([repr(x.b_path) for x in repo.index.diff(None)])
            )
        )

    branch_name = active_branch.name

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
    upstream_remote.pull(repo.heads.master)

    repo.git.merge(branch_name)
    repo.git.branch("-d", branch_name)
    success_out("Branch {!r} deleted.".format(branch_name))

    info_out("NOW, you might want to run:\n")
    info_out("git push origin master\n\n")

    push_for_you = input("Run that push? [Y/n] ").lower().strip() != "n"
    if push_for_you:
        upstream_remote.push("master")
        success_out("Current master pushed to {}".format(upstream_remote.name))

    # XXX perhaps we should delete the branch off the fork remote if it exists
