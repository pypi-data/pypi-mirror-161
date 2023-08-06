from __future__ import annotations

import argparse
from typing import Any


def boolean(arg: bool | str) -> bool:
    arg = str(arg)
    if arg.lower() not in {"true", "false"} or not isinstance((eval(arg)), bool):
        raise argparse.ArgumentTypeError(f"{arg.strip()} (expected bool)")
    return eval(arg)


def list_bool(arg: str) -> list[bool]:
    return _list_type(arg, bool)


def list_dict(arg: str) -> list[dict]:
    return _list_type(arg, dict)


def list_float(arg: str) -> list[int]:
    return _list_type(arg, float)


def list_int(arg: str) -> list[int]:
    return _list_type(arg, int)


def list_str(arg: str) -> list[str]:
    return _list_type(arg, str)


def _list_type(arg: str, type: type) -> list[Any]:
    """
    `arg` is a stringified list.
    """
    arg = eval(str(arg))
    if not isinstance(arg, list):
        raise argparse.ArgumentTypeError(f"{str(arg).strip()} (expected list)")
    for item in arg:
        if not isinstance(item, type):
            raise argparse.ArgumentTypeError(f"{item.strip()} (expected {type.__name__})")
    return arg
