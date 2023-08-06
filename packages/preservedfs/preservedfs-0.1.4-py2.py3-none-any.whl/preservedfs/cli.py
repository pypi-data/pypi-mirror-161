import os
import sys
import click
from preservedfs import run
# Main parameters
DEBUG = False


@click.group()
@click.option('--debug/--no-debug', default=DEBUG)
def cli(debug):
    "CLI for PreservedFS."
    DEBUG = debug
    pass


@cli.command()
@click.argument('target', type=click.Path(file_okay=False))
@click.argument('mnt', type=click.Path(file_okay=False))
@click.argument('local', type=click.Path(file_okay=False))
def launch(target, mnt, local):
    """Launch the PreservedFS service.

    This command will mount the `TARGET` folder into
    the `MNT` one. Any changes in `TARGET` will be
    registered in `LOCAL` and reflected in `MNT`.

    Files in `TARGET` are unchanged.
    """
    "Launch the PreservedFS with corresponding parameters."
    os.makedirs(target, exist_ok=True)
    os.makedirs(mnt, exist_ok=True)
    os.makedirs(local, exist_ok=True)
    run(target, mnt, local)


def main():
    "Entry point to the CLI."
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("Welcome to PreservedFS")
    cli()


if __name__ == '__main__':
    main()
