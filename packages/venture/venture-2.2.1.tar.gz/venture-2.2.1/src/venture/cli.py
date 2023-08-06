# from __future__ import annotations
import time
import subprocess
import os
from typing import Any

import yaml
import arc
from arc.color import fg, effects
from arc.logging import logger

# pylint: disable=wrong-import-position
from .browse_list import BrowseList, BrowseItem
from .ui import get_ui_provider
from .ui.ui_provider import T, V
from . import util
from .tags import get_tags
from .config import config, Config, CONFIG_FILE
from .types import OpenContext
from .icons import icon_map

DEBUG = False
cache = util.Cache(config)
start = time.time()


def pick(items: T, pick_config: Config, open_context: OpenContext) -> V:
    provider_type = get_ui_provider(pick_config.ui, open_context)
    provider = provider_type(items, config)
    logger.debug("Time to render: %s", time.time() - start)
    choice = provider.run()
    if not choice:
        raise arc.ExecutionError("No Valid Option Picked")

    return choice


def execute(path: str, open_context: OpenContext):
    exec_str = config.get_exec(open_context)
    command = exec_str.format(path=util.resolve(path))
    logger.debug("Executing %s", command)
    if not DEBUG:
        subprocess.run(command, check=True, shell=True)


def get_items() -> dict[str, BrowseItem]:
    if cache.exists() and config.browse.use_cache:
        items = cache.read()
        if cache.valid():
            return items

    browser = BrowseList(config.browse.entries)
    browser.discover()
    items = browser.items
    if config.browse.use_cache:
        cache.write(browser.items)

    return items


cli = arc.namespace(name="venture")


@cli.subcommand()
def run():
    """Open the venture selection menu"""
    items = get_items()
    # The method to add the QuickLaunch to the Menu
    # is a little hacky.
    quick_launch_choice = "quicklaunch"
    if config.browse.show_quicklaunch:
        items = {
            "QuickLaunch": {"path": quick_launch_choice, "icon": icon_map["hamburger"]},
            **items,
        }

    if DEBUG:
        for key, value in items.items():
            print(f"{key:<20} : {value}")

    choice: str = pick(items, config, OpenContext.BROWSE)
    if choice == quick_launch_choice:
        cli(quick_launch_choice)
    else:
        execute(choice, OpenContext.BROWSE)


@cli.subcommand()
def dump(force: bool = False):
    """Dump Default Config to ~/.config/venture.yaml if it does not exist"""
    if config.exists() and not force:
        raise arc.ExecutionError(
            "Configuration already exists. Run again with --force to overwrite"
        )
    config.write(default=True)


@cli.subcommand()
def quicklaunch():
    """Open the Quick Launch Menu"""
    choice = pick(config.quicklaunch.entries, config, OpenContext.QUICK_LAUNCH)
    execute(choice["path"], OpenContext.QUICK_LAUNCH)


@quicklaunch.subcommand("list")
def list_quicklaunch():
    """List quick-launch entries"""
    if len(config.quicklaunch.entries) == 0:
        print(
            "No quick-launch items, add one with "
            f"{fg.GREEN}quicklaunch:add{effects.CLEAR}"
        )
        return

    print("Quicklaunch Items:")
    for name, values in config.quicklaunch.entries.items():
        print(f"- {values['icon']}  {name} {fg.GREY}({values['path']}){effects.CLEAR}")


DOT = "\uf192"


@quicklaunch.subcommand()
def add(
    *,
    name: str = arc.Option(short="n"),
    path: str = arc.Option(short="p"),
    icon: str = arc.Option(short="i", default=DOT),
    tags: list[str] = arc.Option(short="t", default=[]),
    no_default_tags: bool = arc.Flag(short="d"),
    icon_only: bool = False,
):
    """\
    Add a new quick-launch entry

    # Arguments
    name: Display name for the quick-launch entry
    path: File path to launch when the entry is picked
    icon: Icon to display along with the name, optional
    tags: Comma-seperated values to tag the entry with.
            Will be displayed along with the name of the
            entry. Icon substitution available.
    no-default-tags: Disable the generation of default tags for this
                     quick-launch entry
    icon-only: Automatic tag-generation will display icon-only rather
               than icon + name
    """

    if not os.path.exists(util.resolve(path)):
        raise arc.ExecutionError(
            f"The path {fg.YELLOW}{path}{effects.CLEAR} {fg.RED}doesn't exist"
        )

    all_tags = get_tags(
        path,
        tags,
        icon_only,
        no_default_tags,
    )

    config.quicklaunch.entries[name] = {
        "path": path,
        "icon": icon,
        "tags": list(all_tags),
    }
    config.write()

    print(f"{fg.GREEN}{name} Added!{effects.CLEAR}")


@quicklaunch.subcommand()
def remove(name: str):
    """Remove a quick-launch entry"""
    if name not in config.quicklaunch.entries:
        raise arc.ExecutionError(f"{name} is not a quick-launch entry")

    config.quicklaunch.entries.pop(name)
    config.write()
    print(f"{fg.GREEN}{name} Removed!{effects.CLEAR}")


@cli.subcommand("cache")
def cache_command(enable: bool = False, disable: bool = False):
    """Interact with the Venture cache.
    If no arguments are provided, will display the current state of the cache

    The cache stores the data generated to display the main listing.
    For most reasonably sized outputs, the cache isn't necessary, but
    can still speed things up (if only by a fraction of a second). If
    you find running refresh to be annoying, try disabling it and review
    your performance.

    # Arguments
    enable:  enables the cache
    disable: disables the cache
    """
    if all((enable, disable)):
        print("Cannot enable and disable the cache at the same time!")

    elif enable:
        config.browse.use_cache = True
        config.write()
        print("Cache Enabled")

    elif disable:
        config.browse.use_cache = False
        config.write()
        print("Cache Disabled")

    else:
        cache.read()
        green = lambda string: fg.GREEN + string + effects.CLEAR
        red = lambda string: fg.RED + string + effects.CLEAR
        print(
            "Cache is "
            + (green("enabled") if config.browse.use_cache else red("disabled"))
        )
        print("Cache is " + (green("present") if cache.exists() else red("empty")))
        print("Cache is " + (green("valid") if cache.valid() else red("invalid")))


@cache_command.subcommand()
def refresh():
    """Refreshes the contents of the cache"""
    browse = BrowseList(config.browse.entries)
    browse.discover()
    cache.write(browse.items)
    print("Cache Refreshed")


@cli.subcommand("update-config")
def update():
    """Checks if the config file needs to be updated"""
    with open(CONFIG_FILE, "r") as f:
        data: dict[str, Any] = yaml.load(f.read(), Loader=yaml.CLoader)

    if data.get("directories"):
        should_update = util.confirm(
            "Looks like you're using an old version of the "
            "config, would you like to update it?"
        )
        if should_update:
            updated = Config.update_config(data)
            updated.write()
            print("Config updated, you should be good to go!")
        else:
            print(
                "Ok, but until you update only ",
                "the default configuration will apply",
            )
    else:
        print("No updates needed!")
