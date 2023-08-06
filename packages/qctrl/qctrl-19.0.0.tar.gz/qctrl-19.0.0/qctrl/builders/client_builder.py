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
# pylint:disable=missing-module-docstring

import logging
from typing import Dict
from urllib.parse import urljoin

from gql import Client
from qctrlcommons.auth import ClientAuthBase
from qctrlcommons.exceptions import QctrlException
from qctrlcommons.utils import generate_user_agent

from qctrl.builders.http_transport import (
    QctrlGqlClient,
    QctrlRequestsHTTPTransport,
)
from qctrl.constants import OIDC_CLIENT_ID
from qctrl.qctrlauth.session import QctrlOAuth2Session
from qctrl.utils import (
    check_client_version,
    error_handler,
)

from .. import __version__ as qctrl_version
from ..scripts_utils import file_path_for_url

LOGGER = logging.getLogger(__name__)


class OIDCClientAuth(ClientAuthBase):
    """
    Client authentication for OIDC.
    """

    def __init__(self, oidc_session):
        super().__init__()
        self.oidc_session = oidc_session

    def encode(self) -> str:
        return f"Bearer {self.oidc_session.access_token}"


@error_handler
def _create_oidc_session(oidc_url: str) -> QctrlOAuth2Session:
    """
    Returns the GQL client.

    Parameters
    ----------
    oidc_url: str
        The Api url the package should use.

    Returns
    -------
    QctrlOAuth2Session
        OpenID compliant OAuth2Session.
    """

    oidc_session = QctrlOAuth2Session(
        client_id=OIDC_CLIENT_ID,
        base_url=oidc_url,
        session_file_path=file_path_for_url(oidc_url),
    )
    oidc_session.authenticate_if_needed()
    return oidc_session


def create_client_auth(oidc_url: str) -> ClientAuthBase:
    """
    Returns the GQL client.

    Parameters
    ----------
    oidc_url: str
        The Api url the package should use.

    Returns
    -------
    ClientAuthBase
        Object to handle authentication in the GQL Client.

    Raises
    ------
    QctrlException
        If user doesn't have the `cli-access` role.
    """
    oidc_session = _create_oidc_session(oidc_url)
    if not oidc_session.has_role("cli-access"):
        oidc_session.invalidate_access_token()
        raise QctrlException(
            "Access not allowed due to invalid subscription. "
            "Please access `https://boulder.q-ctrl.com` to activate your access."
        )

    return OIDCClientAuth(oidc_session)


@check_client_version
def create_gql_client(
    api_root: str, auth: ClientAuthBase = None, headers: Dict = None
) -> Client:
    """Creates a gql client.

    Parameters
    ----------
    auth: ClientAuthBase
        The auth object.
    api_root: str
        The host url.
    headers: Dict
        HTTP headers


    Returns
    -------
    Client
        The GQL Client.
    """

    url = urljoin(api_root, "graphql/")
    LOGGER.debug("gql url: %s", url)
    headers = headers or {}

    headers.update(
        {
            "Content-Encoding": "gzip",
            "Content-Type": "application/json",
            "User-Agent": generate_user_agent("Q-CTRL Python", version=qctrl_version),
        }
    )

    # use_json needs to be set to false otherwise the library will attempt
    # to dump and encode the data twice.
    transport = QctrlRequestsHTTPTransport(
        url=url, use_json=False, headers=headers, auth=auth, retries=3
    )
    return QctrlGqlClient(transport=transport, fetch_schema_from_transport=True)
