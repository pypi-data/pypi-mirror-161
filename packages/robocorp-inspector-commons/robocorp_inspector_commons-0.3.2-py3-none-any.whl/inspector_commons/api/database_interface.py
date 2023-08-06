from pathlib import Path
from typing import Optional

from inspector_commons.database import Database


class DatabaseConnector(Database):
    def __init__(
        self, path: Optional[str] = None, load_on_start: Optional[bool] = None
    ):
        super().__init__(path, load_on_start)

    def is_same_path(self, path):
        return Path(path).samefile(Path(self.path))
