"""
Copyright (C) 2021 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""

from datetime import datetime, timedelta
from typing import Tuple, List

import grpc
import http.client
import json
import certifi

import kaskada.api.v1alpha.compute_pb2_grpc as compute_grpc
import kaskada.api.v1alpha.materialization_pb2_grpc as material_grpc
import kaskada.api.v1alpha.table_pb2_grpc as table_grpc
import kaskada.api.v1alpha.staged_file_pb2_grpc as staging_grpc
import kaskada.api.v1alpha.view_pb2_grpc as view_grpc


class Client(object):
    LEGACY_ENGINE = "LEGACY"

    def getBearerToken(
        endpoint: str, audience: str, client_id: str, client_secret: str
    ):
        """
        Requests a bearer token given the provided parameters

        Args:
            endpoint (str): the authentication endpoint to request a token from
            audience (str): the audience the token is requesting
            client_id (str): the user provided client id
            client_secret (str): the user provided client secret

        Returns:
            AccessToken: Kaskada Access Token
        """
        conn = http.client.HTTPSConnection(endpoint)
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "audience": audience,
            "grant_type": "client_credentials",
        }
        headers = {
            "content-type": "application/json",
        }
        conn.request("POST", "/oauth/token", json.dumps(payload), headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        return Client.AccessToken.fromJson(data, endpoint, audience, client_id, client_secret)

    class AccessToken(object):
        def fromJson(
            json_data: str,
            endpoint: str,
            audience: str,
            client_id: str,
            client_secret: str,
        ):
            """
            AccessToken constructor

            Args:
                json_data (str): UTF-8 response from the oauth token request
                endpoint (str): the authentication endpoint to request a token from
                audience (str): the audience the token is requesting
                client_id (str): the user provided client id
                client_secret (str): the user provided client secret

            Raises:
                PermissionError: Unable to validate access token.
            """
            data = json.loads(json_data)
            if (
                "access_token" not in data
                and "expires_in" not in data
                and "token_type" not in data
            ):
                raise PermissionError(
                    "Unable to validate access token. Token details: {}".format(
                        json_data
                    )
                )
            access_token = data["access_token"]
            # The token is valid from now + expires_in seconds.
            # Set the renewal time to one hour before the expires time for safety.
            expires_at = datetime.now() + timedelta(0, data["expires_in"] - 3600)
            token_type = data["token_type"]
            return Client.AccessToken(
                access_token=access_token,
                expires_at=expires_at,
                token_type=token_type,
                endpoint=endpoint,
                audience=audience,
                client_id=client_id,
                client_secret=client_secret)

        def fromJwt(
            jwt: str,
        ):
            """
            Creates an AccessToken from a JWT

            Args:
                jwt (str): A pre-authorized JWT

            """
            return Client.AccessToken(access_token=jwt)

        def __init__(self,
                     access_token: str = None,
                     expires_at: int = None,
                     token_type: str = None,
                     endpoint: str = None,
                     audience: str = None,
                     client_id: str = None,
                     client_secret: str = None):
            self.init_time = datetime.now()
            self.access_token = access_token
            self.expires_at = expires_at
            self.token_type = token_type
            self.endpoint = endpoint
            self.client_id = client_id
            self.client_secret = client_secret
            self.audience = audience

    def authorized(
        client_id: str,
        client_secret: str,
        exchange_endpoint: str,
        audience: str,
        endpoint: str,
        is_secure: bool,
    ):
        """
        Initializes an authorized Kaskada Client

        Args:
            client_id (str): Kaskada Client ID
            client_secret (str): Kaskada Client Secret
            exchange_endpoint (str): Authentication endpoint to exchange JWTs
            audience (str): Authentication audience
            endpoint (str): API Endpoint
            is_secure (bool): Use SSL connection.

        Returns:
            Client: Authorized client
        """
        token = Client.getBearerToken(
            exchange_endpoint, audience, client_id, client_secret
        )
        return Client(client_id, token, endpoint, is_secure)

    def preauthorized(
        jwt: str,
        endpoint: str,
        is_secure: bool
    ):
        """
        Initializes a preauthorized Kaskada Client

        Args:
            jwt (str): A valid JWT
            endpoint (str): API Endpoint
            is_secure (bool): Use SSL connection.

        Returns:
            Client: Preauthorized client
        """
        token = Client.AccessToken.fromJwt(jwt)
        return Client(None, token, endpoint, is_secure)

    def client_id_only(client_id: str, endpoint: str, is_secure: bool):
        """
        Initializes a Kaskada Client with a Client ID only

        Args:
            client_id (str): Kaskada only Client ID
            endpoint (str):  API Endpoint
            is_secure (bool): Use SSL

        Returns:
            Client: Demo client
        """
        return Client(client_id, None, endpoint, is_secure)

    def __init__(self,
                 client_id: str = None,
                 client_secret: str = None,
                 jwt: str = None,
                 exchange_endpoint: str = None,
                 audience: str = None,
                 endpoint: str = None,
                 is_secure: bool = None):

        token: Client.AccessToken = None
        # Client with a pre-authorized JWT (using cached JWTs)
        if client_id is None and client_secret is None:
            assert jwt is not None, "client initialization requires a client ID + client secret or a jwt"
            token = Client.AccessToken.fromJwt(jwt)
        # Client with credentials needs to exchange for a token
        elif client_id is not None and client_secret is not None:
            token = Client.getBearerToken(
                exchange_endpoint, audience, client_id, client_secret
            )
        # Client ID only for demo and trial users
        else:
            assert client_id is not None, "client ID must be provided"

        assert exchange_endpoint is not None and len(exchange_endpoint) > 0, \
            "invalid authorization exchange endpoint provided"
        assert audience is not None and len(audience) > 0, "invalid authorization audience provided"
        assert endpoint is not None and len(endpoint) > 0, "invalid api endpoint provided"
        assert is_secure is not None, "invalid is_secure flag provided"

        if is_secure:
            with open(certifi.where(), "rb") as f:
                trusted_certs = f.read()
            credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
            channel = grpc.secure_channel(endpoint, credentials)
        else:
            channel = grpc.insecure_channel(endpoint)
        self.computeStub = compute_grpc.ComputeServiceStub(channel)
        self.tableStub = table_grpc.TableServiceStub(channel)
        self.viewStub = view_grpc.ViewServiceStub(channel)
        self.stagingStub = staging_grpc.StagedFileServiceStub(channel)
        self.materializationStub = material_grpc.MaterializationServiceStub(channel)
        self.client_id = client_id
        self.token = token

    def get_metadata(self) -> List[Tuple[str, str]]:
        """
        Fetches the metadata for the current client. Renews token if necessary.

        Raises:
            Exception: invalid token

        Returns:
            List[Tuple[str, str]]: Client metadata
        """
        if self.token is None:
            return [("client-id", self.client_id)]
        elif self.token.client_id is not None and self.token.client_secret is not None:
            if self.token.expires_at is None:
                raise Exception(
                    "invalid token. please re-initialize the Kaskada client for continued use"
                )

            current_time = datetime.now()
            if self.token.expires_at is not None:
                remaining_token_time = (
                    self.token.expires_at - current_time
                ).total_seconds()
                # A token is expired if the difference between the expired time and current time is non-positive
                if remaining_token_time <= 0:

                    # Refresh the token by requesting a new one
                    self.token = Client.getBearerToken(
                        self.token.endpoint,
                        self.token.audience,
                        self.token.client_id,
                        self.token.client_secret,
                    )
        return [("authorization", self.token.access_token)]
