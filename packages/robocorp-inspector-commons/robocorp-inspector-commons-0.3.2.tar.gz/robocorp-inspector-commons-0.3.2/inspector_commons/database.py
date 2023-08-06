# pylint: disable=cell-var-from-loop
import base64
import logging
import os
from pathlib import Path
from threading import Lock
from typing import Dict, Optional

from RPA.core.locators import ImageTemplate  # type: ignore
from RPA.core.locators import (BrowserDOM, Locator, LocatorsDatabase,
                               sanitize_name)


class DatabaseError(Exception):
    """Common exception for Inspector's database errors."""


class Database:
    """Common interface for locators database."""

    def __init__(
        self, path: Optional[str] = None, load_on_start: Optional[bool] = None
    ):
        self.logger = logging.getLogger(__name__)
        self.cache: Dict[str, Dict] = {}
        self.lock = Lock()

        path = str(Path(path)) if path is not None else path
        self.database = LocatorsDatabase(path)
        if load_on_start:
            self.load()
            if self.error:
                self.logger.warning(*self.error)

    @property
    def path(self):
        return self.database.path

    @property
    def error(self):
        return self.database.error

    @property
    def names(self):
        return list(sorted(self.database.locators.keys()))

    def _create_cache(self):
        locators: Dict[str, Dict] = {
            name: locator.to_dict() for name, locator in self.database.locators.items()
        }

        def load_image(path) -> Optional[str]:
            root = Path(self.database.path).parent
            try:
                with open(root / path, "rb") as infile:
                    return base64.b64encode(infile.read()).decode()
            except FileNotFoundError:
                self.logger.warning("Failed to read image: %s", path)
                return ""

        for locator in locators.values():
            if locator["type"] == "browser" and locator.get("screenshot"):
                locator["screenshot"] = load_image(locator["screenshot"])
            elif locator["type"] == "image":
                locator["value"] = load_image(locator["path"])

        self.cache = locators

    def get(self, name):
        if name not in self.database.locators:
            raise KeyError(f"No locator with name: {name}")

        return self.cache[name]

    def pop(self, name):
        if name not in self.database.locators:
            raise KeyError(f"No locator with name: {name}")

        del self.database.locators[name]
        return self.cache.pop(name)

    def load(self):
        self.database.load()
        self._create_cache()

    def save(self):
        # Filter out stored source images, if they exist
        root = Path(self.database.path).parent
        for locator in self.database.locators.values():
            if not isinstance(locator, ImageTemplate):
                continue
            if not getattr(locator, "source", None):
                continue
            try:
                Path(root / str(locator.source)).unlink()
                self.logger.info("Removed source image: %s", locator.source)
                locator.source = None
            except FileNotFoundError:
                pass

        self.database.save()
        self._create_cache()

    def list(self):
        """Convert current database to JSON."""
        if self.database.error:
            message = self.database.error[0] % self.database.error[1]
            raise DatabaseError(message)

        return self.cache

    def update(self, name, fields):
        """Update locator entries."""
        if not name.strip():
            raise DatabaseError("Empty/missing locator name")

        stored = self.database.locators.get(name, {})
        cached = self.cache.get(name, {})

        def required(src, dst=None):
            dst = dst or src
            path = getattr(stored, dst, None)
            if fields[src] != cached.get(src):
                fields[dst] = self._save_image(name, dst, fields[src], path)
            else:
                fields[dst] = path

        def optional(src, dst=None):
            dst = dst or src
            val = fields.get(src)
            path = getattr(stored, dst, None)
            if val:
                if val != cached.get(src):
                    fields[dst] = self._save_image(name, dst, val, path)
                else:
                    fields[dst] = path
            elif path:
                try:
                    Path(path).unlink()
                except FileNotFoundError:
                    pass

        if fields["type"] == "browser":
            optional("screenshot")
        elif fields["type"] == "image":
            required("value", "path")

        try:
            self.database.locators[name] = Locator.from_dict(fields)
        except ValueError as err:
            raise DatabaseError from err

        self.save()
        return self.list()

    def delete(self, name):
        """Delete locator entries."""
        if name not in self.database.locators:
            raise DatabaseError(f"Unknown locator: {name}")

        locator = self.database.locators.pop(name)

        def remove(key):
            path = getattr(locator, key, None)
            if not path:
                return
            try:
                Path(path).unlink()
            except FileNotFoundError:
                pass

        if isinstance(locator, BrowserDOM):
            remove("screenshot")
        elif isinstance(locator, ImageTemplate):
            remove("path")

        self.save()
        return self.list()

    def _save_image(self, name, field, content, path=None):
        """Save base64 image into a file."""
        root = Path(self.database.path).parent
        images = root / ".images"

        if path is not None and str(path).strip():
            path = root / path
        else:
            path = images / f"{sanitize_name(name)}-{field}.png"

        data = base64.b64decode(content)

        os.makedirs(images, exist_ok=True)
        with open(path, "wb") as outfile:
            outfile.write(data)

        return str(path.relative_to(root))
