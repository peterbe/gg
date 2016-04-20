import click

from gg.utils import call_and_error, get_repo_name, get_branches
from gg.state import save

from gg.main import cli, pass_config

@cli.command()
@click.argument('bugnumber', default='')
@pass_config
def start(config, bugnumber=''):
    branches = get_branches()
    if 'Not a git repository' in branches:
        print("Are you sure you're in a git repository?")
        return  # XXX raise click error

    # click.echo("bugnumber=%r" % bugnumber)
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

    branchname = ''
    if bugnumber:
        branchname = 'bug-{}-'.format(bugnumber)

    def clean_branchname(string):
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

    branchname += clean_branchname(description)
    print("CONFIG", config.configfile)
    # print(call_and_error('git checkout -b "{}"'.format(branchname)))

    save(config.configfile, description, branchname, bugnumber)
