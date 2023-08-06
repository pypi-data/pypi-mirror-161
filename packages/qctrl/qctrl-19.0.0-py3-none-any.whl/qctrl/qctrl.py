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
import os
import sys
import webbrowser
from threading import Thread
from typing import (
    Dict,
    Optional,
    Union,
)

import click
import tenacity
from gql import (
    Client,
    gql,
)
from qctrlcommons.exceptions import QctrlException
from requests.exceptions import (
    BaseHTTPError,
    RequestException,
)

from .builders import (
    AsyncResult,
    build_and_bind_namespaces,
    create_client_auth,
    create_environment,
    create_gql_client,
)
from .constants import (
    BASE_URL,
    DEFAULT_API_ROOT,
    DEFAULT_OIDC_URL,
    INVALID_SUBSCRIPTION_ERROR,
    UNEXPECTED_TOKEN_ERROR,
)
from .graphs import Graph
from .parallel import ParallelExecutionCollector
from .queries import (
    ActivityMonitorQuery,
    GetMutationNameQuery,
    MeQuery,
)
from .utils import (
    PackageRegistry,
    _get_mutation_result_type,
)

LOGGER = logging.getLogger(__name__)


class Qctrl:
    """A mediator class. Used to authenticate with Q-CTRL and access Q-CTRL features.

    Creating an instance of this class requires authentication with Q-CTRL's API.

    The recommended method of authentication is through the interactive authentication
    method. This method can be invoked by simply calling `Qctrl()` without any arguments.
    This method will also create an authentication file that will be used for subsequent
    authentications when using the package.

    .. code-block:: python

      qctrl = Qctrl()

    You can also access toolkits provided by Boulder Opal through the corresponding namespaces
    of the Qctrl object.
    See the `reference <https://docs.q-ctrl.com/boulder-opal/references/qctrl/Toolkits.html>`_
    for details.

    .. deprecated:: 15.4.4
          Email and password based authentication has been removed in favour of
          url based authentication. To authenticate simply call `qctrl = Qctrl()`
          without any additional arguments.

    Parameters
    ----------
    email : str, optional
        The email address for a Q-CTRL account.
        [This field has been deprecated] (Default value = None)
    password : str, optional
        The password for a Q-CTRL account. [This field has been deprecated] (Default value = None)
    api_root : str, optional
        The URL of the Q-CTRL API. (Default value = None)
    oidc_url : str, optional
        The URL of the Q-CTRL OIDC. (Default value = None)
    env_namespace : str, optional
        The environment namespace of the Q-CTRL stack. (Default value = None)
    skip_version_check: bool, optional
        Option for disabling the version check. (Default value = False)
    client : gql.Client, optional
        A GraphQL client that provides access to a Q-CTRL GraphQL endpoint. You can pass
        this parameter to use Q-CTRL features provided by a non-standard Q-CTRL API
        implementation, for example, one running locally or in a private cloud. If you
        pass this parameter, do not pass `email`, `password`, or `api_root`.
        (Default value = None)

    Attributes
    ----------
    functions : :ref:`qctrl.dynamic.namespaces.FunctionNamespace`
    types : :ref:`qctrl.dynamic.types`

    Raises
    ------
    QctrlApiException
    """

    gql_api = None
    functions = None
    types = None

    def __init__(
        self,
        email: str = None,
        password: str = None,
        api_root: str = None,
        oidc_url: str = None,
        env_namespace: Optional[str] = None,
        skip_version_check: bool = False,
        client: Client = None,
    ):
        if not skip_version_check:
            self._check_version_thread()

        if email or password:
            error_message = (
                "Q-CTRL Python package authentication has been updated."
                " Please start a session without your credentials."
            )
            click.echo(error_message)
            sys.exit(1)

        if client is None:
            api_root = api_root or os.environ.get("QCTRL_API_HOST") or DEFAULT_API_ROOT
            oidc_url = oidc_url or os.environ.get("QCTRL_OIDC_URL") or DEFAULT_OIDC_URL

            env_namespace = env_namespace or os.environ.get("QCTRL_ENV_NAMESPACE")
            if env_namespace:
                api_root = BASE_URL.format(f"{env_namespace}.api")
                oidc_url = BASE_URL.format(f"{env_namespace}.id")

            self.gql_api = _build_client(api_root=api_root, oidc_url=oidc_url)
        else:
            if env_namespace or oidc_url or api_root:
                raise ValueError(
                    "If you pass a client, do not pass an env_namespace, oidc_url, or api_root."
                )
            self.gql_api = client

        self.gql_env = create_environment(self.gql_api)
        self.collector: Optional[ParallelExecutionCollector] = None
        self._build_and_bind_namespaces()

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type((RequestException, BaseHTTPError)),
    )
    def _build_and_bind_namespaces(self):
        """Builds the dynamic namespaces."""
        build_and_bind_namespaces(self)

    @staticmethod
    def create_graph() -> Graph:
        """
        Creates a graph object for representing remote computations.

        Returns
        -------
        Graph
            The new graph object.
        """
        return Graph()

    def activity_monitor(
        self,
        limit: int = 5,
        offset: int = 0,
        status: str = None,
        action_type: str = None,
    ) -> None:
        """Prints a list of previously run actions to the console
        and their statuses. Allows users to filter the amount of
        actions shown as well as provide an offset.

        Parameters
        ----------
        limit : int
            The number of previously ran actions to show.(Default is 5)
        offset : int
            Offset the list of actions by a certain amount.
        status : str
            The status of the action.
        action_type : str
            The action type.
        """

        query = ActivityMonitorQuery(self.gql_api)
        query(limit=limit, offset=offset, status=status, action_type=action_type)

    def get_result(
        self, action_id: Union[str, int]
    ) -> "qctrl.dynamic.types.CoreActionResult":
        """This function is used to return the results of a previously run function.
        You will be able to get the id of your action from the activity monitor.

        Parameters
        ----------
        action_id: str
            the id of the action which maps to an executed function.

        Returns
        -------
        qctrl.dynamic.types.CoreActionResult
            an instance of a class derived from a CoreActionResult.
        """
        action_id = str(action_id)

        query = GetMutationNameQuery(self.gql_api)
        mutation_name = query(action_id)

        field_type = _get_mutation_result_type(self.gql_api.schema, mutation_name)

        refresh_query = self.gql_env.build_refresh_query(field_type)
        data = refresh_query(action_id)

        result = self.gql_env.load_data(field_type, data)
        self.gql_env.wait_for_completion(refresh_query, AsyncResult(field_type, result))
        return result

    def parallel(self) -> ParallelExecutionCollector:
        """
        Context manager for executing multiple function calls in parallel.

        Any :ref:`functions <qctrl.dynamic.namespaces.FunctionNamespace>` that you call inside the
        context manager will be scheduled for execution when the context manager exits. For
        example:

        .. code-block:: python

          with qctrl.parallel():
              result_1 = qctrl.functions.calculate_optimization(...)
              result_2 = qctrl.functions.calculate_optimization(...)
              # The functions get executed when the context manager exits, so result_1 and result_2
              # do not have the results of the optimizations yet.

          # Once outside the context manager, the functions have been executed, so result_1 and
          # result_2 now contain the optimization results.

        Returns
        -------
        ParallelExecutionCollector
            The context manager that collects function calls to be executed in parallel.
        """
        return ParallelExecutionCollector(self)

    def is_collecting(self) -> bool:
        """Checks if the object is in collection mode.

        Returns
        -------
        bool
            True if in collection mode, False otherwise.
        """
        return bool(self.collector)

    def start_collection_mode(self, collector: ParallelExecutionCollector):
        """Starts collection mode. All function calls will be collected
        and executed when the collector object exits.

        Parameters
        ----------
        collector: ParallelExecutionCollector
            the collector object where function calls are stored.

        Raises
        ------
        RuntimeError
            unable to enter collection mode if already collecting.
        """
        if self.is_collecting():
            raise RuntimeError("unable to nest parallel collections")

        self.collector = collector

    def stop_collection_mode(self):
        """Stops collection mode. Function calls will be executed
        immediately.
        """
        self.collector = None

    def _run_gql_query(self, query: str, variable_values: Dict = None) -> Dict:
        """
        Runs a GQL query in a Python script.

        Parameters
        ----------
        query: str
            query string.
        variable_values: Dict
            Dictionary of input parameters. (Default value = None)

        Returns
        -------
        Dict
            gql response.

        Raises
        ------
        QctrlException
            if there's any root level errors
        """
        response = self.gql_api.execute(gql(query), variable_values)
        if response.get("errors"):
            raise QctrlException(response["errors"])
        return response

    @staticmethod
    def _check_version_thread():
        """
        Use another thread to check qctrl version.
        """
        for package in PackageRegistry:
            Thread(target=package.check_latest_version, daemon=True).start()


@tenacity.retry(
    wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
    stop=tenacity.stop_after_attempt(3),
    retry=tenacity.retry_if_exception_type((RequestException, BaseHTTPError)),
)
def _build_client(api_root: str, oidc_url: str) -> Client:
    """
    Builds an authenticated GraphQL client and validates its authentication.

    Parameters
    ----------
    api_root: str
        API root (Default value = None)
    oidc_url: str
        OIDC url (Default value = None)

    Returns
    -------
    GraphQLClient
        gql client.
    """

    try:
        auth = create_client_auth(oidc_url)
        client = create_gql_client(api_root, auth)
        MeQuery(client)()

    except QctrlException as error:
        LOGGER.info(error, exc_info=error)

        if "token" in str(error):
            click.echo(UNEXPECTED_TOKEN_ERROR, err=True)
            sys.exit(1)

        if "invalid subscription" in str(error):
            if "api." in api_root:
                webbrowser.open(api_root.replace("api.", "boulder."))

            click.echo(INVALID_SUBSCRIPTION_ERROR, err=True)
            sys.exit(1)

        sys.exit(error)

    return client


__all__ = ["Qctrl"]
