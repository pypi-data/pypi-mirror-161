import time
import uuid
from math import floor
from typing import Optional

from inspector_commons import __version__


# TODO: Change metrics into dataclasses(?)
# pylint: disable=too-few-public-methods
class Metric:
    """Baseclass for a metric."""

    INSTANCE_ID: Optional[str] = None
    KEY: str = "inspector."

    def __init__(self, value: str):
        self.timestamp = str(int(floor(time.time() * 1000)))
        self.type = "test.inspector.dev"
        self.key = Metric.KEY + "base"
        self.value = value

    def __str__(self):
        return (
            f"{{id: {self.instance_id}, "
            + f"timestamp: {self.timestamp}, "
            + f"type: {self.type}, "
            + f"key: {self.key}, "
            + f"value: {self.value}}}"
        )

    @property
    def instance_id(self):
        if Metric.INSTANCE_ID is None:
            Metric.INSTANCE_ID = str(uuid.uuid4())
        return Metric.INSTANCE_ID


class MetricStart(Metric):
    """Class for a Start metric entry."""

    def __init__(self):
        super().__init__(value=__version__)
        self.key = Metric.KEY + "start"
