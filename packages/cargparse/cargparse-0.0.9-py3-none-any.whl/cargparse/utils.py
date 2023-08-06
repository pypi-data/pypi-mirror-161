from __future__ import annotations

import configparser
from pathlib import Path


def _dict_str_to_list_flagged(x: dict | str) -> list[str]:
    """
    Convert key-value pairs of (stringified) dict to a list of (--flagged) string arguments.
    """
    arg_dict = []
    for key, value in eval(str(x)).items():
        arg_dict.append(f"--{key}")
        arg_dict.append(str(value))
    return arg_dict


def _read_file(
    filename: Path | str,
    format: str | None = None,
    case_sensitive: bool | None = None,
    reader: configparser.ConfigParser | None = None,
) -> list[str]:
    """
    `format` takes priority if specified.
    """

    filename = Path(filename)
    valid_formats = {"cfg", "ini", "json", "toml", "yaml"}

    if format in {"cfg", "ini"} or (filename.suffix in {".cfg", ".ini"} and format not in valid_formats):
        config_dict_str = _read_ini(filename, case_sensitive, reader)

    elif format == "json" or (filename.suffix == ".json" and format not in valid_formats):
        config_dict_str = _read_json(filename)

    elif format == "toml" or (filename.suffix == ".toml" and format not in valid_formats):
        config_dict_str = _read_toml(filename)

    elif format == "yaml" or (filename.suffix == ".yaml" and format not in valid_formats):
        config_dict_str = _read_yaml(filename)

    else:
        format_type_msg = f"format: '{format}'" if format else f"type: '{filename.suffix[1:]}'"
        raise ValueError(f"Unfamiliar {format_type_msg}. Supported types: cfg/ini, json, toml, yaml")

    return _dict_str_to_list_flagged(config_dict_str)


def _read_ini(filename: Path, case_sensitive: bool = True, reader: configparser.ConfigParser | None = None) -> str:

    cparser = reader if reader else configparser.ConfigParser()

    if case_sensitive:
        cparser.optionxform = str  # type: ignore

    cparser.read(filename)

    return {section: dict(cparser.items(section)) for section in cparser.sections()}  # type: ignore


def _read_json(filename: Path) -> str:
    import json

    try:
        with open(filename) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"{e.__class__.__name__} in {filename.resolve()}\n{e}")
        exit(1)


def _read_toml(filename: Path) -> str:

    try:  # tomllib is built-in from Python 3.11; earlier versions use its predecessor tomli
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

    try:
        with open(filename, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"{e.__class__.__name__} in {filename.resolve()}\n{e}")
        exit(1)


def _read_yaml(filename: Path) -> str:
    import yaml

    try:
        with open(filename) as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"{e.__class__.__name__} in {filename.resolve()}\n{e}")
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark  # type: ignore[attr-defined]
            print(f"Error position: ({mark.line + 1}:{mark.column + 1})")
        exit(1)
