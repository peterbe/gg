import os
import subprocess
from urllib.parse import urlparse

import click
import git


def get_repo(here="."):
    if os.path.abspath(here) == "/":  # hit rock bottom
        raise git.InvalidGitRepositoryError("Unable to find repo root")
    if os.path.isdir(os.path.join(here, ".git")):
        return git.Repo(here)
    return get_repo(os.path.join(here, ".."))


def get_repo_name():
    repo = get_repo()
    return os.path.basename(repo.working_dir)


def error_out(msg, raise_abort=True):
    click.echo(click.style(msg, fg="red"))
    if raise_abort:
        raise click.Abort


def success_out(msg):
    click.echo(click.style(msg, fg="green"))


def warning_out(msg):
    click.echo(click.style(msg, fg="yellow"))


def info_out(msg):
    click.echo(msg)


def is_github(data):
    if data.get("bugnumber") and data.get("url"):
        return "github" in urlparse(data["url"]).netloc
    return False


def is_bugzilla(data):
    if data.get("bugnumber") and data.get("url"):
        return "bugzilla" in urlparse(data["url"]).netloc
    return False


def get_default_branch(repo, origin_name):
    # TODO: Figure out how to do this with GitPython
    res = subprocess.run(
        f"git remote show {origin_name}".split(),
        check=True,
        capture_output=True,
        cwd=repo.working_tree_dir,
    )
    for line in res.stdout.decode("utf-8").splitlines():
        if line.strip().startswith("HEAD branch:"):
            return line.replace("HEAD branch:", "").strip()

    raise NotImplementedError(f"No remote called {origin_name!r}")
