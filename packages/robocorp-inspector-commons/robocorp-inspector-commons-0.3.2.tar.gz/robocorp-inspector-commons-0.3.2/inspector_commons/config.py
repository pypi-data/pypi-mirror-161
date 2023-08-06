from pathlib import Path

from inspector_commons.utils import robocorp_home

_UNSET = object()

HOME = robocorp_home() / "inspector"
PATHS = [Path.cwd() / "inspector.yaml", HOME / "inspector.yaml"]


class Config:
    def __init__(self):
        # TODO: Convert to TypedDict
        self._values = {}
        self.set("home", HOME)

    def get(self, key, default=_UNSET):
        if default is not _UNSET:
            return self._values.get(key, default)

        try:
            return self._values[key]
        except KeyError as err:
            raise KeyError(f"Undefined configuration key: {key}") from err

    def set(self, key, value):
        self._values[key] = value

    def load(self):
        # TODO: Load possible configuration from PATHS
        raise NotImplementedError

    def save(self):
        raise NotImplementedError
