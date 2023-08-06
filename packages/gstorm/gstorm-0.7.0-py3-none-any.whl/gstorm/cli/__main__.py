"""Main CLI g-storm interface.

Enables building static-typed ORM models.
"""

import click
from . import scripts


@click.group()
def cli():
    pass


def main():
    cli.add_command(scripts.cleanup)
    cli.add_command(scripts.validate_schema)
    cli.add_command(scripts.build_classes)
    # cli.add_command(scripts.build_query)
    # cli.add_command(scripts.build_create)
    # cli.add_command(scripts.build_upsert)
    cli()


if __name__ == "__main__":
    main()
