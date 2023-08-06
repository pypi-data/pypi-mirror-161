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
"""
Q-CTRL OIDC Session.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import (
    Callable,
    Optional,
)

from jwt.api_jwt import decode
from oauthlib.oauth2 import WebApplicationClient
from oauthlib.oauth2.rfc6749.errors import (
    InvalidGrantError,
    TokenExpiredError,
)
from qctrlcommons.exceptions import QctrlException
from qctrlcommons.utils import get_nested_value
from requests_oauthlib import OAuth2Session

from .redirect_listener import (
    complete_login,
    get_free_network_port,
)

LOGGER = logging.getLogger(__name__)

# OAUTHLIB_INSECURE_TRANSPORT=1 disables the requirement for HTTPS for the
# localhost redirect server and allows "insecure" (HTTP) requests to our OIDC
# server as a side effect.
# As the servers will always validate tokens from clients against our trusted CA
# and our public services only accept HTTPS, it is safe to use this at client side.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


class QctrlApplicationClient(WebApplicationClient):
    """
    QctrlApplicationClient is a subclass of WebApplicationClient that
    implements the verify_token helper method.
    """

    REFRESH_THRESHOLD = 60  # seconds

    def verify_token(self):
        """
        Verifies if the token is still valid or is expiring soon.
        """
        if not (self.access_token or self.token.get("access_token")):
            raise ValueError("Missing access token.")

        if self._expires_at and self._expires_at - time.time() < self.REFRESH_THRESHOLD:
            raise TokenExpiredError()


class QctrlOAuth2Session(OAuth2Session):
    """
    QctrlOAuth2Session is a subclass of OAuth2Session.

    This class implements some helper authentication related methods and overrides
    the `access_token` property to automatically refresh the token if it is expired.
    """

    _client: QctrlApplicationClient

    def __init__(
        self,
        client_id=None,
        client=None,
        base_url=None,
        scope=None,
        redirect_uri=None,
        redirect_uri_port=None,
        auto_refresh_kwargs=None,
        session_file_path: Path = None,
        token: Optional[dict] = None,
        token_updater: Optional[Callable] = None,
        **kwargs,
    ):
        """
        Initializes the QctrlOAuth2Session.
        """

        if redirect_uri and not redirect_uri_port:
            raise ValueError("redirect_uri_port is required when redirect_uri is set")

        if redirect_uri_port and not redirect_uri:
            raise ValueError("redirect_uri is required when redirect_uri_port is set")

        self.session_file_path = session_file_path
        self.redirect_uri_port = redirect_uri_port or get_free_network_port()
        redirect_uri = redirect_uri or f"http://localhost:{self.redirect_uri_port}"

        super().__init__(
            client_id=client_id,
            client=client or QctrlApplicationClient(client_id, redirect_uri),
            scope=scope or ["openid", "profile", "email", "offline_access"],
            auto_refresh_kwargs=auto_refresh_kwargs or {"client_id": client_id},
            redirect_uri=redirect_uri,
            token=token or self._token_loader,
            token_updater=token_updater or self._token_updater,
            **kwargs,
        )

        if base_url:
            if not base_url.endswith("/"):
                base_url += "/"

            oidc_base_url = f"{base_url}auth/realms/q-ctrl/protocol/openid-connect/"
            self.auth_url = f"{oidc_base_url}auth"
            self.token_url = f"{oidc_base_url}token"
            self.auto_refresh_url = f"{oidc_base_url}token"
            self.user_info_url = f"{oidc_base_url}userinfo"

    def _token_updater(self, token: dict):
        """
        Saves the token to the file.
        """
        if not self.session_file_path:
            return

        try:
            self.session_file_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            self.session_file_path.touch(mode=0o600, exist_ok=True)
            self.session_file_path.write_text(
                json.dumps(token, indent=2), encoding="utf-8"
            )
        except IOError as exc:
            LOGGER.error("%s", exc, exc_info=True)
            raise QctrlException("incorrect permissions for credentials file") from exc

    @property
    def _token_loader(self):
        """
        Loads the token from the file.
        """
        if not self.session_file_path:
            return {}

        try:
            return json.load(open(self.session_file_path, "r", encoding="utf-8"))
        except FileNotFoundError:
            return {}
        except IsADirectoryError as exc:
            raise QctrlException("credentials file cannot be a directory") from exc

    @property
    def access_token(self):
        try:
            self._client.verify_token()
            return self._client.access_token

        except TokenExpiredError:
            if self.auto_refresh_url:
                try:
                    self.token = self.refresh_token(self.auto_refresh_url)
                except Warning:
                    self.authenticate()

                if self.token_updater:
                    self.token_updater(self.token)
                return self._client.access_token
            raise

    def authenticate(self):
        """
        Generates the authorization url, opens it in the browser and starts the
        local server to listen for the redirect.
        """
        authorization_url, _ = self.authorization_url(self.auth_url)
        print("")
        print("Authentication URL:")
        print("")
        print(authorization_url)
        print("")
        complete_login(
            self.redirect_uri_port,
            authorization_url,
            self._fetch_token_from_authorization_response,
        )
        print("Successful authentication!")

    def authenticate_if_needed(self):
        """
        Verify if the `access_token` is still valid or can be refreshed, if not
        starts the `authenticate` flow.
        """
        try:
            if self.access_token and self.user_info:
                return
            self.authenticate()
        except (InvalidGrantError, ValueError):
            self.authenticate()

    @property
    def user_info(self):
        """
        Returns the user info from the OIDC server.
        """
        response = self.get(self.user_info_url)
        response.raise_for_status()
        return response.json()

    def _fetch_token_from_authorization_response(self, authorization_response):
        """
        Fetch token from authorization response and save it if `token_updater`
        is present.
        """
        print("Finalising authentication...")
        token = self.fetch_token(
            self.token_url, authorization_response=authorization_response
        )
        if self.token_updater:
            self.token_updater(token)

    def has_role(self, role) -> bool:
        """
        Returns True if the user has the given role for the client.
        """
        payload = decode(self.access_token, options={"verify_signature": False})
        client_roles = get_nested_value(
            payload, f"resource_access.{self.client_id}.roles", []
        )
        return role in client_roles

    def invalidate_access_token(self):
        """
        Invalidates the access token, forcing a refresh on next access.
        """
        if not self.token:
            return

        expired_access_token = self.token
        expired_access_token["expires_at"] = -1
        expired_access_token["expires_in"] = -1
        self.token_updater(expired_access_token)
