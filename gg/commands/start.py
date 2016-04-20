import click

from gg.utils import call_and_error, get_repo_name, get_branches, error_out
from gg.state import save
from gg.main import cli, pass_config


@cli.command()
@click.argument('bugnumber', default='')
@pass_config
def start(config, bugnumber=''):
    branches = get_branches()
    if 'Not a git repository' in branches:
        error_out("Are you sure you're in a git repository?")

    if bugnumber:
        raise NotImplementedError(bugnumber)
    else:
        summary = None
    if summary:
        description = input('Summary ["{}"]: '.format(summary)).strip()
    else:
        # XXX how do I make that extra space after the : to appear?
        description = input('Summary: '.strip())
    # click.echo(repr(get_repo_name()))
    # click.echo(description)

    branch_name = ''
    if bugnumber:
        branch_name = 'bug-{}-'.format(bugnumber)

    def clean_branch_name(string):
        string = (
            string
            .replace('   ', ' ')
            .replace('  ', ' ')
            .replace(' ', '-')
            .replace('=', '-')
            .replace('->', '-')
            .replace('---', '-')
        )
        for each in ':\'"/(),[]{}.?`$<>#*;':
            string = string.replace(each, '')
        return string.lower().strip()

    branch_name += clean_branch_name(description)
    out, err = call_and_error(['git', 'checkout', '-b', branch_name])
    if err:
        error_out(err)
    elif config.verbose:
        click.echo(out)

    save(config.configfile, description, branch_name, bugnumber)
