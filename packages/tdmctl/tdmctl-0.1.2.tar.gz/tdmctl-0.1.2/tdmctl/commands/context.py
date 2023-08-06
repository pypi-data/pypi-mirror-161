from pathlib import Path

import yaml
import typer

from tdmctl import core

#
# Config init and getter
#

default_config = {"current_context": None, "context": {}}


def get_config_path_file() -> str:
    """
    Get the config path .yaml
    """
    return core.get_home_user_path() + "/.tdmctl/config.yaml"


def config_exists() -> bool:
    """
    Check if the config file exists
    """
    return Path(get_config_path_file()).exists()


def init_home_user_config() -> None:
    """
    Initialize the home user config directory
    """
    home_user_config_path = core.get_home_user_path() + "/.tdmctl"
    if not Path(home_user_config_path).exists():
        typer.echo("Creating .tdmctl directory in {}".format(home_user_config_path))
        Path(home_user_config_path).mkdir(parents=True)
    if not config_exists():
        save_config(default_config)


def get_config() -> dict:
    """
    Get the config file and ask for create if not
    """
    home_user_config_path = get_config_path_file()
    with open(home_user_config_path, 'r', encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def save_config(config: dict) -> None:
    """
    Save the config file
    """
    home_user_config_path = get_config_path_file()
    if not config_exists:
        Path(home_user_config_path).touch()
    with open(home_user_config_path, 'w+', encoding="utf-8") as f:
        yaml.dump(config, f)


# Context management
def get_current_context_name() -> str:
    """
    Get the current context
    """
    return get_config()["current_context"]


def set_current_context(name: str | None) -> None:
    """
    Set the current context
    """
    lconfig = get_config()
    if name not in lconfig["context"] or name is None:
        typer.echo("Context name not found")
        return
    lconfig["current_context"] = name
    typer.echo("Context set as {}".format(name))
    save_config(lconfig)


def get_all_contexts() -> dict:
    """
    Get all contexts
    """
    return get_config()["context"]


def create_context(set_current: bool = False) -> str:
    """
    Create a new context to config
    :param set_current: set the new context as current
    :return: the new context name
    """
    lconfig = get_config()
    if "context" not in lconfig:
        lconfig["context"] = {}
    name = typer.prompt("Enter name for context connection (not hostname)")
    lconfig["context"][name] = {
        "host": typer.prompt("Enter hostname for server api (without api suffix)"),
        "user": typer.prompt("Enter username"),
        "pass": typer.prompt("Enter password"),
    }
    save_config(lconfig)
    typer.echo("Context created")
    if set_current:
        set_current_context(name)
        typer.echo("Context set as {}".format(name))
    return name


def delete_context(context_name: str) -> None:
    """
    Delete a context
    """
    lconfig = get_config()
    current_context = lconfig["current_context"]
    if context_name not in lconfig["context"]:
        typer.echo("Context name not found")
        return

    delete = typer.confirm("Are you sure you want to delete context {}?".format(context_name))
    if not delete:
        raise typer.Abort

    del lconfig["context"][context_name]
    save_config(lconfig)
    typer.echo("Context deleted")
    if context_name == current_context:
        set_current_context(None)


# print data
def print_config_context(context_name: str) -> None:
    """
    Print the config file
    """
    lconfig = get_config()
    if context_name not in lconfig["context"]:
        typer.echo("Context name not found")
    else:
        typer.echo("Host: " + str(lconfig["context"][context_name]["host"]))
        typer.echo("User: " + str(lconfig["context"][context_name]["user"]))


def print_current_context() -> None:
    """
    Print the current context
    """
    print_config_context(get_current_context_name())


#
# Command zone
#
app = typer.Typer()


@app.command(name="current")
def current_command():
    """
    Print the current context with host and username
    """
    print_current_context()


@app.command(name="list")
def list_context_command():
    """
    Print available context
    """
    current_context_name = get_current_context_name()
    available_contexts = get_all_contexts()
    for context_name, context_config in available_contexts.items():
        if context_name == current_context_name and current_context_name is not None:
            typer.echo(f"* {context_name} host:{context_config['host']} user:{context_config['user']}")
        else:
            typer.echo(f"  {context_name} host:{context_config['host']} user:{context_config['user']}")


@app.command(name="set")
def set_command(name: str):
    """
    Set the current context
    """
    set_current_context(name)


@app.command(name="create")
def create_command(set_current: bool = False):
    """
    Create a new context to config
    """
    create_context(set_current)


@app.command(name="del")
def delete_command(context: str):
    """
    Delete a context
    """
    delete_context(context)
