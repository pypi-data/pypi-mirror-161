import typer
from rich.console import Console
from rich.table import Table

from tdmctl import api

app = typer.Typer()
console = Console()


@app.callback()
def callback():
    """
    Manage Group of TouDoum Server
    """


@app.command(name="list")
def list_command():
    """
    Print available group
    """
    data = api.get("/group").json()

    table = Table("Name")
    for group in data["results"]:
        table.add_row(group["name"])
    console.print(table)
