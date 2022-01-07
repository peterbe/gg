import json

import click

from gg.state import load_config, update_config
from gg.main import cli, pass_config


@cli.command()
@click.option(
    "--push-to-origin",
    default="",
    help="Push to the origin instead of your fork (true or false)",
)
@click.option(
    "--toggle-fixes-message",
    is_flag=True,
    default=False,
    help="Enable or disable the 'fixes' functionality in commits",
)
@pass_config
def local_config(config, push_to_origin="", toggle_fixes_message=False):
    """Setting configuration options per repo name"""
    if push_to_origin:
        try:
            before = load_config(config.configfile, "push_to_origin")
            print(f"push_to_origin before: {before}")
        except KeyError:
            print("push_to_origin before: not set")
        new_value = json.loads(push_to_origin)
        update_config(config.configfile, push_to_origin=new_value)
        print(f"push_to_origin after: {new_value}")

    if toggle_fixes_message:
        try:
            before = load_config(config.configfile, "fixes_message")
            print(f"toggle_fixes_message before: {before}")
        except KeyError:
            print("toggle_fixes_message before: not set")
            before = True  # the default
        new_value = not before
        update_config(config.configfile, fixes_message=new_value)
        print(f"fixes_message after: {new_value}")
