# pylint: disable=too-many-instance-attributes
import base64
import json
import logging
import tkinter as tk  # type: ignore
import traceback
from io import BytesIO

import mss  # type: ignore
from PIL import Image, ImageTk  # type: ignore


class SnippingTool:
    def __init__(self, timeout=30):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.timeout = timeout

        #: Final result
        self.error = None
        self.result = None

        with mss.mss() as sct:
            # NB: Always uses the left-most monitor
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)

        #: Display dimensions
        self.width = monitor["width"]
        self.height = monitor["height"]

        self.logger.debug("Screen dimensions: %dx%d", self.width, self.height)
        self.logger.debug("Screenshot size: %dx%d", *screenshot.size)

        #: Desktop screenshot (as PIL.Image)
        self.screenshot_image = Image.frombytes(
            "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
        )

        #: Desktop screenshot (as PNG bytes)
        self.screenshot_bytes = mss.tools.to_png(screenshot.rgb, screenshot.size)

        #: Current snip coordinates
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

        #: Snipping outline rectangle
        self.outline = None

        # Root widget
        self.root = tk.Tk()
        self.root.configure(bg="#f0f0f0")

        # Bring window to full screen and top most level. For some reason this
        # overrideredirect toggling is required to make this work on macOS:
        # https://stackoverflow.com/a/42173885/6734941
        try:
            self.root.overrideredirect(True)
            self.root.overrideredirect(False)
        except Exception:  # pylint: disable=broad-except
            self.logger.warning(traceback.format_exc())

        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)

        # Create canvas for drawing content
        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            cursor="crosshair",
        )

        # Use screenshot as background, resized to fit screen in case of scaling
        self.background = ImageTk.PhotoImage(
            self.screenshot_image.resize((self.width, self.height), Image.LANCZOS)
        )

        self.canvas.create_image((0, 0), image=self.background, anchor="nw")
        self.canvas.pack()

        # Focus users input on the canvas
        # FIXME: Doesn't work at least on macOS
        self.canvas.focus()
        self.canvas.focus_force()

        # Connect the event handlers
        self.canvas.bind("<Escape>", self._on_escape)
        self.canvas.bind("<B1-Motion>", self._on_move)
        self.canvas.bind("<ButtonPress-1>", self._on_button_press)
        self.canvas.bind("<ButtonRelease-1>", self._on_button_release)

    def run(self):
        # self.logger.debug("Starting application")
        self.root.after(int(self.timeout * 1000), self._on_timeout)
        self.root.mainloop()

        if self.error:
            raise RuntimeError(self.error)

        return self.result

    def quit(self):
        self.root.quit()

    def _to_width(self, value):
        return max(min(value, self.width), 0)

    def _to_height(self, value):
        return max(min(value, self.width), 0)

    def _on_timeout(self, _):
        self.logger.warning("Timeout reached (%d seconds)", self.timeout)
        self.error = "Timeout reached"
        self.quit()

    def _on_escape(self, _):
        self.logger.warning("Aborted by user")
        self.error = "Aborted by user"
        self.quit()

    def _on_button_press(self, event):
        self.start_x = self.end_x = self._to_width(event.x)
        self.start_y = self.end_y = self._to_height(event.y)

        if not self.outline:
            self.outline = self.canvas.create_rectangle(
                self.start_x,
                self.start_y,
                self.end_x,
                self.end_y,
                outline="#1B97F3",
                stipple="gray12",
            )

    def _on_move(self, event):
        self.end_x = self._to_width(event.x)
        self.end_y = self._to_height(event.y)

        if self.outline:
            self.canvas.coords(
                self.outline, self.start_x, self.start_y, self.end_x, self.end_y
            )

    def _on_button_release(self, _):
        width, height = self.screenshot_image.size
        width_scale = width / self.root.winfo_width()
        height_scale = height / self.root.winfo_height()

        if width_scale != height_scale:
            # This might mean that the window is not truly fullscreen or
            # that the screenshot missed something
            self.logger.warning(
                "Uneven width/height scaling (%s / %s)", width_scale, height_scale
            )

        scale_factor = height_scale
        self.logger.debug("Calculated scale factor: %f", scale_factor)

        coordinates = (
            int(scale_factor * min(self.start_x, self.end_x)),
            int(scale_factor * min(self.start_y, self.end_y)),
            int(scale_factor * max(self.start_x, self.end_x)),
            int(scale_factor * max(self.start_y, self.end_y)),
        )

        self.logger.info("Snip coordinates: %s", coordinates)
        snip = self.screenshot_image.crop(coordinates)

        stream = BytesIO()
        snip.save(stream, format="png")
        snip_bytes = stream.getvalue()

        self.result = base64.b64encode(snip_bytes).decode()
        self.quit()


def main():
    log_datefmt = "%Y/%m/%d %H:%M:%S"
    log_format = "%(asctime)s.%(msecs)03d › %(levelname)s › %(name)s › %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=log_datefmt)

    # Reduce unwanted debug logging
    logging.getLogger("PIL").setLevel(logging.INFO)

    try:
        snipper = SnippingTool()
        result = snipper.run()
        output = {"image": str(result)}
    except Exception as err:  # pylint: disable=broad-except
        logging.debug(traceback.format_exc())
        output = {"error": str(err)}

    print(json.dumps(output), flush=True)


if __name__ == "__main__":
    main()
