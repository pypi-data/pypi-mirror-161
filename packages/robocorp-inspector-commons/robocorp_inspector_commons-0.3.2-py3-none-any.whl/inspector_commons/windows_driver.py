import base64
import logging
from dataclasses import dataclass
from io import BytesIO
from queue import Empty, Queue
from typing import Dict, List, Tuple, Union

import uiautomation as auto
import win32api  # pylint: disable=import-error
import win32gui  # pylint: disable=import-error
from PIL import ImageGrab
from pynput_robocorp.mouse import Listener
from RPA.core.geometry import Region
from RPA.core.windows import ElementInspector, RecordElement, WindowsElements

LOCATOR_VERSION = 1.0

PICK_TIMEOUT = 60

COLOR_RED = win32api.RGB(255, 0, 0)


WindowsLocatorProperties = Dict[str, str]
WindowsLocator = Dict[str, WindowsLocatorProperties]
MatchedWindowsLocator = Dict[str, Union[str, float]]
MatchedWindowsLocators = Dict[str, List[MatchedWindowsLocator]]
OpenWindow = Dict[str, str]
OpenWindows = List[OpenWindow]


@dataclass
class Rectangle(Region):
    @classmethod
    def from_element(cls, element):
        left = int(element.xcenter - (element.width / 2))
        right = int(element.xcenter + (element.width / 2))
        bottom = int(element.ycenter + (element.height / 2))
        top = int(element.ycenter - (element.height / 2))
        return cls(left, top, right, bottom)

    @classmethod
    def from_control(cls, control: auto.Control):
        left = int(control.BoundingRectangle.left)
        top = int(control.BoundingRectangle.top)
        right = int(control.BoundingRectangle.right)
        bottom = int(control.BoundingRectangle.bottom)
        return cls(left, top, right, bottom)

    def get_screenshot(self) -> str:
        image = ImageGrab.grab(self.as_tuple())
        jpeg_image_buffer = BytesIO()
        image.save(jpeg_image_buffer, format="JPEG")
        return base64.b64encode(jpeg_image_buffer.getvalue()).decode("utf-8")

    def get_borders(self, thickness: int) -> List[Tuple[int, int, int, int]]:
        """Get one pixel rectangles as tuples from rectangle coordinates"""
        rect = self.as_tuple()
        return [
            (rect[0] + i, rect[1] + i, rect[2] - i, rect[3] - i)
            for i in range(thickness)
        ]


class WindowMismatch(Exception):
    pass


class WindowsDriver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._windows_elements = WindowsElements()
        self._active_window = ""
        self.queue = Queue()

    def _construct_locator(
        self,
        element: RecordElement,
    ) -> WindowsLocator:
        locator_path: str = element["locator"]
        control: auto.Control = element["control"]
        window_name: str = element["top"]
        if window_name != self._active_window:
            raise WindowMismatch("Non active window clicked")

        name = control.Name or "WindowsLocator"

        properties = {
            "window": self._active_window,
            "strategy": "WindowsLocator",
            "value": locator_path,
            "version": LOCATOR_VERSION,
        }

        if hasattr(control, "BoundingRectangle"):
            try:
                properties["screenshot"] = Rectangle.from_control(
                    control
                ).get_screenshot()
            except AttributeError as err:
                self.logger.error("Failed to get locator screenshot=%r", err)

        return {name: properties}

    def _on_click(
        self,
        x_coord: int,
        y_coord: int,
        element: auto.Control,  # pylint: disable=unused-argument
        pressed: bool,
    ) -> None:
        self.logger.debug("Element clicked (%s) at=%s,%s", pressed, x_coord, y_coord)

        locator = {}

        try:
            elements: List[RecordElement] = []
            ElementInspector.inspect_element(action="", recording=elements)
            locator = self._construct_locator(elements[0])
        except (ValueError, IndexError) as err:
            self.logger.error(err)
        except WindowMismatch as err:
            self.logger.info(err)
            return

        self.queue.put(locator)

    @classmethod
    def _find_all_top_level_window(cls) -> List[auto.Control]:
        return auto.GetRootControl().GetChildren()

    def _focus_active_window(self, active_window: str) -> None:
        self._active_window = active_window
        windows = self._find_all_top_level_window()
        for window in windows:
            if hasattr(window, "Name") and window.Name == self._active_window:
                if hasattr(window, "SwitchToThisWindow"):
                    window.SwitchToThisWindow()
                if hasattr(window, "SetFocus"):
                    window.SetFocus()
                break
        else:
            self.logger.error("Could not focus window=%s", active_window)

    def listen(self, active_window: str):
        with auto.UIAutomationInitializerInThread(debug=True):
            self.logger.info(
                "Start listening for mouse click in window=%s", active_window
            )
            self._focus_active_window(active_window)
            locator = {}
            listener = Listener(on_click=self._on_click)
            try:
                listener.start()
                locator = self.queue.get(block=True, timeout=PICK_TIMEOUT)
            except Empty:
                self.logger.info("Locator selection timeout")
            finally:
                listener.stop()
        return locator

    def validate(self, window: str, value: str) -> MatchedWindowsLocators:
        self.logger.info("Validate=%s, %s", window, value)
        with auto.UIAutomationInitializerInThread(debug=True):
            locators: MatchedWindowsLocators = {"matches": []}
            self._focus_active_window(window)
            root = self._windows_elements.get_element(f"name:{window}")
            element = self._windows_elements.get_element(value, 8, root)
            if element and hasattr(element, "name") and hasattr(element, "locator"):
                locators["matches"].append(
                    {
                        "window": window,
                        "name": element.name,
                        "value": element.locator,
                        "version": LOCATOR_VERSION,
                        "screenshot": Rectangle.from_element(element).get_screenshot(),
                    }
                )
        return locators

    def list_windows(self, exclude_titles=None) -> OpenWindows:
        self.logger.info("Get window info")
        with auto.UIAutomationInitializerInThread(debug=True):
            exclude_titles = exclude_titles or []
            windows = []
            try:
                windows = self._windows_elements.list_windows(icons=True)
            except TypeError as err:
                # If windows is closed while listing the windows library
                # will raise an exception.
                # The fix need to be done in the windows library side,
                # but will add this catch here until the fix is done
                self.logger.error("Failed to list windows: %s", str(err))
            returned_windows = []
            for window in windows:
                win = {"title": window["title"]}
                if window["icon"]:
                    win["icon"] = window["icon"]
                if win["title"] and win["title"] not in exclude_titles:
                    returned_windows.append(win)
        return returned_windows

    def _draw_borders(self, rect: Rectangle, color: win32api.RGB, thickness: int = 5):
        try:
            full_screen_context = win32gui.GetDC(0)
            brush = win32gui.CreateSolidBrush(color)
            win32gui.SelectObject(full_screen_context, brush)
            frames = rect.get_borders(thickness)
            for frame in frames:
                win32gui.FrameRect(full_screen_context, frame, brush)
        except AttributeError as error:
            self.logger.error("Could not draw border=%s", error)

    def focus(self, window: str, locator: str) -> None:
        self.logger.info("Focus element=%s in window=%s", locator, window)
        with auto.UIAutomationInitializerInThread(debug=True):
            self._focus_active_window(window)
            root = self._windows_elements.get_element(f"name:{window}")
            element = self._windows_elements.get_element(locator, 8, root)
            rect = Rectangle.from_element(element)
            self._draw_borders(rect, COLOR_RED)
