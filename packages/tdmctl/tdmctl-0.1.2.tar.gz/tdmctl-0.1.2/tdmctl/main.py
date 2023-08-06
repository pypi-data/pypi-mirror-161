import typer

from tdmctl.__init__ import __version__
from tdmctl.core import *
from tdmctl.commands import context
app = typer.Typer()

app.add_typer(context.app, name="context")

context.init_home_user_config()


@app.callback()
def callback():
    """
    tdmctl
    """

@app.command()
def version():
    """
    Print the version 
    """
    typer.echo("tdmctl version {}".format(__version__))
