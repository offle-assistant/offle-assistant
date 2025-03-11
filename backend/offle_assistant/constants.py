import os
import pathlib

import appdirs


OFFLE_ENV = os.getenv("OFFLE_ENV", "development")

__all__ = [
    "OFFLE_ENV",
]


def get_cache_dir():
    cache_dir = pathlib.Path(
        appdirs.user_cache_dir("offle-assistant", "offle-org")
    )
    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir


CACHE_DIR = get_cache_dir()
