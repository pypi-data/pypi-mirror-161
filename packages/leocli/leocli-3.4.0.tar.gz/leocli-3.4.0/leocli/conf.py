"""Configuration of leocli."""

import sys
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

import xdg
import yaml
from termcolor import cprint

if TYPE_CHECKING:
    from argparse import Namespace


class LeoConfig:
    SETTINGS_PATHES = (
        xdg.xdg_config_home() / "leocli/leocli.yaml",
        Path("/etc/leocli/leocli.yaml"),
    )

    DEFAULTS = {
        "lang": "en",
        "pager": "less -R -I -S -X",
        "use_emojis": False,
        "use_cache": True,
        "cache_dir": xdg.xdg_cache_home() / "leocli",
    }

    def __init__(self):
        self._path = self.SETTINGS_PATHES[0]

        for key, default_value in self.DEFAULTS.items():
            attr_name = f"_{key}"

            def getter(self, attr_name: str, default_value):
                return getattr(self, attr_name, default_value)

            def setter(self, value, attr_name: str):
                setattr(self, attr_name, value)

            def deleter(self, attr_name: str, default_value):
                setattr(self, attr_name, default_value)

            # set property
            setattr(
                self.__class__,
                key,
                property(
                    partial(getter, attr_name=attr_name, default_value=default_value),
                    partial(setter, attr_name=attr_name),
                    partial(deleter, attr_name=attr_name, default_value=default_value),
                ),
            )
            # set default value
            setattr(self, key, default_value)

        self.load()

    def load(self):
        for path in self.SETTINGS_PATHES:
            if path.is_file():
                self.load_file(path)

                break

    def load_file(self, path: Path):
        self._path = path
        with path.open("r") as file:
            data = yaml.safe_load(file) or {}

        if not isinstance(data, dict):
            cprint(
                f"Config file {self._path} seems to be corrupt. Ignoring.",
                color="red",
                file=sys.stderr,
            )

        for key, default_value in self.DEFAULTS.items():
            value = data.get(key, default_value)
            setattr(self, f"_{key}", value)

    def save(self):
        data = {}

        for key, default_value in self.DEFAULTS.items():
            value = getattr(self, f"_{key}")

            if value == default_value:
                continue
            data[key] = value

        if data:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("w") as file:
                yaml.safe_dump(data, file)
        elif self._path.is_file():
            self._path.unlink()

    def update_from_args(self, args: "Namespace"):
        for key in self.DEFAULTS.keys():
            if getattr(args, key, None) is not None:
                setattr(self, key, getattr(args, key))

        self.save()
