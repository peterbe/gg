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
@pass_config
def config(config, fork_name="", origin_name=""):
    """Setting various configuration options"""
    state = read(config.configfile)
    any_set = False
    if fork_name:
        update(config.configfile, {"FORK_NAME": fork_name})
        success_out("fork-name set to: {}".format(fork_name))
        any_set = True
    if origin_name:
        update(config.configfile, {"ORIGIN_NAME": origin_name})
        success_out("origin-name set to: {}".format(origin_name))
        any_set = True
    if not any_set:
        info_out("Fork-name: {}".format(state["FORK_NAME"]))
