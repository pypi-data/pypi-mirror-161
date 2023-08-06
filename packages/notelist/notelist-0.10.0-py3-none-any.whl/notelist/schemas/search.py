"""Search schemas module."""

from marshmallow import Schema
from marshmallow.fields import Str
from marshmallow.validate import Length


class SearchSchema(Schema):
    """Search schema."""

    search = Str(
        validate=Length(min=2, max=200),
        required=True,
        error_messages={"required": "Field is required."}
    )
