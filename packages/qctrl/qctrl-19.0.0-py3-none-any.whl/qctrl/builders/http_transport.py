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

import gzip
from typing import (
    Any,
    Dict,
    Optional,
)

import requests
from gql import Client
from gql.transport.exceptions import (
    TransportClosed,
    TransportProtocolError,
    TransportServerError,
)
from gql.transport.requests import (
    MultipartEncoder,
    RequestsHTTPTransport,
    extract_files,
    json,
)
from gql.transport.requests import log as gql_log
from gql.transport.requests import logging as gql_logging
from graphql import (
    DocumentNode,
    ExecutionResult,
    print_ast,
)
from requests.compat import json as complexjson


class QctrlRequestsHTTPTransport(RequestsHTTPTransport):
    """
    Custom GQL requests class to enable compression of requests.
    """

    def execute(  # type: ignore
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        timeout: Optional[int] = None,
        extra_args: Dict[str, Any] = None,
        upload_files: bool = False,
        disable_result_cache: bool = False,
    ) -> ExecutionResult:
        """
        Execute GraphQL query.

        Execute the provided document AST against the configured remote server. This
        uses the requests library to perform a HTTP POST request to the remote server.

        Parameters
        ----------
        document : DocumentNode
            GraphQL query as AST Node object.
        variable_values : Optional[Dict[str, Any]]
            Dictionary of input parameters (Default value = None).
        operation_name : Optional[str]
            Name of the operation that shall be executed.
            Only required in multi-operation documents (Default value = None).
        timeout : Optional[str]
            Specifies a default timeout for requests (Default value = None).
        extra_args : Dict[str, Any]
            Additional arguments to send to the requests post method.
        upload_files : bool
            Set to True if you want to put files in the variable values.
        disable_result_cache: bool
            Disable cache layer usage when retrieve result (Default value = False).

        Returns
        -------
        ExecutionResult
            The result of execution.
            `data` is the result of executing the query, `errors` is null
            if no errors occurred, and is a non-empty array if an error occurred.

        Raises
        ------
        TransportClosed
            If session is closed.
        TransportServerError
            If an error happens on the HTTP request.
        TransportProtocolError
            If server doesn't return as result.
        """

        if not self.session:
            raise TransportClosed("Transport is not connected")

        query_str = print_ast(document)
        payload: Dict[str, Any] = {"query": query_str}

        if operation_name:
            payload["operationName"] = operation_name

        if disable_result_cache is not None:
            self.headers.update({"disable_result_cache": str(disable_result_cache)})

        post_args = {
            "headers": self.headers,
            "auth": self.auth,
            "cookies": self.cookies,
            "timeout": timeout or self.default_timeout,
            "verify": self.verify,
        }

        if upload_files:
            # If the upload_files flag is set, then we need variable_values
            assert variable_values is not None

            # If we upload files, we will extract the files present in the
            # variable_values dict and replace them by null values
            nulled_variable_values, files = extract_files(
                variables=variable_values,
                file_classes=self.file_classes,
            )

            # Save the nulled variable values in the payload
            payload["variables"] = nulled_variable_values

            # Add the payload to the operations field
            operations_str = json.dumps(payload)
            gql_log.debug("operations %s", operations_str)

            # Generate the file map
            # path is nested in a list because the spec allows multiple pointers
            # to the same file. But we don't support that.
            # Will generate something like {"0": ["variables.file"]}
            file_map = {str(i): [path] for i, path in enumerate(files)}

            # Enumerate the file streams
            # Will generate something like {'0': <_io.BufferedReader ...>}
            file_streams = {str(i): files[path] for i, path in enumerate(files)}

            # Add the file map field
            file_map_str = json.dumps(file_map)
            gql_log.debug("file_map %s", file_map_str)

            fields = {"operations": operations_str, "map": file_map_str}

            # Add the extracted files as remaining fields
            for key, value in file_streams.items():
                fields[key] = (getattr(value, "name", key), value)

            # Prepare requests http to send multipart-encoded data
            data = MultipartEncoder(fields=fields)

            post_args["data"] = data

            if post_args["headers"] is None:
                post_args["headers"] = {}
            else:
                post_args["headers"] = {**post_args["headers"]}

            post_args["headers"]["Content-Type"] = data.content_type

        else:
            if variable_values:
                payload["variables"] = variable_values

            data_key = "json" if self.use_json else "data"

            # compress the payload
            json_payload = complexjson.dumps(payload)
            gzip_payload = gzip.compress(bytes(json_payload, "utf-8"))

            post_args[data_key] = gzip_payload

        # Log the payload
        if gql_log.isEnabledFor(gql_logging.INFO):
            gql_log.info(">>> %s", json.dumps(payload))

        # Pass kwargs to requests post method
        post_args.update(self.kwargs)

        # Pass post_args to requests post method
        if extra_args:
            post_args.update(extra_args)

        # Using the created session to perform requests
        response = self.session.request(
            self.method, self.url, **post_args  # type: ignore
        )
        self.response_headers = (  # pylint: disable=attribute-defined-outside-init
            response.headers
        )

        def raise_response_error(resp: requests.Response, reason: str):
            # We raise a TransportServerError if the status code is 400 or higher
            # We raise a TransportProtocolError in the other cases

            try:
                # Raise a HTTPError if response status is 400 or higher
                resp.raise_for_status()
            except requests.HTTPError as exc:
                raise TransportServerError(str(exc), exc.response.status_code) from exc

            result_text = resp.text
            raise TransportProtocolError(
                f"Server did not return a GraphQL result: "
                f"{reason}: "
                f"{result_text}"
            )

        try:
            result = response.json()

            if gql_log.isEnabledFor(gql_logging.INFO):
                gql_log.info("<<< %s", response.text)

        except Exception:  # pylint:disable=broad-except
            raise_response_error(response, "Not a JSON answer")

        if "errors" not in result and "data" not in result:
            raise_response_error(response, 'No "data" or "errors" keys in answer')

        return ExecutionResult(
            errors=result.get("errors"),
            data=result.get("data"),
            extensions=result.get("extensions"),
        )


class QctrlGqlClient(Client):
    """
    Custom gql client class
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # force the fetch schema for validating client and client version
        with self as session:
            session.fetch_schema()
