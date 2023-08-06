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
import csv
import hashlib
import json
import logging
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Union,
)

import click
from qctrlcommons.exceptions import QctrlException

DEFAULT_AUTH_DIR = Path.home() / ".config" / "qctrl"
LOGGER = logging.getLogger(__name__)


def file_path_for_url(url: str) -> Path:
    """Returns a Path() instance for the default file location using the URL
    MD5 as the filename.

    Parameters
    ----------
    url: str
        path to the file.


    Returns
    -------
    Path
        path object.
    """
    file_name = hashlib.md5(url.encode()).hexdigest()
    return DEFAULT_AUTH_DIR / file_name


TokenType = Dict[str, Union[str, List[str], int]]


def write_auth_file(token: TokenType, file_path: Path) -> None:
    """Writes the authentication file to the specified Path.

    Parameters
    ----------
    token: TokenType
        OIDC token.
    file_path: Path
        path to qctrl credential.

    Raises
    ------
    QctrlException
        no permission to credential file.
    """

    try:
        file_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        file_path.touch(mode=0o600, exist_ok=True)
        file_path.write_text(json.dumps(token))
    except IOError as exc:
        LOGGER.error("%s", exc, exc_info=True)
        raise QctrlException("incorrect permissions for credentials file") from exc


def _write_action_result_to_csv(path: str, actions: List[Dict[str, Any]]):
    """
    Covert action result to csv format

    Parameters
    ----------
    path: str
        Saved file path. It requires filename and file path (i.e path/filename.csv).
    actions: List
        List of action data.
    """
    with open(path, "w", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=actions[0].keys())
        writer.writeheader()
        for json_dict_result in actions:
            json_dict_result["user"] = json_dict_result["user"]["username"]
            writer.writerow(json_dict_result)


def _process_output(result: Dict, output: str = None) -> None:
    """
    Presents the gql response. The result would be printed or save to
    output file with indentation.

    Parameters
    ----------
    result: Dict
        gql response.
    output: str
        output file (Default value = None).
    """
    if output:
        with open(output, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4, sort_keys=True)
            click.echo(f"The result has written to the output file: {output}")
    else:
        # print with indentation
        click.echo(json.dumps(result, indent=4, sort_keys=True))
