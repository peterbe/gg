# -*- coding: utf-8 -*-

import os
import re
import time

import click
import git
from gg.builtins import github
from gg.main import cli, pass_config
from gg.state import load, read, load_config
from gg.utils import (
    error_out,
    get_default_branch,
    info_out,
    is_bugzilla,
    is_github,
    success_out,
)


@cli.command()
@click.option(
    "-n",
    "--no-verify",
    default=False,
    is_flag=True,
    help="This option bypasses the pre-commit and commit-msg hooks.",
)
@click.option(
    "-y",
    "--yes",
    default=False,
    is_flag=True,
    help="Immediately say yes to any questions",
)
@pass_config
def commit(config, no_verify, yes):
    """Commit the current branch with all files."""
    repo = config.repo

    state = read(config.configfile)
    origin_name = state.get("ORIGIN_NAME", "origin")
    default_branch = get_default_branch(repo, origin_name)

    active_branch = repo.active_branch
    if active_branch.name == default_branch:
        error_out(
            f"Can't commit when on the {default_branch} branch. "
            f"You really ought to do work in branches."
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
        info_out("NOTE! There are untracked files:")
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
        push_to_origin = load_config(config.configfile, "push_to_origin")
    except KeyError:
        push_to_origin = False

    try:
        fixes_message = load_config(config.configfile, "fixes_message")
    except KeyError:
        fixes_message = True

    try:
        data = load(config.configfile, active_branch.name)
    except KeyError:
        error_out(
            "You're in a branch that was not created with gg.\n"
            "No branch information available."
        )

    print("Commit message: (type a new one if you want to override)")
    msg = data["description"]
    if data.get("bugnumber"):
        if is_bugzilla(data):
            msg = "bug {} - {}".format(data["bugnumber"], data["description"])
            msg = not yes and input(f'"{msg}" ').strip() or msg
        elif is_github(data):
            msg = not yes and input(f'"{msg}" ').strip() or msg
            if fixes_message:
                msg += "\n\nPart of #{}".format(data["bugnumber"])
    if yes:
        print(msg)

    if data["bugnumber"] and fixes_message:
        question = 'Add the "fixes" mention? [N/y] '
        fixes = yes or input(question).lower().strip()
        if fixes in ("y", "yes") or yes:
            if is_bugzilla(data):
                msg = "fixes " + msg
            elif is_github(data):
                msg = msg.replace("Part of ", "Fixes ")
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
    files_new = []
    for x in repo.index.diff(repo.head.commit):
        files_new.append(x.b_path)

    proceed = True
    if not (files_added or files_removed or files_new):
        info_out("No files to add or remove.")
        proceed = False
        if input("Proceed anyway? [Y/n] ").lower().strip() == "n":
            proceed = True

    if "Peterbe" in msg:
        print(f"data={data}")
        print(f"msg={msg!r}")
        raise Exception("HOW DID THAT HAPPEN!?")
    if proceed:
        if not repo.is_dirty():
            error_out("Branch is not dirty. There is nothing to commit.")
        if files_added:
            index.add(files_added)
        if files_removed:
            index.remove(files_removed)
        try:
            # Do it like this (instead of `repo.git.commit(msg)`)
            # so that git signing works.
            # commit = repo.git.commit(["-m", msg])
            args = ["-m", msg]
            if no_verify:
                args.append("--no-verify")
            commit = repo.git.commit(args)
        except git.exc.HookExecutionError as exception:
            if not no_verify:
                info_out(
                    f"Commit hook failed ({exception.command}, "
                    f"exit code {exception.status})"
                )
                if exception.stdout:
                    error_out(exception.stdout)
                elif exception.stderr:
                    error_out(exception.stderr)
                else:
                    error_out("Commit hook failed.")
            else:
                commit = index.commit(msg, skip_hooks=True)

        success_out(f"Commit created {commit}")

    if not state.get("FORK_NAME"):
        info_out("Can't help you push the commit. Please run: gg config --help")
        return 0

    if push_to_origin:
        try:
            repo.remotes[origin_name]
        except IndexError:
            error_out(f"There is no remote called {origin_name!r}")
    else:
        try:
            repo.remotes[state["FORK_NAME"]]
        except IndexError:
            error_out(f"There is no remote called {state['FORK_NAME']!r}")

    remote_name = origin_name if push_to_origin else state["FORK_NAME"]

    if yes:
        push_for_you = "yes"
    else:
        push_for_you = input(f"Push branch to {remote_name!r}? [Y/n] ").lower().strip()
    if push_for_you not in ("n", "no"):
        push_output = repo.git.push("--set-upstream", remote_name, active_branch.name)
        print(push_output)

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
    rest = re.split(r"github\.com[:/]", origin.url)[1]
    org, repo = rest.split(".git")[0].split("/", 1)

    # Search for an existing open pull request, and remind us of the link
    # to it.
    search = {
        "head": f"{remote_name}:{active_branch.name}",
        "state": "open",
    }
    prs = github.find_pull_requests(config, org, repo, **search)
    if prs is None:
        error_out("Can't iterate over pull requests")
    for pull_request in prs:
        print("Pull Request already created:")
        print("")
        print("\t", pull_request["html_url"])
        print("")
        break
    else:
        # If no known Pull Request exists, make a link to create a new one.
        if remote_name == origin.name:
            github_url = "https://github.com/{}/{}/compare/{}...{}?expand=1".format(
                org, repo, default_branch, active_branch.name
            )
        else:
            github_url = (
                "https://github.com/{}/{}/compare/{}:{}...{}:{}?expand=1".format(
                    org,
                    repo,
                    org,
                    default_branch,
                    remote_name,
                    active_branch.name,
                )
            )
        print("Now, to make a Pull Request, go to:")
        print("")
        success_out(github_url)
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
