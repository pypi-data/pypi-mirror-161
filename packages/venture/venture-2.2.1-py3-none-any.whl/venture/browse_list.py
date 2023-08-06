from typing import TypedDict
from pathlib import Path
import functools
import os

from arc.color import fg, effects
from .types import DirectorySchema
from .config import config
from .icons import default, filetype_icon, Icon
from . import util

GLOB = "/*"
EXCLUDED_DIRS = (".git", "node_modules")
browse = config.browse


class BrowseItem(TypedDict):
    path: str
    icon: Icon


class PathError(Exception):
    ...


class BrowseList:
    def __init__(self, entries: DirectorySchema):
        self.entries = entries
        self.items: dict[str, BrowseItem] = {}

    def discover(self):
        for entry in self.entries:
            if isinstance(entry, str):
                # pylint: disable=no-value-for-parameter
                self.handle_single_path(entry)
            elif isinstance(entry, dict):
                self.handle_hierarchy(entry["base"], entry["subs"])

    def handle_single_path(self, directory: str, prefix: str = None):
        directory = util.resolve(directory)
        prefix = prefix or directory
        path = Path(directory)

        if path.as_posix().endswith(GLOB):
            self.handle_glob(path)

        elif not path.exists():
            raise PathError(f"{path} is not a valid file or directory")

        elif path.is_file():
            self.add_entry(path, prefix)

        elif path.is_dir():
            for sub in path.iterdir():
                self.add_entry(sub, prefix)

    def handle_hierarchy(self, base: str, subs: list[str]):
        paths = [f"{base}/{sub.strip('/')}" for sub in subs]
        # Quick hack to fix globbed paths not getting
        # matched in the below if
        removed_globs = [path.rstrip(GLOB) for path in paths]

        for path in os.listdir(base):
            abs_path = Path(base) / path
            if (
                abs_path.as_posix() not in removed_globs
            ) or browse.include_parent_folder:
                self.add_entry(abs_path, base)

        for path in paths:
            self.handle_single_path(path, base)

    def handle_glob(self, globbed_path: Path):
        path = Path(globbed_path.as_posix().removesuffix(GLOB))
        path_str = path.as_posix()
        subs = [
            entry.as_posix().removeprefix(path_str).removeprefix("/")
            for entry in path.iterdir()
            if (browse.show_hidden or not entry.name.startswith("."))
            and entry.name not in EXCLUDED_DIRS
        ]

        self.handle_hierarchy(path_str, subs)

    def add_entry(self, path: Path, prefix: str):
        if (path.name.startswith(".") and not browse.show_hidden) or (
            path.is_file() and not browse.show_files
        ):
            return

        name = self.get_unique_path(path, prefix)
        if path.is_file():
            icon = self.get_icon(path.suffix)
        else:
            icon = self.get_icon("directory")

        self.items[name] = {
            "path": path.as_posix(),
            "icon": icon,
        }

    def get_unique_path(self, path: Path, prefix: str):
        string = path.as_posix().removeprefix(prefix).lstrip("/")
        prefix_path = Path(prefix)

        # Generates the shortest path that is unique
        # given defined entry points
        parts_len = len(prefix_path.parts)
        selection_start = parts_len - 1
        while string in self.items:
            string = (
                "/".join(prefix_path.parts[selection_start:parts_len]) + "/" + string
            )

            if selection_start <= 0:
                raise PathError(
                    f"Was unable to create a unique name for {fg.YELLOW}{path}{effects.CLEAR} "
                    "this is likely because multiple entries contain the given path"
                )

            if string in self.items:
                selection_start -= 1

        return string

    @staticmethod
    @functools.lru_cache()
    def get_icon(filetype: str) -> Icon:
        """Returns the icon associated with a specific file type"""
        return filetype_icon(filetype.lstrip(".")) or default
