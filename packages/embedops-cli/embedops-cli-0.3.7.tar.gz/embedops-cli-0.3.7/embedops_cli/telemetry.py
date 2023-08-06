"""
`telemetry`
=======================================================================
Utility for telemetry
* Author(s): Jimmy Gomez
"""
import requests
from embedops_cli.config import settings
from .embedops_authorization import get_auth_token

measurement_id = settings.get("measurement_id")
api_secret = settings.get("api_secret")
CLIENT_ID = "embedops-cli"


def login_event():
    """Login Event"""
    event = {"name": "login"}
    send_telemetry(event)


def command_event(command, subcommands):
    """Format CLI command event for telemetry and send"""
    event = {"name": command, "params": subcommands}
    send_telemetry(event)


def send_telemetry(event):
    """Sends telemetry to Embedops telemetry endpoint"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    host = settings.get("host")
    url = f"{host}/api/v1/users/myself/cli-telemetry"
    requests.post(url, headers=headers, json=event)
