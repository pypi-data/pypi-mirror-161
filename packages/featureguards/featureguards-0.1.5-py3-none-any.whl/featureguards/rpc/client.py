from typing import Iterator, Tuple

from featureguards.proto.auth.auth_pb2 import (AuthenticateRequest,
                                               RefreshRequest)
from featureguards.proto.auth.auth_pb2_grpc import AuthStub
from featureguards.proto.toggles.toggles_pb2 import (FetchRequest,
                                                     FetchResponse,
                                                     ListenPayload,
                                                     ListenRequest)
from featureguards.proto.toggles.toggles_pb2_grpc import TogglesStub
from grpc import (RpcError, StatusCode, channel_ready_future, secure_channel,
                  ssl_channel_credentials)

VERSION = 'v0.1.0'
TIMEOUT_SEC = 1


class Client:

    def __init__(self, api_key: str, addr: str) -> None:
        channel = secure_channel(addr, ssl_channel_credentials())
        channel_ready_future(channel).result(timeout=TIMEOUT_SEC)
        self.auth = AuthStub(channel)
        self.toggles = TogglesStub(channel)
        self.api_key = api_key

    # Auth

    def authenticate(self) -> Tuple[str, str]:
        """
            authenticate returns (access, refresh token)
        """
        res = self.auth.Authenticate(
            request=AuthenticateRequest(version=VERSION),
            metadata=(('x-api-key', self.api_key), ),
            timeout=TIMEOUT_SEC)
        return (res.access_token, res.refresh_token)

    def refresh(self, token: str) -> Tuple[str, str]:
        res = self.auth.Refresh(request=RefreshRequest(token=token),
                                timeout=TIMEOUT_SEC)
        return (res.access_token, res.refresh_token)

    def refresh_and_auth(self, token: str) -> Tuple[str, str]:
        try:
            return self.refresh(token)
        except RpcError as ex:
            if ex.code() == StatusCode.PERMISSION_DENIED:
                return self.authenticate()
            raise ex

    # Toggles
    def fetch(self, access_token: str, client_version: int) -> FetchResponse:
        return self.toggles.Fetch(
            request=FetchRequest(version=client_version),
            metadata=(self.with_jwt_token(access_token), ),
            timeout=TIMEOUT_SEC)

    def listen(self, access_token: str,
               client_version: int) -> Iterator[ListenPayload]:
        for payload in self.toggles.Listen(
                request=ListenRequest(version=client_version),
                metadata=(self.with_jwt_token(access_token), ),
                timeout=TIMEOUT_SEC):
            yield payload

    def with_jwt_token(self, token: str) -> Tuple[str, str]:
        return ('authorization', 'Bearer ' + token)
