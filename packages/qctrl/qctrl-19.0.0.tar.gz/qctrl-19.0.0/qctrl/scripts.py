# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""Module that defines CLI scripts to be used from installed pip package.

For example:
    $ qctrl auth
"""
import logging
import os
from pathlib import Path
from typing import Any

import click
import inflection
from gql import gql
from qctrlcommons.exceptions import QctrlException

from qctrl import __version__
from qctrl.builders.client_builder import (
    create_client_auth,
    create_gql_client,
)
from qctrl.constants import (
    DEFAULT_API_ROOT,
    DEFAULT_OIDC_URL,
    OIDC_CLIENT_ID,
)
from qctrl.qctrlauth.session import QctrlOAuth2Session
from qctrl.queries import (
    ActivityMonitorQuery,
    GetQueueInfoQuery,
    GetWorkerInfoQuery,
)
from qctrl.queries.action_export import ActionExportQuery
from qctrl.scripts_utils import (
    TokenType,
    _process_output,
    _write_action_result_to_csv,
    file_path_for_url,
    write_auth_file,
)
from qctrl.utils import error_handler

DEFAULT_AUTH_DIR = Path.home() / ".config" / "qctrl"
LOGGER = logging.getLogger(__name__)


@click.group()
def main():
    """Q-CTRL CLI tool."""


@main.command()
@click.option("--access-token", required=True, help="JWT Access Token.")
@click.option("--refresh-token", required=True, help="JWT Refresh Token.")
@click.option(
    "--api-root",
    default=DEFAULT_API_ROOT,
    help="Custom Q-CTRL API base URL.",
    show_default=f"{DEFAULT_API_ROOT}",
)
@click.option(
    "--path",
    type=Path,
    default=lambda: os.environ.get("QCTRL_AUTHENTICATION_CREDENTIALS"),
    help=(
        "Use this option to set a custom location for the authentication files. "
        "If preset, will use the ENV variable `QCTRL_AUTHENTICATION_CREDENTIALS`. "
        "Otherwise, defaults to the standard config location."
    ),
)
def generate_auth_file(
    token: TokenType, oidc_url: str = DEFAULT_OIDC_URL, path: Path = None
) -> Any:
    """Generates the Q-CTRL Authentication file from command line.

    Parameters
    ----------
    token: str
        OIDC token.
    oidc_url: str, optional
        qctrl oidc url: (Default value = "https://id.q-ctrl.com/")
    path: Path
        (Default value = None)
    Returns
    -------
    """
    if not path:
        path = file_path_for_url(oidc_url)

    write_auth_file(token, path)


@main.command()
@click.option(
    "--oidc-url",
    default=DEFAULT_OIDC_URL,
    help="Q-CTRL OIDC base URL.",
    show_default=f"{DEFAULT_OIDC_URL}",
)
@click.option(
    "--path",
    type=Path,
    default=lambda: os.environ.get("QCTRL_AUTHENTICATION_CREDENTIALS"),
    help=(
        "Use this option to set a custom location for the authentication files. "
        "If preset, will use the ENV variable `QCTRL_AUTHENTICATION_CREDENTIALS`. "
        "Otherwise, defaults to the standard config location."
    ),
)
@error_handler
def auth(oidc_url: str = DEFAULT_OIDC_URL, path: str = None) -> QctrlOAuth2Session:
    """Q-CTRL Authentication setup.

    Provides default configuration for environmental authentication,
    allowing users to avoid managing in-script credentials. After this setup,
    the Qctrl package can be used in a Python environment as below:

        \b
        $ python
        >>> from qctrl import Qctrl
        >>> qctrl = Qctrl()

    For more details, access our documentation at https://docs.q-ctrl.com
    """

    oidc_client = QctrlOAuth2Session(
        OIDC_CLIENT_ID,
        base_url=oidc_url,
        session_file_path=Path(path) if path else file_path_for_url(oidc_url),
    )
    oidc_client.authenticate()
    return oidc_client


@main.command()
@click.option(
    "--options",
    help="Shows a list of available options for a particular argument.",
    type=click.Choice(["status", "type"], case_sensitive=False),
)
@click.option(
    "--limit",
    help="The number of previously ran actions to show.",
    type=int,
    default=5,
    show_default=True,
)
@click.option(
    "--offset",
    help="Offset the list of actions by a certain amount.",
    type=int,
    default=0,
    show_default=True,
)
@click.option("--status", help="The status of the action.")
@click.option("--type", help="The action type.")
@click.option(
    "--api-root",
    default=DEFAULT_API_ROOT,  # pylint: disable=too-many-arguments
    help="Custom Q-CTRL API base URL.",
    show_default=f"{DEFAULT_API_ROOT}",
)
@click.option(
    "--oidc-url",
    default=DEFAULT_OIDC_URL,
    help="Q-CTRL OIDC base URL.",
    show_default=f"{DEFAULT_OIDC_URL}",
)
def activity(
    options, limit, offset, status, type, api_root, oidc_url
):  # pylint: disable=redefined-builtin
    """
    Shows previously run actions and their statuses.
    """
    # Attempts to use previously store auth file, prompts interactive auth otherwise.
    gql_api = create_gql_client(api_root, create_client_auth(oidc_url))

    activity_monitor = ActivityMonitorQuery(gql_api)

    if options:
        click.secho(
            f"The list of available {inflection.pluralize(options)} are: ", bold=True
        )
        if options == "status":
            [  # pylint: disable=expression-not-assigned
                click.secho(value) for value in activity_monitor.get_valid_statuses()
            ]
        if options == "type":
            [  # pylint: disable=expression-not-assigned
                click.secho(value) for value in activity_monitor.get_valid_types()
            ]
    else:
        activity_monitor(limit=limit, offset=offset, status=status, action_type=type)


@main.command(help="Displays the current version of the 'qctrl' package.")
def version() -> None:
    """
    Outputs the current package version.
    """
    click.secho(__version__)


@main.command(help="Describes the current environment.")
@click.option(
    "--api-root",
    default=DEFAULT_API_ROOT,  # pylint: disable=too-many-arguments
    help="Custom Q-CTRL API base URL.",
    show_default=f"{DEFAULT_API_ROOT}",
)
@click.option(
    "--oidc-url",
    default=DEFAULT_OIDC_URL,
    help="Q-CTRL OIDC base URL.",
    show_default=f"{DEFAULT_OIDC_URL}",
)
@click.option(
    "--type",
    help="specify the report type.",
    default="queue",
    type=click.Choice(["queue", "worker"], case_sensitive=False),
    show_default="queue",
)
def env(api_root, oidc_url, type):  # pylint:disable=redefined-builtin
    """Shows details to allow monitoring of the current
    environment.
    """
    gql_api = create_gql_client(api_root, create_client_auth(oidc_url))
    if type and type == "worker":
        # display per-worker view
        get_env = GetWorkerInfoQuery(gql_api)
    else:
        # display per-queue view
        get_env = GetQueueInfoQuery(gql_api)
    print("Fetching environment details. Please wait ...")
    click.secho(get_env())


@main.command(help="Run GraphQL query.")
@click.option(
    "--api-root",
    default=DEFAULT_API_ROOT,
    help="Custom Q-CTRL API base URL.",
    show_default=f"{DEFAULT_API_ROOT}",
)
@click.option(
    "--oidc-url",
    default=DEFAULT_OIDC_URL,
    help="Q-CTRL OIDC base URL.",
    show_default=f"{DEFAULT_OIDC_URL}",
)
@click.option("--input", "--i", help="input graphql file", required=True)
@click.option("--output", "--o", help="output file", default=None, show_default=None)
def gql_query(api_root, oidc_url, input, output):  # pylint:disable=redefined-builtin
    """
    Runs gql query and return indented result.
    """
    gql_api = create_gql_client(api_root, create_client_auth(oidc_url))
    with open(input, "r", encoding="utf-8") as file:
        query = file.read()
    result = gql_api.execute(gql(query))

    if result.get("errors"):
        # raise exception when there's any root level errors
        raise QctrlException(result["errors"])  # pylint: disable=unsubscriptable-object

    _process_output(result, output)


@main.command(help="Get JWT access token.")
@click.option(
    "--oidc-url",
    default=DEFAULT_OIDC_URL,
    help="Custom Q-CTRL OIDC base URL.",
    show_default=f"{DEFAULT_OIDC_URL}",
)
@click.option("--output", "--o", help="output file", default=None, show_default=None)
@click.pass_context
def access_token(ctx, oidc_url, output):
    """
    Get JWT access token.
    """
    oidc_session = ctx.invoke(auth, oidc_url=oidc_url)
    _process_output({"access_token": oidc_session.access_token}, output)


@main.command(help="Export the action data into csv file.")
@click.option(
    "--api-root",
    help="Custom Q-CTRL API base URL.",
    default=DEFAULT_API_ROOT,
    show_default=f"{DEFAULT_API_ROOT}",
)
@click.option(
    "--oidc-url",
    default=DEFAULT_OIDC_URL,
    help="Custom Q-CTRL OIDC base URL.",
    show_default=f"{DEFAULT_OIDC_URL}",
)
@click.option("--start-date", help="The date begin i.e 2020-12-31", required=True)
@click.option("--end-date", help="The date till i.e 2021-06-30", required=True)
@click.option(
    "--ignore-test-users",
    help="Flag to ignore the action records created by test users.",
    default=True,
    show_default=True,
)
@click.option(
    "--file-name",
    help="Saved file name",
    default="result.csv",
    show_default="result.csv",
)
@click.option("--path", help="Path of saved file", required=True)
def action_export(
    api_root, oidc_url, start_date, end_date, ignore_test_users, file_name, path
):
    """
    Exports action data to csv file.
    """
    directory_path = Path.home() / path
    if not directory_path.exists():
        click.echo(f"Cannot find Path {directory_path}")
    else:
        gql_api = create_gql_client(api_root, create_client_auth(oidc_url))
        action_export_query = ActionExportQuery(gql_api)
        result = action_export_query(start_date, end_date, ignore_test_users)

        if not result:
            click.echo("No match action data found")
        else:
            # format and save the result to file
            saved_path = directory_path / file_name
            _write_action_result_to_csv(saved_path, result)

            click.echo(f"The result has been saved to {saved_path}")
