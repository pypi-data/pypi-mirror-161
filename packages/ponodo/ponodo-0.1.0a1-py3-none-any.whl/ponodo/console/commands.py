import click
from werkzeug import run_simple

from ponodo.core import handle_application


@click.group()
def cli():
    """Ask some command to execute nicely"""


@cli.command()
@click.option(
    "-p",
    "--port",
    default=4000,
    show_default=True,
    help="Set the development server port",
)
def serve(port):
    """Run local development server"""
    run_simple(
        "localhost",
        port,
        application=handle_application,
        use_reloader=True,
        use_debugger=True,
        reloader_type="watchdog",
    )


@cli.group()
def make():
    """The fast way to make file"""


@cli.command()
def migrate():
    """Perform database migrations"""
