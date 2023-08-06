import atexit
import os
import sys
from pathlib import Path

from inspector_commons.database import Database
from inspector_commons.telemetry import Telemetry


class Context:
    INSTANCES = {
        "manager": None,
        "browser": None,
        "image": None,
        "recorder": None,
    }

    def __init__(self, logger, config):
        #: Shared console/file logger
        self.logger = logger
        #: Application configuration
        self.config = config
        #: Created pywebview windows
        self.windows = []
        #: Telemetry client
        # TODO: create a property from telemetry, use ABC
        self.telemetry = Telemetry(debug=self.is_debug)
        #: Locators database
        self.database = Database(self.config.get("database", None))
        #: Currently selected locator (for editing)
        self.selected = None
        #: Active webdriver
        self.webdriver = None

        self.telemetry.start_worker()
        atexit.register(self._on_exit)

    def _on_exit(self):
        if self.webdriver is not None:
            self.webdriver.stop()

    @property
    def is_debug(self):
        return self.config.get("debug")

    @property
    def entrypoint(self):
        # note: pywebview uses sys.argv[0] as base
        base = Path(sys.argv[0]).resolve().parent
        static = Path(__file__).resolve().parent / "static"
        return os.path.relpath(str(static), str(base))

    # TODO: move open_window or use ABC
    def open_window(self, kind, **kwargs):
        self.logger.debug("Opening window: %s", kind)

        factory = WINDOWS.get(kind)
        if factory is None:
            raise KeyError(f"Unknown window type: {kind}")

        window = self.INSTANCES[kind]
        if window is not None and window.is_valid:
            window.restore()
            return window

        window = factory.create(self, **kwargs)
        self.INSTANCES[kind] = window

        self.windows.append(window)
        return window

    def close_windows(self):
        for window in reversed(self.windows):
            if window.is_valid:
                self.logger.debug("Closing window: %s", window)
                window.destroy()

    def force_update(self):
        manager = self.INSTANCES["manager"]
        if manager is not None:
            manager.evaluate_js("window.pywebview.state.update()")

    def load_locator(self, name):
        try:
            with self.database.lock:
                self.database.load()
                return self.database.get(name)
        except KeyError:
            return None
