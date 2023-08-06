#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import os
from typing import Any, NamedTuple, Union

from gql import gql, Client, RequestsHTTPTransport
from graphql.language.ast import DocumentNode

from . import constants

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class Auth(NamedTuple):
    expiration_dt: datetime
    token: str


###############################################################################


class NuminaClient:
    """
    A wrapper around the default gql.Client that allows for auto_refreshing of the
    authentication token on it's expiration.

    Parameters
    ----------
    numina_graph_url: str
        The URL to target for graphql requests.
        Default: "https://api.numina.co/graphql"
    auto_refresh_on_expiration: bool
        Should the authentication token be refreshed on it's expiration.
        Default: True (refresh authentication token)
    """

    def __init__(
        self,
        numina_graph_url: str = "https://api.numina.co/graphql",
        auto_refresh_on_expiration: bool = True,
    ):
        # Store params
        self.graph_url = numina_graph_url
        self.refresh_auth = auto_refresh_on_expiration

        # Lazy load
        self._client = None

    LOGIN_QUERY = """
        mutation {{
          logIn(
              email: "{email}",
              password: "{password}" ) {{
            jwt {{
              token
              exp
            }}
          }}
        }}
    """

    @staticmethod
    def login(numina_graph_url: str) -> Auth:
        """
        Pull credentials from environment and return authentication details.

        Parameters
        ----------
        numina_graph_url: str
            The URL to target for graphql login.

        Returns
        -------
        auth_details: Auth
            The authentication details returned from the login.

        Raises
        ------
        gql.transport.exceptions.TransportQueryError:
            Failed to login with credentials provided.
        """
        # Get email and pass for env
        email = os.getenv("NUMINA_GRAPH_EMAIL")
        password = os.getenv("NUMINA_GRAPH_PASSWORD")

        # Construct no auth transport and client
        no_auth_transport = RequestsHTTPTransport(url=numina_graph_url)
        no_auth_client = Client(
            transport=no_auth_transport,
            fetch_schema_from_transport=True,
        )

        # Make gql query
        query = gql(NuminaClient.LOGIN_QUERY.format(email=email, password=password))

        # Get result
        result = no_auth_client.execute(query)

        # Unpack and return Auth details
        return Auth(
            expiration_dt=datetime.fromisoformat(result["logIn"]["jwt"]["exp"]),
            token=result["logIn"]["jwt"]["token"],
        )

    @staticmethod
    def create_auth_client(numina_graph_url: str, auth_details: Auth) -> Client:
        """
        Create authenticated client for requests.

        Parameters
        ----------
        numina_graph_url: str
            The URL to target for graphql queries.
        auth_details: Auth
            The authentication details to use for queries.
            See NuminaClient.login() for more details.

        Returns
        -------
        client: Client
            The authenticated client.
        """
        # Create transport and client
        authenticated_transport = RequestsHTTPTransport(
            url=constants.NUMINA_GRAPH_URL,
            headers={"Authorization": auth_details.token},
        )
        authenticated_client = Client(
            transport=authenticated_transport, fetch_schema_from_transport=True
        )

        return authenticated_client

    @staticmethod
    def _auth_is_expired(expiration_dt: datetime) -> bool:
        return datetime.utcnow() > expiration_dt

    @property
    def client(self) -> Client:
        # Check if first time client is being created
        if self._client is None:
            self._auth = self.login(self.graph_url)
            self._client = self.create_auth_client(self.graph_url, self._auth)
            log.debug("Initialized authentication token and client.")

        # Check if auth should be refreshed
        else:
            # Check for expired auth token
            if self._auth_is_expired(self._auth.expiration_dt):
                log.debug("Current authentication token for client has expired.")

                # Check if refresh is allowed
                if self.refresh_auth:
                    self._auth = self.login(self.graph_url)
                    self._client = self.create_auth_client(self.graph_url, self._auth)
                    log.debug("Refreshed authentication token and client.")

        return self._client

    def execute(self, query: Union[str, DocumentNode]) -> Any:
        """
        Passthrough to gql.Client.execute but using the already existing client.

        Parameters
        ----------
        query: Union[str, DocumentNode]
            The graphql query to execute.

        Returns
        -------
        result: Any
            The result from the executed query.
        """
        # Convert str query to gql
        if isinstance(query, str):
            query = gql(query)

        # Run and return query
        return self.client.execute(query)

    def __str__(self) -> str:
        return f"<NuminaClient ['{self.graph_url}']>"

    def __repr__(self) -> str:
        return str(self)
