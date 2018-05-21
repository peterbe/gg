import datetime

import click

from gg.utils import error_out, info_out, success_out

from gg.main import cli, pass_config


@cli.command()
@click.argument("searchstring", default="")
@pass_config
def branches(config, searchstring=""):
    """List all branches. And if exactly 1 found, offer to check it out."""
    repo = config.repo

    branches_ = list(find(repo, searchstring))
    if branches_:
        merged = get_merged_branches(repo)
        info_out("Found existing branches...")
        print_list(branches_, merged)
        if len(branches_) == 1:
            # If the found branch is the current one, error
            active_branch = repo.active_branch
            if active_branch == branches_[0]:
                error_out("You're already on '{}'".format(branches_[0].name))
            branch_name = branches_[0].name
            if len(branch_name) > 50:
                branch_name = branch_name[:47] + "…"
            check_it_out = (
                input("Check out '{}'? [Y/n] ".format(branch_name)).lower().strip()
                != "n"
            )
            if check_it_out:
                branches_[0].checkout()
    elif searchstring:
        error_out("Found no branches matching '{}'.".format(searchstring))
    else:
        error_out("Found no branches.")


def find(repo, searchstring):
    for head in repo.heads:
        if searchstring:
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
            info_out("\tError getting ref log ({!r})".format(each["error"]))
        info_out("\t" + each["info"]["date"].isoformat())
        info_out("\t" + format_age(each["info"]["date"]))
        info_out("\t" + format_msg(each["info"].get("message", "*no commit yet*")))
        info_out("")
