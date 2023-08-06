from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Iterable


class ConfigNamespace:

    def __init__(self, args: argparse.Namespace) -> None:

        # update object namespace so arguments can be accessed as attributes
        self.__dict__.update(**vars(args))

        # save namespace as a class variable for inspection
        self.namespace = args


    def __getattr__(self, name: str) -> Any:

        if name not in self.namespace:

            # TODO: search all keys and show tree if it occurs elsewhere

            raise AttributeError(
                f"{name} not in namespace: {sorted(vars(self).keys())}",
            )

        return super().__getattribute__(name)


    def __repr__(self) -> str:
        return str(self.namespace)


class ConfigParser:
    """
    ArgumentParser wrapper for configuration files.
    """

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        """
        You must supply an ArgumentParser object that defines the arguments for your project using
        flagged arguments. Positional arguments will not work. If you want to make an argument
        required, use `parser.add_argument('--flag', required=True)`
        """
        self.parser = parser


    def parse_args(self, args: dict | str) -> ConfigNamespace:
        if not isinstance(eval(str(args)), dict):
            raise argparse.ArgumentTypeError(f"`args` must be a valid (stringified) dictionary. args={args}")
        return self._parse(self._dict_to_flagged_args(args))


    def parse_file(self, filename: Path | str, format: str | None = None) -> ConfigNamespace:
        filename = Path(filename)
        if not filename.exists():
            raise FileNotFoundError(filename)
        return self._parse(self._load(filename, format))


    def _parse(self, args: list[str]) -> ConfigNamespace:
        """
        Parse and validate types with ArgumentParser.
        """
        return ConfigNamespace(self.parser.parse_args(args))


    def _load(self, filename: Path, format: str | None) -> list[str]:

        if filename.suffix in {'.yaml', '.yml'} or format == 'yaml':
            import yaml
            with open(filename) as f:
                try:
                    derp = yaml.safe_load(f)
                except:
                    raise Exception
                return self._dict_to_flagged_args(derp) # yaml.safe_load(f))

        elif filename.suffix == '.json' or format == 'json':
            import json
            raise NotImplementedError(f"{filename.suffix} config files are not (yet) supported")

        elif filename.suffix in {'.cfg', '.ini'} or format in {'cfg', 'ini'}:
            import configparser
            pass

        elif filename.suffix == '.toml' or format == 'toml':
            import toml
            pass

        else:
            raise argparse.ArgumentTypeError(
                f"Unfamiliar format '{filename.suffix[1:]}'. Supported types: cfg, ini, json, toml, yaml",
            )


    def _dict_to_flagged_args(self, x: dict | str) -> list[str]:
        """
        Convert key-value pairs of stringified dict to a list of (--flagged) string arguments.
        """
        arg_dict = []
        for key, value in eval(str(x)).items():
            arg_dict.append(f"--{key}")
            arg_dict.append(str(value))
        return arg_dict


    @classmethod
    def merge(self, namespaces: Iterable[ConfigNamespace]) -> ConfigNamespace:
        raise NotImplementedError(f"Combining {self.__class__.__name__} is not (yet) supported")
