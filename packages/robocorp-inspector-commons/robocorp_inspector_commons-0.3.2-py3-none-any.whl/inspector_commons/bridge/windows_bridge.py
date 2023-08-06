from inspector_commons.bridge.base import Bridge, traceback
from inspector_commons.bridge.mixin import DatabaseMixin
from inspector_commons.windows_driver import (
    MatchedWindowsLocators,
    OpenWindows,
    WindowsDriver,
    WindowsLocator,
)


class WindowsBridge(DatabaseMixin, Bridge):
    """Javascript API bridge for windows locators."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.windows_driver = WindowsDriver()

    @traceback
    def pick(self, active_window: str) -> WindowsLocator:
        self.logger.info("Picking windows locator from=%s", active_window)
        return self.windows_driver.listen(active_window)

    @traceback
    def validate(self, active_window: str, value: str) -> MatchedWindowsLocators:
        self.logger.info("Validate locator=%s - %s", active_window, value)
        return self.windows_driver.validate(active_window, value)

    @traceback
    def list_windows(self, exclude_titles=None) -> OpenWindows:
        self.logger.info("List available windows")
        return self.windows_driver.list_windows(exclude_titles)

    @traceback
    def focus(self, active_window: str, value: str) -> None:
        self.logger.info("Focus element")
        self.windows_driver.focus(active_window, value)
