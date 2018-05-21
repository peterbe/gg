# -*- coding: utf-8 -*-

import os
import time
import re

import git
import click

from gg.utils import error_out, get_repo, info_out, success_out, is_github, is_bugzilla
from gg.state import read, load
from gg.main import cli, pass_config
from gg.builtins import github


# a chang.
@cli.command()
@click.option(
    "-n",
    "--no-verify",
    default=False,
    is_flag=True,
    help="This option bypasses the pre-commit and commit-msg hooks.",
)
@pass_config
def commit(config, no_verify):
    """Commit the current branch with all files."""
    try:
        repo = get_repo()
    except git.InvalidGitRepositoryError as exception:
        error_out('"{}" is not a git repository'.format(exception.args[0]))

    active_branch = repo.active_branch
    if active_branch.name == "master":
        error_out(
            "Can't commit when on the master branch. "
            "You really ought to do work in branches."
        )

    now = time.time()

    def count_files_in_directory(directory):
        count = 0
        for root, _, files in os.walk(directory):
            # We COULD crosscheck these files against the .gitignore
            # if we ever felt overachievious.
            count += len(files)
        return count

    # First group all untracked files by root folder
    all_untracked_files = {}
    for path in repo.untracked_files:
        root = path.split(os.path.sep)[0]
        if root not in all_untracked_files:
            all_untracked_files[root] = {
                "files": [],
                "total_count": count_files_in_directory(root),
            }
        all_untracked_files[root]["files"].append(path)

    # Now filter this based on it being single files or a bunch
    untracked_files = {}
    for root, info in all_untracked_files.items():
        for path in info["files"]:
            age = now - os.stat(path).st_mtime
            # If there's fewer untracked files in its directory, suggest
            # the directory instead.
            if info["total_count"] == 1:
                path = root
            if path in untracked_files:
                if age < untracked_files[path]:
                    # youngest file in that directory
                    untracked_files[path] = age
            else:
                untracked_files[path] = age

    if untracked_files:
        ordered = sorted(untracked_files.items(), key=lambda x: x[1], reverse=True)
        print("NOTE! There are untracked files:")
        for path, age in ordered:
            if os.path.isdir(path):
                path = path + "/"
            print("\t", path.ljust(60), humanize_seconds(age), "old")

        # But only put up this input question if one the files is
        # younger than 12 hours.
        young_ones = [x for x in untracked_files.values() if x < 60 * 60 * 12]
        if young_ones:
            ignore = input("Ignore untracked files? [Y/n] ").lower().strip()
            if ignore.lower().strip() == "n":
                error_out(
                    "\n\tLeaving it up to you to figure out what to do "
                    "with those untracked files."
                )
                return 1
            print("")

    state = read(config.configfile)

    try:
        data = load(config.configfile, active_branch.name)
    except KeyError:
        error_out(
            "You're in a branch that was not created with gg.\n"
            "No branch information available."
        )

    if data.get("bugnumber"):
        msg = "bug {} - {}".format(data["bugnumber"], data["description"])
    else:
        msg = data["description"]

    print("Commit message: (type a new one if you want to override)")

    msg = input('"{}" '.format(msg)).strip() or msg

    if data["bugnumber"]:
        if is_bugzilla(data):
            question = 'Add the "fixes" prefix? [N/y] '
        elif is_github(data):
            question = 'Add the "fixes" suffix? [N/y] '
        else:
            raise NotImplementedError("Don't know what issue tracker you use :(")
        fixes = input(question).lower().strip()
        if fixes in ("y", "yes"):
            if is_bugzilla(data):
                msg = "fixes " + msg
            elif is_github(data):
                msg += ", fixes #{}".format(data["bugnumber"])
            else:
                raise NotImplementedError

    # Now we're going to do the equivalent of `git commit -a -m "..."`
    index = repo.index
    files_added = []
    files_removed = []
    for x in repo.index.diff(None):
        if x.deleted_file:
            files_removed.append(x.b_path)
        else:
            files_added.append(x.b_path)
    if not (files_added or files_removed):
        error_out("No files to add or remove")
    if not repo.is_dirty():
        error_out("Branch is not dirty. There is nothing to commit.")
    if files_added:
        index.add(files_added)
    if files_removed:
        index.remove(files_removed)
    try:
        commit = index.commit(msg)
    except git.exc.HookExecutionError as exception:
        if not no_verify:
            info_out(
                "Commit hook failed ({}, exit code {})".format(
                    exception.command, exception.status
                )
            )
            if exception.stdout:
                error_out(exception.stdout)
            elif exception.stderr:
                error_out(exception.stderr)
            else:
                error_out("Commit hook failed.")
        else:
            commit = index.commit(msg, skip_hooks=True)

    if config.verbose:
        success_out("Commit created {}".format(commit.hexsha))

    if not state.get("FORK_NAME"):
        info_out("Can't help you push the commit. Please run: gg config --help")
        return 0

    try:
        repo.remotes[state["FORK_NAME"]]
    except IndexError:
        error_out("There is no remote called '{}'".format(state["FORK_NAME"]))

    push_for_you = (
        input("Push branch to {}? [Y/n] ".format(state["FORK_NAME"])).lower().strip()
    )
    if push_for_you not in ("n", "no"):
        destination = repo.remotes[state["FORK_NAME"]]
        pushed, = destination.push()
        # Was it rejected?
        if (
            pushed.flags & git.remote.PushInfo.REJECTED
            or pushed.flags & git.remote.PushInfo.REMOTE_REJECTED
        ):
            error_out('The push was rejected ("{}")'.format(pushed.summary), False)

            try_force_push = input("Try to force push? [Y/n] ").lower().strip()
            if try_force_push not in ("no", "n"):
                pushed, = destination.push(force=True)
                info_out(pushed.summary)
            else:
                return 0

    else:
        # If you don't want to push, then don't bother with GitHub
        # Pull Request stuff.
        return 0

    if not state.get("GITHUB"):
        if config.verbose:
            info_out(
                "Can't help create a GitHub Pull Request.\n"
                "Consider running: gg github --help"
            )
        return 0

    origin = repo.remotes[state.get("ORIGIN_NAME", "origin")]
    rest = re.split("github\.com[:/]", origin.url)[1]
    org, repo = rest.split(".git")[0].split("/", 1)

    # Search for an existing open pull request, and remind us of the link
    # to it.
    search = {
        "head": "{}:{}".format(state["FORK_NAME"], active_branch.name),
        "state": "open",
    }
    for pull_request in github.find_pull_requests(config, org, repo, **search):
        print("Pull Request already created:")
        print("")
        print("\t", pull_request["html_url"])
        break
    else:
        # If no known Pull Request exists, make a link to create a new one.
        github_url = "https://github.com/{}/{}/compare/{}:{}...{}:{}?expand=1"
        github_url = github_url.format(
            org, repo, org, "master", state["FORK_NAME"], active_branch.name
        )
        print("Now, to make a Pull Request, go to:")
        print("")
        print(github_url)
    print("(⌘-click to open URLs)")

    return 0


def _humanize_time(amount, units):
    """Chopped and changed from http://stackoverflow.com/a/6574789/205832"""
    intervals = (1, 60, 60 * 60, 60 * 60 * 24, 604800, 2419200, 29030400)
    names = (
        ("second", "seconds"),
        ("minute", "minutes"),
        ("hour", "hours"),
        ("day", "days"),
        ("week", "weeks"),
        ("month", "months"),
        ("year", "years"),
    )

    result = []
    unit = [x[1] for x in names].index(units)
    # Convert to seconds
    amount = amount * intervals[unit]
    for i in range(len(names) - 1, -1, -1):
        a = int(amount) // intervals[i]
        if a > 0:
            result.append((a, names[i][1 % a]))
            amount -= a * intervals[i]
    return result


def humanize_seconds(seconds):
    return "{} {}".format(*_humanize_time(seconds, "seconds")[0])
