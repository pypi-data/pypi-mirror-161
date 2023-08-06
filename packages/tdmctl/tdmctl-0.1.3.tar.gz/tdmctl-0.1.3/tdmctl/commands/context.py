import typer
from rich.console import Console
from rich.table import Table

from tdmctl.core import ContextManager, ContextNotFoundError, ContextEarlyError

app = typer.Typer()
console = Console()


@app.callback()
def callback():
    """
    Manage Context for acting on multiple servers
    """


@app.command(name="list")
def list_context_command():
    """
    Print available context
    """
    context_manager = ContextManager()
    try:
        active_context_name = context_manager.current.name
    except AttributeError:
        active_context_name = None
    table = Table("Context", "Host", "Username")
    for context in context_manager.context_list:
        if context.name == active_context_name:
            table.add_row(f"*{context.name}", context.host, context.user, style="bold")
        else:
            table.add_row(f"{context.name}", context.host, context.user)
    console.print(table)


@app.command(name="set")
def set_command(name: str):
    """
    Set the current context
    """
    context_manager = ContextManager()
    try:
        context_manager.set_context(name)
        console.print("Context set to {}".format(name))
    except ContextNotFoundError as e:
        console.print(e)


@app.command(name="create")
def create_command(set_current: bool = False):
    """
    Create a new context to config
    """
    context_manager = ContextManager()
    try:
        context_manager.add_context(
                typer.prompt("Context name "),
                typer.prompt("Host example (http://localhost:8080/api) "),
                typer.prompt("User for api"),
                typer.prompt("Password for api"),
                set_current=set_current
        )
        typer.echo("Context created")
    except ContextEarlyError as e:
        typer.echo(e)


@app.command(name="del")
def delete_command(context: str):
    """
    Delete a context
    """
    context_manager = ContextManager()
    try:
        context = context_manager.get_context(context)
        if typer.confirm("Are you sure you want to delete {} at url {} ?".format(context.name, context.host)):
            context_manager.del_context(context)
            typer.echo("Context deleted")
        else:
            typer.echo("Context not deleted")
    except ContextNotFoundError as e:
        typer.echo(e)
