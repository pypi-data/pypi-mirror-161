"""Note schemas module."""

from datetime import datetime

from marshmallow import Schema, pre_load, post_load, pre_dump, ValidationError
from marshmallow.fields import Str, Bool, DateTime, List
from marshmallow.validate import Length, Regexp

from notelist.tools import get_uuid


class NoteSchema(Schema):
    """Note schema."""

    class Meta:
        """Note schema meta class."""

        ordered = True

    id = Str(
        validate=Regexp(r"[a-z0-9]{32}$"),
        missing=get_uuid
    )

    notebook_id = Str(
        validate=Regexp(r"[a-z0-9]{32}$"),
        required=True,
        error_messages={"required": "Field is required."}
    )

    archived = Bool(missing=False)
    title = Str(validate=Length(max=200))
    body = Str(validate=Length(max=10000000))
    tags = List(Str(validate=Length(min=1, max=200)))
    created = DateTime(missing=datetime.now)
    last_modified = DateTime(missing=datetime.now)

    @pre_load
    def preload(self, data: dict, **kwargs) -> dict:
        """Pre-process data before being deserialized/loaded.

        :param data: Initial data.
        :param kwargs: Options.
        :return: Final data.
        """
        k1 = "title"
        k2 = "tags"

        if k1 in data and type(data[k1]) == str:
            data[k1] = data[k1].strip()

        if k2 in data and type(data[k2]) == list:
            data[k2] = [i.strip() if type(i) == str else i for i in data[k2]]

            if any(map(lambda x: data[k2].count(x) > 1, data[k2])):
                raise ValidationError({k2: ["Field items must be unique."]})

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


class NoteFilterSchema(Schema):
    """Note filter schema."""

    class Meta:
        """Note schema meta class."""

        ordered = True

    archived = Bool(allow_none=True, missing=None)
    
    tags = List(
        Str(validate=Length(min=1, max=200)),
        allow_none=True,
        missing=None
    )

    no_tags = Bool(missing=False)
    last_mod = Bool(missing=True)
    asc = Bool(missing=True)

    @pre_load
    def preload(self, data: dict, **kwargs) -> dict:
        """Pre-process data before being deserialized/loaded.

        :param data: Initial data.
        :param kwargs: Options.
        :return: Final data.
        """
        k = "tags"

        if k in data and type(data[k]) == list:
            data[k] = [i.strip() if type(i) == str else i for i in data[k]]

            if any(map(lambda x: data[k].count(x) > 1, data[k])):
                raise ValidationError({k: ["Field items must be unique."]})

        return data
