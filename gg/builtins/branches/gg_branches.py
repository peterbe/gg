import datetime

import click
import git

from gg.utils import error_out, info_out, success_out

from gg.main import cli, pass_config


class InvalidRemoteName(Exception):
    """when a remote doesn't exist"""


@cli.command()
@click.argument("searchstring", default="")
@pass_config
def branches(config, searchstring=""):
    """List all branches. And if exactly 1 found, offer to check it out."""
    repo = config.repo

    try:
        branches_ = list(find(repo, searchstring))
    except InvalidRemoteName as exception:
        remote_search_name = searchstring.split(":")[0]
        if remote_search_name in [x.name for x in repo.remotes]:
            error_out(f"Invalid remote name {exception!r}")

        (repo_name,) = [
            x.url.split("/")[-1].split(".git")[0]
            for x in repo.remotes
            if x.name == "origin"
        ]
        # Add it and start again
        remote_url = f"https://github.com/{remote_search_name}/{repo_name}.git"
        if not click.confirm(
            f"Add remote {remote_search_name!r} ({remote_url})", default=True
        ):
            error_out("Unable to find or create remote")

        repo.create_remote(remote_search_name, remote_url)
        branches_ = list(find(repo, searchstring))

    if branches_:
        merged = get_merged_branches(repo)
        info_out("Found existing branches...")
        print_list(branches_, merged)
        if len(branches_) == 1 and searchstring:
            # If the found branch is the current one, error
            active_branch = repo.active_branch
            if active_branch == branches_[0]:
                error_out(f"You're already on {branches_[0].name!r}")
            branch_name = branches_[0].name
            if len(branch_name) > 50:
                branch_name = branch_name[:47] + "…"
            check_it_out = (
                input(f"Check out {branch_name!r}? [Y/n] ").lower().strip() != "n"
            )
            if check_it_out:
                branches_[0].checkout()
    elif searchstring:
        error_out(f"Found no branches matching {searchstring!r}.")
    else:
        error_out("Found no branches.")


def find(repo, searchstring, exact=False):
    # When you copy-to-clipboard from GitHub you get something like
    # 'peterbe:1545809-urllib3-1242' for example.
    # But first, it exists as a local branch, use that.
    if searchstring and ":" in searchstring:
        remote_name = searchstring.split(":")[0]
        for remote in repo.remotes:
            if remote.name == remote_name:
                # remote.pull()
                found_remote = remote
                break
        else:
            raise InvalidRemoteName(remote_name)

        for head in repo.heads:
            if exact:
                if searchstring.split(":", 1)[1].lower() == head.name.lower():
                    yield head
                    return
            else:
                if searchstring.split(":", 1)[1].lower() in head.name.lower():
                    yield head
                    return

        info_out(f"Fetching the latest from {found_remote}")
        for fetchinfo in found_remote.fetch():
            if fetchinfo.flags & git.remote.FetchInfo.HEAD_UPTODATE:
                # Most boring
                pass
            else:
                msg = "updated"
                if fetchinfo.flags & git.remote.FetchInfo.FORCED_UPDATE:
                    msg += " (force updated)"
                print(fetchinfo.ref, msg)

            if str(fetchinfo.ref) == searchstring.replace(":", "/", 1):
                yield fetchinfo.ref

    for head in repo.heads:
        if searchstring:
            if exact:
                if searchstring.lower() != head.name.lower():
                    continue
            else:
                if searchstring.lower() not in head.name.lower():
                    continue
        yield head


def get_merged_branches(repo):
    # XXX I wish I could dedude from a git.refs.head.Head object if it was
    # merged. Then I wouldn't have to do this string splitting crap.
    output = repo.git.branch("--merged")
    return [x.split()[-1] for x in output.splitlines() if x.strip()]


def print_list(heads, merged_names):
    def wrap(head):
        try:
            log = head.log()
        except ValueError as exception:
            # https://github.com/gitpython-developers/GitPython/issues/758
            return {
                "head": head,
                "info": {"date": datetime.datetime.utcnow()},
                "error": str(exception),
            }
        try:
            most_recent = log[-1]
        except IndexError:
            return {"head": head, "info": {"date": datetime.datetime.utcnow()}}
        return {
            "head": head,
            "info": {
                "date": datetime.datetime.utcfromtimestamp(most_recent.time[0]),
                "message": most_recent.message,
                "oldhexsha": most_recent.oldhexsha,
            },
        }

    def format_age(dt):
        delta = datetime.datetime.utcnow() - dt
        return str(delta)

    def format_msg(message):
        if len(message) > 80:
            return message[:76] + "…"
        return message

    wrapped = sorted(
        [wrap(head) for head in heads], key=lambda x: x["info"].get("date")
    )
    for each in wrapped:
        info_out("".center(80, "-"))
        success_out(
            each["head"].name
            + (each["head"].name in merged_names and " (MERGED ALREADY)" or "")
        )
        if each.get("error"):
            info_out(f"\tError getting ref log ({each['error']!r})")
        info_out("\t" + each["info"]["date"].isoformat())
        info_out("\t" + format_age(each["info"]["date"]))
        info_out("\t" + format_msg(each["info"].get("message", "*no commit yet*")))
        info_out("")
