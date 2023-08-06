"""
`embedops_authorization`
=======================================================================
Managing the user login functions
* Author(s): Bailey Steinfadt
"""
import os
import base64
import pathlib
import webbrowser
from time import sleep
import logging
import subprocess
from operator import itemgetter
from urllib.parse import urlparse
import requests
import dotenv
import click
from dynaconf import Dynaconf
from dynaconf.loaders import toml_loader
import boto3
from embedops_cli.api.configuration import Configuration
from embedops_cli.api.rest import ApiException
from embedops_cli.api.api_client import ApiClient
from embedops_cli.eo_types import (
    DockerRegistryException,
    DockerNotRunningException,
    LoginFailureException,
    UnauthorizedUserException,
    UnknownDockerException,
)
from embedops_cli.api.default_api import DefaultApi
from embedops_cli.config import settings

_logger = logging.getLogger(__name__)

EMBEDOPS_REGISTRY = "https://registry.embedops.com"
user_secrets = os.path.join(os.path.expanduser("~"), ".eosecrets.toml")


def get_auth_token(secrets_file=user_secrets) -> str:
    """Retrieve the Auth0 token from user secrets"""
    key = None
    if not os.path.exists(secrets_file):
        return key
    secrets_file_settings = Dynaconf(SETTINGS_FILES=[secrets_file])
    try:
        key = secrets_file_settings.EMBEDOPS_AUTH_TOKEN
    except AttributeError:
        # eat the attribute error because it's expected when the user has not logged in
        pass
    return key


def set_auth_token(auth_token: str, secrets_file=user_secrets):
    """Set the Auth0 token in user secrets"""
    try:
        toml_loader.write(secrets_file, {"EMBEDOPS_AUTH_TOKEN": auth_token}, merge=True)
    except (IOError) as exc:
        raise LoginFailureException from exc


def fetch_registry_token() -> str:
    """Retrieve a GitLab token for the user's group and store it"""
    user_client = get_user_client()

    user = user_client.get_my_user()
    if len(user.groups) < 1:
        raise UnauthorizedUserException

    first_group_membership = user.groups[0]
    org_id = first_group_membership.group.org_id

    token_record = user_client.get_aws_access_key_for_org(org_id)
    set_registry_token(
        token_record.access_key.access_key_id, token_record.access_key.secret_access_key
    )


def get_registry_token(secrets_file=user_secrets):
    """Retrieve the Auth0 token from user secrets"""
    if not os.path.exists(secrets_file):
        raise UnauthorizedUserException
    secrets_file_settings = Dynaconf(SETTINGS_FILES=[secrets_file])
    try:
        registry_token_id = secrets_file_settings.EMBEDOPS_ECR_TOKEN_ID
        registry_token_secret = secrets_file_settings.EMBEDOPS_ECR_TOKEN_SECRET
    except AttributeError as exc:
        raise UnauthorizedUserException from exc
    if not registry_token_id or not registry_token_secret:
        raise UnauthorizedUserException
    return registry_token_id, registry_token_secret


def set_registry_token(
    registry_access_key_id: str,
    registry_secret_access_key: str,
    secrets_file=user_secrets,
):
    """Set the AWS ECR registry access token in user secrets"""
    try:
        toml_loader.write(
            secrets_file, {"EMBEDOPS_ECR_TOKEN_ID": registry_access_key_id}, merge=True
        )
        toml_loader.write(
            secrets_file,
            {"EMBEDOPS_ECR_TOKEN_SECRET": registry_secret_access_key},
            merge=True,
        )

    except (IOError) as exc:
        raise LoginFailureException from exc


def auth0_url_encode(byte_data):
    """
    Safe encoding handles + and /, and also replace = with nothing
    :param byte_data:
    :return:
    """
    return base64.urlsafe_b64encode(byte_data).decode("utf-8").replace("=", "")


def request_authorization():  # pylint: disable=too-many-locals
    """start the routine for the user to authenticate with Auth0"""

    ############## Setup request bits ################
    env_path = pathlib.Path(".") / ".env"
    dotenv.load_dotenv(dotenv_path=env_path)

    # TODO: we'll need to set this to where the .env are stored in the application
    client_id = "wBgMNZyLb76QRZe3eDRsCnoBLBy4qMQh"
    base_url = "https://embedops.us.auth0.com/oauth"

    code_obj = request_user_code(client_id, base_url)

    # Request the user code and verification url, show instructions to user
    user_code = code_obj["user_code"]
    show_login_instructions(user_code)

    # Open the browser window to the login url
    # Start the server and poll until the callback has been invoked
    verification_url = code_obj["verification_uri_complete"]
    device_code = code_obj["device_code"]

    return launch_login_url(verification_url, base_url, device_code, client_id)


def request_user_code(client_id, base_url):
    """Request the code to show to the user"""
    # We generate a nonce (state) that is used to protect against attackers invoking the callback
    data = {
        "audience": "https://app.embedops.com",
        "scope": "openid email profile offline_access",
        "client_id": client_id,
    }
    url = f"{base_url}/device/code"

    code_req_response = requests.post(url, data=data)
    return code_req_response.json()


def show_login_instructions(user_code):
    """Printing some pretty instructions for the user while logging in"""
    click.secho("\n")
    click.secho("-" * 80, fg="magenta")
    click.secho("Welcome to Dojo Five EmbedOps CLI!\n", fg="magenta")
    click.secho(
        "To login, confirm this device in your browser by verifying this code:",
        fg="cyan",
    )
    click.secho(f"\n          >> {user_code} <<\n", fg="bright_cyan")
    click.secho("-" * 80, fg="magenta")


def launch_login_url(verification_url, base_url, device_code, client_id):
    """Launch the url for the user to log into EmbedOps"""
    webbrowser.open_new(verification_url)
    click.secho("\nWaiting for verification in browser:")
    click.secho("(To stop, press cancel in browser and type CTRL+C here)\n")
    verified = False
    while not verified:
        url = f"{base_url}/token"
        token_data = {
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": client_id,
        }
        token_resp = None
        token_record = None
        try:
            token_resp = requests.post(url, data=token_data)
        except RuntimeError as exc:
            raise LoginFailureException from exc

        if token_resp:
            token_record = token_resp.json()
            click.secho("\n")
            break
        click.secho(".", nl=False, fg="magenta")
        sleep(0.1)

    return token_record["access_token"]


def check_token():
    """Check whether the token received is good or not"""
    user = None
    user_client = get_user_client()
    try:
        user = user_client.get_my_user()
    except (ValueError, TypeError, ApiException):
        return False

    return user is not None


def get_user_client():
    """Get a client for the embedops API as the currently signed in user"""
    api_host = settings.get("host")  # TODO: get config.py working in CLI
    auth_token = get_auth_token()
    configuration = Configuration()
    configuration.host = f"{api_host}/api/v1"
    configuration.api_key["Authorization"] = auth_token
    configuration.api_key_prefix["Authorization"] = "Bearer"

    api_client = ApiClient(configuration=configuration)

    return DefaultApi(api_client=api_client)


def docker_cli_login(aws_access_key_id, aws_secret_access_key):
    """Login using Docker CLI. Returns the return code of the subprocess"""

    sts_client = boto3.client(
        "sts",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    # need to assume proper role before being able to grab ECR credentials
    assume_role_response = sts_client.assume_role(
        RoleArn="arn:aws:iam::623731379476:role/EOToolsReadRole",
        RoleSessionName="EmbedOpsCLI-Session",
    )
    aws_access_key_id, aws_secret_access_key, aws_session_token = itemgetter(
        "AccessKeyId", "SecretAccessKey", "SessionToken"
    )(assume_role_response["Credentials"])
    ecr_client = boto3.client(
        "ecr",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
    )
    ecr_authorization_data = ecr_client.get_authorization_token()["authorizationData"][
        0
    ]
    authorization_token, registry_server = itemgetter(
        "authorizationToken", "proxyEndpoint"
    )(ecr_authorization_data)
    registry_token = base64.b64decode(authorization_token).decode().replace("AWS:", "")
    try:
        subprocess.check_output(
            f"echo {registry_token} | \
                docker login -u AWS --password-stdin {urlparse(registry_server).netloc}",
            shell=True,
            stderr=subprocess.DEVNULL,
        )
        return 0
    except subprocess.CalledProcessError as err:
        _logger.error(err.returncode)

        if "Is the docker daemon running?" in str(err.stdout):
            raise DockerNotRunningException from err

        return err.returncode


def login_to_registry(secrets_file=user_secrets):
    """Log into a docker registry"""
    try:
        registry_token_id, registry_token_secret = get_registry_token(secrets_file)
    except UnauthorizedUserException as exc:
        raise UnauthorizedUserException from exc
    return_code = docker_cli_login(registry_token_id, registry_token_secret)
    if return_code == 1:
        raise DockerRegistryException
    if return_code > 0:
        raise UnknownDockerException
    return return_code
