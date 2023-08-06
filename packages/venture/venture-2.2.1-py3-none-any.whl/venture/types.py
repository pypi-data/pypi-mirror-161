# pylint: disable=inherit-non-class
from __future__ import annotations
from typing import List, Union, TypedDict, Optional
from enum import Enum


class OpenContext(Enum):
    BROWSE = "Browse"
    QUICK_LAUNCH = "QuickLaunch"


class BaseSub(TypedDict):
    base: str
    subs: list[str]


DirectorySchema = List[Union[str, BaseSub]]


class QuickLaunchEntry(TypedDict):
    path: str
    icon: str
    tags: Optional[list[str]]
