# -*- coding: utf-8 -*-

import re

from gg.builtins import github
from gg.main import cli, pass_config
from gg.state import read
from gg.utils import (
    error_out,
    get_default_branch,
    info_out,
)


@cli.command()
@pass_config
def pr(config):
    """Find PRs based on the current branch"""
    repo = config.repo

    state = read(config.configfile)
    origin_name = state.get("ORIGIN_NAME", "origin")
    default_branch = get_default_branch(repo, origin_name)

    active_branch = repo.active_branch
    if active_branch.name == default_branch:
        error_out(f"You can't find PRs from the {default_branch} branch. ")

    state = read(config.configfile)

    # try:
    #     data = load(config.configfile, active_branch.name)
    # except KeyError:
    #     error_out(
    #         "You're in a branch that was not created with gg.\n"
    #         "No branch information available."
    #     )

    if not state.get("GITHUB"):
        if config.verbose:
            info_out(
                "Can't help create a GitHub Pull Request.\n"
                "Consider running: gg github --help"
            )
        return 0

    origin = repo.remotes[state.get("ORIGIN_NAME", "origin")]
    rest = re.split(r"github\.com[:/]", origin.url)[1]
    org, repo = rest.split(".git")[0].split("/", 1)

    # Search for an existing open pull request, and remind us of the link
    # to it.
    search = {
        "head": f"{state['FORK_NAME']}:{active_branch.name}",
        "state": "open",
    }
    for pull_request in github.find_pull_requests(config, org, repo, **search):
        print("Pull Request:")
        print("")
        print(
            "\t",
            pull_request["html_url"],
            "  ",
            "(DRAFT)"
            if pull_request["draft"]
            else f"({pull_request['state'].upper()})",
        )
        print("")

        full_pull_request = github.get_pull_request(
            config, org, repo, pull_request["number"]
        )
        # from pprint import pprint

        # pprint(full_pull_request)

        print("Mergeable?", full_pull_request.get("mergeable", "*not known*"))
        print("Updated", full_pull_request["updated_at"])

        print("")
        break
    else:
        info_out("Sorry, can't find a PR")

    return 0


# def _humanize_time(amount, units):
#     """Chopped and changed from http://stackoverflow.com/a/6574789/205832"""
#     intervals = (1, 60, 60 * 60, 60 * 60 * 24, 604800, 2419200, 29030400)
#     names = (
#         ("second", "seconds"),
#         ("minute", "minutes"),
#         ("hour", "hours"),
#         ("day", "days"),
#         ("week", "weeks"),
#         ("month", "months"),
#         ("year", "years"),
#     )

#     result = []
#     unit = [x[1] for x in names].index(units)
#     # Convert to seconds
#     amount = amount * intervals[unit]
#     for i in range(len(names) - 1, -1, -1):
#         a = int(amount) // intervals[i]
#         if a > 0:
#             result.append((a, names[i][1 % a]))
#             amount -= a * intervals[i]
#     return result


# def humanize_seconds(seconds):
#     return "{} {}".format(*_humanize_time(seconds, "seconds")[0])
