from threading import Lock, Thread
from time import sleep
from typing import Mapping, Optional, Sequence

from grpc import RpcError, StatusCode

from featureguards.common import Attrs, FeatureToggleException
from featureguards.evaluate import is_on
from featureguards.proto.shared.feature_toggle_pb2 import FeatureToggle
from featureguards.rpc.client import Client

DEFAULT_ADDR = 'api.featureguards.com:443'


class FeatureToggles:

    def __init__(self, client: Client,
                 defaults: Optional[Mapping[str, bool]]) -> None:
        self.client = client
        self.listener = None
        self.defaults = defaults

        # Lock protects below
        self.lock = Lock()
        self.stopped = False
        self.client_version = 0
        self.fts_by_name: Mapping[str, FeatureToggle] = {}

    def _process(self, feature_toggles: Sequence[FeatureToggle],
                 version: int) -> None:
        with self.lock:
            for ft in feature_toggles:
                if ft.deleted_at and ft.deleted_at.ToNanoseconds() > 0:
                    continue

                self.fts_by_name[ft.name] = ft

            self.client_version = version

    def is_on(self, name: str, attrs: Optional[Attrs] = None) -> bool:
        """
            is_on returns whether feature flag is on or not based on its settings and the attributes
            passed (optionally).

            Parameters:
                name: str
                    The name of the feature flag as defined in featureguards.com (Case-sensitive)
                attrs: Mapping[str, Union[str, bool, int, float, datetime]], optional
                    Attributes passed as context to featureguards for evaluations. For example,
                    percentage feature flags can hash the user_id to determine if the feature should
                    be on or off for a particular user. Similarly, allow/disallow lists use the
                    attributes passed for evaluating their rules.
        """
        with self.lock:
            found = self.fts_by_name.get(name)
        if not found:
            raise FeatureToggleException(f'feature toggle {name} is not found')

        return is_on(found, attrs)

    def _fetch(self) -> None:
        self.access_token, self.refresh_token = self.client.authenticate()
        fetched = self.client.fetch(self.access_token, 0)
        self._process(fetched.feature_toggles, fetched.version)

    def _start(self) -> None:
        self._fetch()
        self.listener = Thread(target=self._listen_loop,
                               name='feature_guards_listen',
                               daemon=True)
        self.listener.start()

    def stop(self) -> None:
        """
        Stops the background thread used to listen for changes in values for feature flags
        """
        if self.listener:
            with self.lock:
                self.stopped = True

    def _listen_loop(self) -> None:
        while True:
            with self.lock:
                if self.stopped:
                    return

            try:
                self._listen(self.access_token)
            except RpcError as ex:
                if ex.code() == StatusCode.PERMISSION_DENIED:
                    self.client.refresh_and_auth(self.refresh_token)
            except Exception:
                sleep(3)

    def _listen(self, access_token: str) -> None:
        with self.lock:
            client_version = self.client_version
        for payload in self.client.listen(access_token, client_version):
            self._process(payload.feature_toggles, payload.version)


def init(api_key: str,
         addr: str = DEFAULT_ADDR,
         defaults: Mapping[str, bool] = None) -> FeatureToggles:
    client = Client(api_key=api_key, addr=addr)
    return FeatureToggles(client, defaults)
