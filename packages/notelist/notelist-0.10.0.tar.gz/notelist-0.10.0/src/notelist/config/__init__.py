"""Configuration package."""

from os import environ
from os.path import dirname, join
import json
from typing import Any


# File paths
_dir = dirname(__file__)
_schema = join(_dir, "settings.json")


class SettingsManager:
    """Key-value settings manager.

    Each setting is stored as an environment variable where the key and value
    of the setting are the key and value of the environment variable.
    """

    def __init__(self):
        """Initialize the instance loading the setting schema."""
        with open(_schema) as f:
            self._schema = json.load(f)

    def get(self, key: str) -> Any:
        """Return the value of a setting.

        An exception is raised if the setting is not found or not set.

        :param key: Setting key.
        :return: Setting value.
        """
        # Schema
        s = self._schema.get(key)

        if s is None:
            return s

        _typ = s.get("type", "string")
        _def = s.get("default")

        # Environment variable
        val = environ.get(key, _def)

        try:
            if val is not None:
                if _typ == "integer":
                    val = int(val)
                elif _typ != "string":
                    raise Exception(f"'{_typ}' type not supported")
        except Exception as e:
            raise Exception(f"'{key}' setting error: {e}")

        return val
