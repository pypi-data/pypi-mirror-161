import typer
from .group import app as group_app

app = typer.Typer()
app.add_typer(group_app, name="group")


@app.callback()
def callback():
    """
    Manage System of TouDoum Server
    """
