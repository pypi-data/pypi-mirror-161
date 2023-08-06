from pathlib import Path


def get_home_user_path():
    """
    Get the home user path
    """
    return str(Path.home())

