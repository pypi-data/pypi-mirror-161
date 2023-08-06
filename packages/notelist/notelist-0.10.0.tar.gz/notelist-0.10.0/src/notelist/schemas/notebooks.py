"""Notebook schemas module."""

from datetime import datetime

from marshmallow import Schema, pre_load, post_load, pre_dump
from marshmallow.fields import Str, DateTime, Dict
from marshmallow.validate import Length, Regexp

from notelist.tools import get_uuid


class NotebookSchema(Schema):
    """Notebook schema."""

    class Meta:
        """Notebook schema meta class."""

        ordered = True

    id = Str(
        validate=Regexp(r"[a-z0-9]{32}$"),
        missing=get_uuid
    )

    user_id = Str(
        validate=Regexp(r"[a-z0-9]{32}$"),
        required=True,
        error_messages={"required": "Field is required."}
    )

    name = Str(
        validate=Length(min=2, max=200),
        required=True,
        error_messages={"required": "Field is required."}
    )

    tag_colors = Dict(
        Str(validate=Length(min=1, max=200)),
        Str(validate=Regexp(r"[#]?[a-fA-F0-9]{6}"))
    )

    created = DateTime(missing=datetime.now)
    last_modified = DateTime(missing=datetime.now)

    @pre_load
    def preload(self, data: dict, **kwargs) -> dict:
        """Pre-process data before being deserialized/loaded.

        :param data: Initial data.
        :param kwargs: Options.
        :return: Final data.
        """
        k1 = "name"
        k2 = "tag_colors"

        if k1 in data and type(data[k1]) == str:
            data[k1] = data[k1].strip()

        if k2 in data and type(data[k2]) == dict:
            data[k2] = {
                i.strip() if type(i) == str else i: v
                for i, v in data[k2].items()}

        return data

    @post_load
    def postload(self, data: dict, **kwargs) -> dict:
        """Post-process data after being deserialized/loaded.

        :param data: Initial data.
        :param kwargs: Options.
        :return: Final data.
        """
        for k in ("created", "last_modified"):
            if k in data:
                data[k] = data[k].isoformat(timespec="seconds")

        return data

    @pre_dump
    def predump(self, data: dict, **kwargs) -> dict:
        """Pre-process data before being serialized/dumped.

        :param data: Initial data.
        :param kwargs: Options.
        :return: Final data.
        """
        for k in ("created", "last_modified"):
            if k in data:
                data[k] = datetime.fromisoformat(data[k])

        return data
