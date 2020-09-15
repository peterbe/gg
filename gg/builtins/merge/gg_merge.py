from gg.utils import error_out, info_out, success_out
from gg.state import read
from gg.main import cli, pass_config


@cli.command()
@pass_config
def merge(config):
    """Merge the current branch into $default_branch."""
    repo = config.repo

    state = read(config.configfile)
    default_branch = state.get("DEFAULT_BRANCH", "master")

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

    origin_name = state.get("ORIGIN_NAME", "origin")
    upstream_remote = None
    for remote in repo.remotes:
        if remote.name == origin_name:
            upstream_remote = remote
            break
    if not upstream_remote:
        error_out(f"No remote called {origin_name!r} found")

    repo.heads[default_branch].checkout()
    upstream_remote.pull(repo.heads[default_branch])

    repo.git.merge(branch_name)
    repo.git.branch("-d", branch_name)
    success_out("Branch {!r} deleted.".format(branch_name))

    info_out("NOW, you might want to run:\n")
    info_out(f"git push {origin_name} {default_branch}\n\n")

    push_for_you = input("Run that push? [Y/n] ").lower().strip() != "n"
    if push_for_you:
        upstream_remote.push(default_branch)
        success_out(f"Current {default_branch} pushed to {upstream_remote.name}")

    # XXX perhaps we should delete the branch off the fork remote if it exists
