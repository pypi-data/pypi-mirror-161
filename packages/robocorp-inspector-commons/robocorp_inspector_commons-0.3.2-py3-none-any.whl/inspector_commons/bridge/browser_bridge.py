import traceback as tb

import requests

from inspector_commons.bridge.base import Bridge, traceback
from inspector_commons.bridge.mixin import DatabaseMixin
from inspector_commons.webdriver import Webdriver, friendly_name


class BrowserBridge(DatabaseMixin, Bridge):
    """Javascript API bridge for browser locators."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elements = []

    @property
    def driver(self):
        return self.ctx.webdriver

    @driver.setter
    def driver(self, value):
        self.ctx.webdriver = value

    @property
    def is_running(self):
        return self.ctx.webdriver is not None and self.ctx.webdriver.is_running

    @property
    def url(self):
        current_url = None
        if self.is_running:
            current_url = self.driver.url
        return current_url

    def status(self):
        try:
            return self.is_running
        except Exception as exc:
            self.logger.exception(exc)
            raise

    def list(self):
        url = self.ctx.config.get("remote")
        if url is None:
            return []

        try:
            response = requests.get(url)
            return response.json()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception(tb.format_exc())
            self.ctx.config.set("remote", None)
            return []

    @traceback
    def connect(self, browser):
        if browser["type"] == "selenium":
            self.logger.info("Connecting to remote webdriver: %s", browser)
            self.driver = Webdriver.from_remote(
                browser["executor_url"],
                browser["session_id"],
                browser["handle"],
            )
        else:
            raise ValueError(f"Unsupported browser type: {browser}")

    @traceback
    def start(self, url=None):
        is_new_session = not self.is_running
        if is_new_session:
            self.driver = Webdriver()
            self.driver.start()

        if url is not None and str(url).strip():
            self.driver.navigate(url)
            response = {"url": url}
        elif is_new_session:
            self.show_guide()
            response = {"url": ""}
        else:
            response = {"url": self.driver.url}

        return response

    @traceback
    def show_guide(self):
        self.driver.show_guide("inspect-guide")

    @traceback
    def stop(self):
        if self.driver:
            self.driver.stop()

    @traceback
    def pick(self):
        if not self.is_running:
            raise RuntimeError("No active browser session")

        self.driver.clear()
        return self.driver.pick()

    @traceback
    def validate(self, strategy, value):
        if not self.is_running:
            raise RuntimeError("No active browser session")

        try:
            self.driver.clear()
            self.elements = self.driver.find(strategy, value)
            if not self.elements:
                raise ValueError("No matches found")

            screenshot = self.elements[0].screenshot_as_base64
            matches = self.driver.highlight(self.elements)
        except Exception as exc:  # pylint: disable=broad-except
            self.logger.info("Failed to validate: %s", exc)
            self.elements = []
            screenshot = ""
            matches = []

        if not self.driver.url.startswith("data:text/html"):
            source = self.driver.url
        else:
            source = ""

        return {
            "source": source,
            "screenshot": screenshot,
            "matches": [{"name": name, "value": value} for name, value in matches],
        }

    @traceback
    def focus(self, match_id):
        if not self.is_running:
            raise RuntimeError("No active browser session")
        try:
            element = self.elements[int(match_id)]
        except (ValueError, IndexError):
            self.logger.warning("Unexpected highlight index: %s", match_id)
            return

        self.logger.debug("Focusing element #%d: %s", match_id, friendly_name(element))
        self.driver.focus(element)
