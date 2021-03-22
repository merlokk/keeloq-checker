# (c) 2021, Merlok

import pathlib
import click


@click.group()
def kcheck_cli():
    pass


__version__ = open(pathlib.Path(__file__).parent / "VERSION").read().strip()


@kcheck_cli.command()
def version():
    """Version of keeloq checker."""
    click.echo("keeloq checker version: " + __version__)





if __name__ == '__main__':
    kcheck_cli()
