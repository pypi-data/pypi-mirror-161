import os
from typing import Any, Optional
import hashlib
import logging

import yaml
from pydantic import BaseModel

from .types import DirectorySchema, QuickLaunchEntry
from . import util
from .types import OpenContext

logger = logging.getLogger("arc_logger")


CONFIG_FILE = os.getenv("VENTURE_CONFIG") or util.resolve("~/.config/venture.yaml")


class BrowseConfig(BaseModel):
    exec: str = ""
    use_cache: bool = True
    show_files: bool = True
    show_hidden: bool = False
    show_icons: bool = True
    include_parent_folder: bool = True
    entries: DirectorySchema = ["~"]
    show_quicklaunch: bool = False


class QuickLaunchConfig(BaseModel):
    exec: str = ""
    show_filepath: bool = False
    entries: dict[str, QuickLaunchEntry] = {}


class Config(BaseModel):
    checksum: Optional[str] = None
    exec: str = "code -r {path}"
    args: dict[str, str] = {}
    ui: str = "rofi"
    browse: BrowseConfig = BrowseConfig()
    quicklaunch: QuickLaunchConfig = QuickLaunchConfig()
    color_icons: bool = True

    def get_exec(self, open_context: OpenContext = None):
        if open_context is OpenContext.BROWSE:
            exec_str = self.browse.exec
        elif open_context is OpenContext.QUICK_LAUNCH:
            exec_str = self.quicklaunch.exec
        else:
            return self.exec

        if not exec_str:
            return self.exec

        return exec_str

    @classmethod
    def from_file(cls, file):
        with open(file) as f:
            contents = f.read()

        checksum = hashlib.md5(contents.encode("utf-8")).hexdigest()
        data: dict[str, Any] = yaml.load(contents, Loader=yaml.CLoader)
        return cls(checksum=checksum, **data)

    def write(self, default: bool = False):
        """Write Configuration to file in yaml format"""
        if default:
            data = Config().dict(exclude={"checksum"})
        else:
            data = self.dict(exclude={"checksum"})

        with util.safe_write(CONFIG_FILE) as f:
            f.write(yaml.dump(data, Dumper=yaml.CDumper))

    @staticmethod
    def exists() -> bool:
        return os.path.exists(CONFIG_FILE)

    @classmethod
    def update_config(cls, data: dict[str, Any]) -> "Config":
        """Given the old config data structure, updates it to match the new design"""
        default = cls()
        return cls(
            **{
                "ui": data.get("ui_provider", default.ui),
                "args": data.get(data.get("ui_provider", default.ui), {}),
                "exec": data.get("exec", default.exec),
                "browse": {
                    "exec": default.browse.exec,
                    "use_cache": data.get("use_cache", default.browse.use_cache),
                    "show_files": data.get("show_files", default.browse.show_files),
                    "show_hidden": data.get("show_hidden", default.browse.show_hidden),
                    "show_icons": data.get("show_icons", default.browse.show_icons),
                    "include_parent_folder": data.get(
                        "include_parent_folder", default.browse.include_parent_folder
                    ),
                    "show_quicklaunch": data.get(
                        "show_quicklaunch_in_browse", default.browse.show_quicklaunch
                    ),
                    "entries": data.get("directories", default.browse.entries),
                },
                "quicklaunch": {
                    "exec": default.quicklaunch.exec,
                    "entries": data.get("quicklaunch", default.quicklaunch.entries),
                },
            }
        )


if os.path.isfile(CONFIG_FILE):
    logger.debug("Loading %s", CONFIG_FILE)
    config: Config = Config.from_file(CONFIG_FILE)
else:
    logger.debug("Config File not found, loading defaults")
    config = Config()
