"""User schemas module."""

from datetime import datetime

from marshmallow import Schema, pre_load, post_load, pre_dump
from marshmallow.fields import Str, Bool, Email, DateTime
from marshmallow.validate import Length, Regexp

from notelist.tools import get_uuid


class UserSchema(Schema):
    """User schema."""

    class Meta:
        """User schema meta class."""

        ordered = True

    id = Str(
        validate=Regexp(r"[a-z0-9]{32}$"),
        missing=get_uuid
    )

    username = Str(
        validate=Regexp(r"[a-zA-Z0-9]{2,200}$"),
        required=True,
        error_messages={"required": "Field is required."}
    )

    password = Str(
        validate=Regexp(r"[a-zA-Z0-9-_+*.,;=<>/\\|%&#@$(){}\[\]!?]{8,200}$"),
        required=True,
        error_messages={"required": "Field is required."}
    )

    admin = Bool(missing=False)
    enabled = Bool(missing=False)
    name = Str(validate=Length(min=2, max=200))
    email = Email(validate=Length(max=200))
    created = DateTime(missing=datetime.now)
    last_modified = DateTime(missing=datetime.now)

    @pre_load
    def preload(self, data: dict, **kwargs) -> dict:
        """Pre-process data before being deserialized/loaded.

        :param data: Initial data.
        :param kwargs: Options.
        :return: Final data.
        """
        k = "name"

        if k in data and type(data[k]) == str:
            data[k] = data[k].strip()

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
