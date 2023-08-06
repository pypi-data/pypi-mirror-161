"""Authentication schemas module."""

from marshmallow import Schema, pre_load
from marshmallow.fields import Str
from marshmallow.validate import Length


class LoginSchema(Schema):
    """Login schema."""

    class Meta:
        """Login schema meta class."""

        ordered = True

    username = Str(
        validate=Length(min=1),
        required=True,
        error_messages={"required": "Field is required"}
    )

    password = Str(
        validate=Length(min=1),
        required=True,
        error_messages={"required": "Field is required"}
    )

    @pre_load
    def pre_load(self, data: dict, **kwargs) -> dict:
        """Pre-process data before being deserialized/loaded.

        :param data: Initial data.
        :param kwargs: Options.
        :return: Final data.
        """
        for k in ("username", "password"):
            if k in data and type(data[k]) == str:
                data[k] = data[k].strip()

        return data
