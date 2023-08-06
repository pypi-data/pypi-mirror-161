import click
from click.core import Group

from td_connect import td_connect as td

cli = Group("td-connect")


@cli.command()
@click.argument("url")
def save_app_code(url: str):
    """Save the code from authenticated login URL.

    Args:
        url (str): The URL redirected to after login.
    """
    engine = td.create_engine()
    td.save_app_code(url, engine)
    engine.dispose()
    click.echo(click.style("Done!", fg="green"))


@cli.command()
def create_app_table():
    """Create the app table in the database."""
    engine = td.create_engine()
    with engine.begin() as conn:
        td.td_app_table.create(conn, checkfirst=True)
    engine.dispose()
    click.echo(click.style("Done!", fg="green"))
