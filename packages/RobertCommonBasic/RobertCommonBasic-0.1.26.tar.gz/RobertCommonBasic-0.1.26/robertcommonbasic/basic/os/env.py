import os

from typing import Optional


def get_env(key: str, default: Optional[str] = None):
    return os.getenv(key, default)


def set_env(key: str, value: str):
    os.environ[key] = value


def has_env(key: str) -> bool:
    if key in os.environ.keys():
        return True
    return False


def del_env(key: str):
    if has_env(key) is True:
        del os.environ[key]