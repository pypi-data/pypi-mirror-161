import os
import functools
from typing import Any
from contextlib import contextmanager
import logging

import ujson

logger = logging.getLogger("arc_logger")


def resolve(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def pango_span(content, **kwargs):
    return (
        "<span "
        + " ".join(f'{key}="{value}"' for key, value in kwargs.items())
        + f">{content}</span>"
    )


def catch(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise Cache.CacheError(f"Cache {func.__name__} failed") from e

    return wrapper


class Cache:
    cache_path = resolve("~/.cache/venture-cache")

    class CacheError(Exception):
        ...

    def __init__(self, config):
        self.config = config
        self.meta: dict[str, Any] = {}
        self.data: dict[str, str] = {}

    @catch
    def read(self):
        logger.debug("Reading %s", self.cache_path)
        data: dict = self.attempt_load()
        self.meta = data.get("meta", {})
        self.data = data.get("data", {})
        return self.data

    @catch
    def write(self, data: dict):
        logger.debug("Writing %s", self.cache_path)
        self.data |= data
        self.meta["checksum"] = self.config.checksum
        to_dump = {"data": self.data, "meta": self.meta}
        with open(self.cache_path, "w") as f:
            f.write(ujson.dumps(to_dump, ensure_ascii=False))

    def attempt_load(self):
        try:
            with open(self.cache_path, "r") as f:
                return ujson.loads(f.read())
        except (ValueError, FileNotFoundError):
            return {}

    def valid(self):
        return self.exists() and self.config.checksum == self.meta.get("checksum")

    @classmethod
    def exists(cls):
        return os.path.isfile(cls.cache_path)


def confirm(message: str):
    result = {
        "y": True,
        "n": False,
    }
    print(f"{message} [Y/N]")
    while True:
        user_input = input("> ").lower()
        if user_input in result:
            return result[user_input]
        print("Not understood, please type 'y' or 'n'")


@contextmanager
def safe_write(file_name: str):
    """Save the contents of the file into memory, then
    yield the file object. If an error occurs, writes the contents
    back into the file.
    """
    with open(file_name, "r") as f:
        contents = f.read()

    file = open(file_name, "w")

    try:
        yield file
    except:
        file.write(contents)
        raise
    finally:
        file.close()
