from pathlib import Path

import yaml
import typer

from tdmctl import core


#
# Config init and getter
#

def get_config_path_file():
    """
    Get the config path .yaml
    """
    return core.get_home_user_path() + "/.tdmctl/config.yaml"


def init_home_user_config():
    """
    Initialize the home user config directory
    """
    home_user_config_path = core.get_home_user_path() + "/.tdmctl"
    if not Path(home_user_config_path).exists():
        Path(home_user_config_path).mkdir(parents=True)


def config_exists():
    """
    Check if the config file exists
    """
    home_user_config_path = get_config_path_file()
    return Path(home_user_config_path).exists()


def get_config():
    """
    Get the config file and ask for create if not
    """
    home_user_config_path = get_config_path_file()
    if not config_exists():
        save_config()
        typer.echo("No config file found")
        create = typer.confirm("Create a config file?")
        if create:
            create_context(set_current=True)
            typer.echo("Config file created")
        else:
            typer.echo("No config file created")
    with open(home_user_config_path, 'r', encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def save_config(config=None):
    """
    Save the config file
    """
    if config is None:
        config = {}
    home_user_config_path = get_config_path_file()
    if not config_exists:
        Path(home_user_config_path).touch()
    with open(home_user_config_path, 'w+', encoding="utf-8") as f:
        yaml.dump(config, f)


# Context management
def get_current_context():
    """
    Get the current context
    """
    lconfig = get_config()
    return lconfig["current_context"]


def set_current_context(name: str):
    """
    Set the current context
    """
    lconfig = get_config()
    if name not in lconfig["context"] or name is not None:
        typer.echo("Context name not found")
        return
    lconfig["current_context"] = name
    save_config(lconfig)
    return lconfig


def get_all_contexts():
    """
    Get all contexts
    """
    lconfig = get_config()
    return lconfig["context"]


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


def delete_context(context: str):
    """
    Delete a context
    """
    lconfig = get_config()
    if context not in lconfig["context"]:
        typer.echo("Context name not found")
        return
    del lconfig["context"][context]
    save_config(lconfig)
    typer.echo("Context deleted")
    if context == get_current_context():
        set_current_context()
        typer.echo("Context set as none")
    return lconfig


# print data
def print_config_context(context: str):
    """
    Print the config file
    """

    lconfig = get_config()
    typer.echo("Host: " + str(lconfig["context"][context]["host"]))
    typer.echo("User: " + str(lconfig["context"][context]["user"]))
    typer.echo("Pass: [REDACTED]")


def print_current_context():
    """
    Print the current context
    """
    print_config_context(get_current_context())


#
# Command zone
#
app = typer.Typer()


@app.command()
def current():
    """
    Print the current context with host and username
    """
    if config_exists():
        print_current_context()
    else:
        typer.echo("No config file found")
        create = typer.confirm("Create a config file?")
        if create:
            create_context(set_current=True)
            typer.echo("Config file created")
            print_current_context()
        else:
            typer.echo("No config file created")


@app.command(name="list")
def list_context():
    """
    Print available context
    """
    current_context_name = get_current_context()
    aviable_contexts = get_all_contexts()
    for name, setting in aviable_contexts.items():
        if name == current_context_name:
            typer.echo("* " + name + " | host: " + setting["host"] + " | user: " + setting["user"])
        else:
            typer.echo("  " + name + " | host: " + setting["host"] + " | user: " + setting["user"])


@app.command(name="set")
def set_context(name: str):
    """
    Set the current context
    """
    set_current_context(name)
    typer.echo("Context set as {}".format(name))


@app.command(name="create")
def create_context_command(set_current: bool = False):
    """
    Create a new context to config
    """
    create_context(set_current)
    typer.echo("Context created")
    return get_config()


@app.command(name="del")
def delete_context_cmd(context: str):
    """
    Delete a context
    """
    delete_context(context)
    typer.echo("Context deleted")
