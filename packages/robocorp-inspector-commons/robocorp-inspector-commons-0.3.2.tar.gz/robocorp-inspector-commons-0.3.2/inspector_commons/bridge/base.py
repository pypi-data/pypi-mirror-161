import logging
import traceback as tb
from abc import ABC
from functools import wraps
from typing import Callable


def traceback(method: Callable):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            self.logger.debug(f"{type(self).__name__}.{method.__name__}()")
            return method(self, *args, **kwargs)
        except Exception:  # pylint: disable=broad-except
            self.logger.exception(tb.format_exc())
            raise

    return wrapper


class Bridge(ABC):
    # pylint: disable=too-few-public-methods
    def __init__(self, context):
        self.logger = logging.getLogger(__name__)
        self._window = None  # Injected after window creation
        self.ctx = context

    @property
    def window(self):
        return self._window

    def set_window(self, window):
        self._window = window

    @traceback
    def close(self):
        if self.window:
            self.window.close()
