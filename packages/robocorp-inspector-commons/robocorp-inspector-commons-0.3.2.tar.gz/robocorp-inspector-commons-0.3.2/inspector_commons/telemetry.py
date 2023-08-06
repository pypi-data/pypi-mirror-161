import logging
import queue
import threading
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from requests.packages.urllib3.util.retry import \
    Retry  # pylint: disable=import-error

from inspector_commons.metric import Metric


class TimeoutHTTPAdapter(HTTPAdapter):
    """Mountable timeout adapter for http(s) calls:
    https://github.com/psf/requests/issues/3070#issuecomment-205070203
    """

    DEFAULT_TIMEOUT = 5  # seconds

    def __init__(self, *args, **kwargs):
        if "timeout" in kwargs:
            self.timeout = kwargs.pop("timeout")
        else:
            self.timeout = self.DEFAULT_TIMEOUT
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):  # pylint: disable=arguments-differ
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


class Telemetry:  # pylint: disable=too-few-public-methods
    TIMEOUT = 1.5
    RETRIES = 2
    BASE_URL = "https://telemetry.robocorp.com/metric-v1/"

    def __init__(self, debug=False):
        self._logger = logging.getLogger(__name__)
        self._debug = debug
        self._thread = threading.Thread(target=self._run_worker)
        self._queue = queue.Queue()
        self._session = None

    def start_worker(self):
        self._thread.daemon = True
        self._thread.start()

    def send(self, metric: Metric):
        if not self._session:
            self._logger.debug("Telemetry not initialized")
            return

        if self._debug:
            self._logger.info("Suppressing telemetry: %s", metric)
            return

        self._queue.put(metric)

    def _run_worker(self):
        self._logger.debug("Starting telemetry worker")

        try:
            self._session = requests.Session()
            self._set_adapters()
            self._set_hooks()
        except RequestException as exc:
            self._logger.warning("Cannot initialize telemetry: %s", exc)
            self._session = None
            return

        while True:
            metric = self._queue.get()
            url = self.BASE_URL + quote(
                f"{metric.type}/"
                + f"{metric.timestamp}/"
                + f"{metric.instance_id}/"
                + f"{metric.key}/"
                + f"{metric.value}"
            )

            try:
                self._session.put(url)
                self._logger.info("Sent telemetry: %s", metric)
            except RequestException as error:
                self._logger.warning("Cannot send telemetry: %s", error)

    def _set_adapters(self):
        timeout = TimeoutHTTPAdapter(timeout=Telemetry.TIMEOUT)
        self._session.mount("https://", timeout)
        self._session.mount("http://", timeout)

        retry = HTTPAdapter(max_retries=self._retry_strategy())
        self._session.mount("https://", retry)
        self._session.mount("http://", retry)

    def _set_hooks(self):
        # pylint: disable=unused-argument
        def assert_status_hook(response, *args, **kwargs):
            response.raise_for_status()

        self._session.hooks["response"] = [assert_status_hook]

    def _retry_strategy(self) -> Retry:
        return Retry(
            total=self.RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["PUT"],
        )
