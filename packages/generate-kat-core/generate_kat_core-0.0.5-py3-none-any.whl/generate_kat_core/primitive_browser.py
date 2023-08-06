import os
from pathlib import Path


class PrimitiveBrowser:
    def __init__(self, initial_search_path: str) -> None:
        self.initial_search_path = initial_search_path

    def list(self) -> list[str]:
        f: Path
        subfolder_names = [f.name for f in os.scandir(self.initial_search_path) if f.is_dir()]

        def function(x: str) -> bool:
            return not (x.startswith('lib') or x.startswith('__'))

        return list(filter(function, subfolder_names))
