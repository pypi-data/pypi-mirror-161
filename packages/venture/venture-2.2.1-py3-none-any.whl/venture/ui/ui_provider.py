from __future__ import annotations
from typing import Mapping, Any, TypeVar, Generic
from abc import ABC, abstractmethod

from ..config import Config


T = TypeVar("T")
V = TypeVar("V")


class UIProvider(Generic[T, V], ABC):
    def __init__(self, items: T, config: Config):
        self.items = items
        self.config = config
        self._display_items = self.format_items(items)

    @abstractmethod
    def run(self) -> V | None:
        """Run the UI Interface. Return the selected value"""

    def format_items(self, items: T) -> Mapping[str, str]:
        """Format the input items into a dictionary
        where the key will be displayed in the UI
        and the value should be returned to the caller
        """
        return {key: key for key in items}  # type: ignore

    def parse_output(self, output: Any) -> str:
        """Called post-execution, used to do any
        nessecary parsing of the chosen answer

        If no parsing is nessecary, there is no need
        to implement this method
        """
        return output
