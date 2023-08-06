import requests
import typer

from tdmctl.__init__ import __version__
from tdmctl.commands.context import get_api_endpoint, get_api_credentials

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'tdmctl version ' + __version__
}
api_endpoint = get_api_endpoint()
api_credentials = get_api_credentials()


def check_api_success_reply(r: requests.Response) -> bool:
    """
    Check if the reply is a success reply
    """
    reply_code = r.status_code
    data = r.json()
    if reply_code == 200:
        return True

    typer.echo(f"Exception: {data['detail']} ({reply_code})")
    return False


def get(url: str) -> requests.Response | None:
    """
    Get the url
    # todo add paginator selector
    """
    reply = requests.get(api_endpoint + url, auth=api_credentials, headers=headers)
    if check_api_success_reply(reply):
        return reply
    return None
