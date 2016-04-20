import click

@click.command()
# @click.option('')
def initdb():
    click.echo('Initialized the database')
