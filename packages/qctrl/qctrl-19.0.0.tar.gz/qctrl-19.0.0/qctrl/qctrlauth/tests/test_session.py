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
Tests for qctrlauth.session module.
"""

import json
import time

import pytest
from jwt.api_jwt import encode
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from qctrlcommons.exceptions import QctrlException

from qctrl.qctrlauth.session import (
    QctrlApplicationClient,
    QctrlOAuth2Session,
)


class Called(Exception):
    """Custom exception to test if mocked functions are called"""


def test_session_default_parameters():
    session = QctrlOAuth2Session()
    assert session
    assert not session.token

    with pytest.raises(ValueError):
        _ = session.access_token


@pytest.mark.parametrize(
    "parameters, exception, match",
    [
        ({"redirect_uri": "a"}, ValueError, "redirect_uri_port is required"),
        ({"redirect_uri_port": 1}, ValueError, "redirect_uri is required"),
    ],
)
def test_session_parameters_validations(parameters, exception, match):
    with pytest.raises(exception, match=match):
        _ = QctrlOAuth2Session(**parameters)


def test_auto_generating_urls():
    session = QctrlOAuth2Session(base_url="http://test")
    assert session.auth_url
    assert session.token_url
    assert session.auto_refresh_url
    assert session.user_info_url


def test_session_authentication_needed(mocker):
    def _complete_login(*_):
        raise Called("_complete_login")

    mocker.patch("qctrl.qctrlauth.session.complete_login", new=_complete_login)

    session = QctrlOAuth2Session(base_url="http://test")
    with pytest.raises(Called, match="_complete_login"):
        session.authenticate_if_needed()


def test_session_authentication_not_needed(mocker):
    def _user_info(*_):
        return True

    mocker.patch(
        "qctrl.qctrlauth.session.QctrlOAuth2Session.user_info", new_callable=_user_info
    )

    valid_token = {"access_token": "foo", "expires_at": time.time() + 1000}
    session = QctrlOAuth2Session(base_url="http://test", token=valid_token)

    assert session.token is valid_token
    session.authenticate_if_needed()
    assert session.token is valid_token


def test_session_authentication_needed_with_valid_token(mocker):
    """
    Test cases where the access token looks valid but is not accepted by the server.
    """

    def _user_info(*_):
        return False

    def _complete_login(*_):
        raise Called("_complete_login")

    mocker.patch(
        "qctrl.qctrlauth.session.QctrlOAuth2Session.user_info", new_callable=_user_info
    )
    mocker.patch("qctrl.qctrlauth.session.complete_login", new=_complete_login)

    valid_token = {"access_token": "foo", "expires_at": time.time() + 1000}
    session = QctrlOAuth2Session(base_url="http://test", token=valid_token)

    with pytest.raises(Called, match="_complete_login"):
        session.authenticate_if_needed()


def test_session_non_expired_token():
    expires_at = time.time() + QctrlApplicationClient.REFRESH_THRESHOLD + 1
    session = QctrlOAuth2Session(
        token={"access_token": "foo", "expires_at": expires_at}
    )
    assert session.token
    assert session.access_token == "foo"


def test_session_with_expired_token_and_no_refresh():
    expires_at = time.time() + QctrlApplicationClient.REFRESH_THRESHOLD
    session = QctrlOAuth2Session(
        token={"access_token": "foo", "expires_at": expires_at}
    )
    assert session.token
    with pytest.raises(TokenExpiredError):
        _ = session.access_token


def test_session_refresh_token(mocker):
    def _refresh_token(*_):
        return {"access_token": "refreshed", "expires_at": time.time() + 1000}

    mocker.patch(
        "qctrl.qctrlauth.session.QctrlOAuth2Session.refresh_token", new=_refresh_token
    )
    expires_at = time.time() + QctrlApplicationClient.REFRESH_THRESHOLD
    original_token = {"access_token": "foo", "expires_at": expires_at}
    session = QctrlOAuth2Session(base_url="http://test", token=original_token)
    assert session.token is original_token
    assert session.access_token == "refreshed"


def test_session_token_persistance_new(tmp_path, mocker):
    file_path = tmp_path / "token.json"

    def _complete_login(_, __, callback):
        callback("response")

    def _fetch_token(self, *_, **__):
        self.token = {"access_token": "new", "expires_at": time.time() + 1000}
        return self.token

    mocker.patch("qctrl.qctrlauth.session.complete_login", new=_complete_login)
    mocker.patch("qctrl.qctrlauth.session.OAuth2Session.fetch_token", new=_fetch_token)

    session = QctrlOAuth2Session(base_url="http://test", session_file_path=file_path)
    with pytest.raises(ValueError, match="Missing access token"):
        _ = session.access_token
    session.authenticate_if_needed()
    assert session.access_token == "new"
    assert file_path.exists()
    assert "new" in file_path.read_text()


def test_session_token_persistance_existing(tmp_path, mocker):
    file_path = tmp_path / "token.json"

    def _refresh_token(*_):
        return {"access_token": "refreshed", "expires_at": time.time() + 1000}

    mocker.patch(
        "qctrl.qctrlauth.session.QctrlOAuth2Session.refresh_token", new=_refresh_token
    )
    expires_at = time.time() + QctrlApplicationClient.REFRESH_THRESHOLD
    original_token = {"access_token": "foo", "expires_at": expires_at}
    file_path.write_text(json.dumps(original_token))
    session = QctrlOAuth2Session(base_url="http://test", session_file_path=file_path)
    assert session.token == original_token
    assert session.access_token == "refreshed"


def test_session_token_persistance_invalid_path(tmp_path):
    file_path = tmp_path  # using a directory instead of a file
    with pytest.raises(QctrlException, match="cannot be a directory"):
        _ = QctrlOAuth2Session(base_url="http://test", session_file_path=file_path)


@pytest.mark.parametrize("user_role", ["cli-access", ""])
def test_has_role(mocker, user_role):
    def _user_info(*_):
        return True

    mocker.patch(
        "qctrl.qctrlauth.session.QctrlOAuth2Session.user_info", new_callable=_user_info
    )
    client_id = "boulder-opal-python"
    payload = {
        "exp": "898798798",
        "sub": "test_user_id",
        "realm_access": {"roles": ["delete"]},
        "resource_access": {client_id: {"roles": [user_role]}},
    }
    access_token = encode(payload, key="test")
    valid_token = {"access_token": access_token, "expires_at": time.time() + 1000}
    session = QctrlOAuth2Session(
        client_id=client_id, base_url="http://test", token=valid_token
    )
    assert session.has_role("cli-access") == bool(user_role)
