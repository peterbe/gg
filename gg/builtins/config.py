import click

from gg.utils import success_out, info_out
from gg.state import update, read
from gg.main import cli, pass_config


@cli.command()
@click.option(
    "-f",
    "--fork-name",
    default="",
    help="Name of the remote which is the fork where you push your branches.",
)
@click.option(
    "-o",
    "--origin-name",
    default="",
    help="Name of the remote which is the origin remote.",
)
@click.option(
    "-b",
    "--default-branch",
    default="",
    help="Name of the default branch.",
)
@pass_config
def config(config, fork_name="", origin_name="", default_branch=""):
    """Setting various configuration options"""
    state = read(config.configfile)
    if fork_name:
        update(config.configfile, {"FORK_NAME": fork_name})
        success_out(f"fork-name set to: {fork_name}")
    else:
        info_out(f"fork-name: {state['FORK_NAME']}")

    if origin_name:
        update(config.configfile, {"ORIGIN_NAME": origin_name})
        success_out(f"origin-name set to: {origin_name}")
    else:
        info_out(f"origin-name: {state.get('ORIGIN_NAME', '*not set*')}")

    if default_branch:
        update(config.configfile, {"DEFAULT_BRANCH": default_branch})
        success_out(f"default-branch set to: {default_branch}")
    else:
        info_out(f"default-branch: {state.get('DEFAULT_BRANCH', '*not set*')}")
