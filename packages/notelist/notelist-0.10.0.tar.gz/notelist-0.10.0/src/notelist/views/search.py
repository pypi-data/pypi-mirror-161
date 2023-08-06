"""Search view module."""

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt

from notelist.schemas.search import SearchSchema
from notelist.schemas.notebooks import NotebookSchema
from notelist.schemas.notes import NoteSchema
from notelist.db import get_main_db
from notelist.responses import OK, get_response_data


# Messages
RETRIEVED_1 = "1 item retrieved"
RETRIEVED_N = "{} items retrieved"

# Schemas
search_schema = SearchSchema()
nb_get_list_schema = NotebookSchema(many=True, exclude=["user_id"])
note_get_list_schema = NoteSchema(many=True, exclude=["body"])

# Blueprint object
bp = Blueprint("search", __name__)


def _select_note(n: dict, search: str) -> bool:
    """Return whether a note document is selected or not.

    :param n: Note document.
    :param search: Search text.
    :return: `True` if `n` is selected or `False` otherwise.
    """
    k1 = "title"
    k2 = "body"
    k3 = "tags"

    return (
        (k1 in n and search in n[k1].lower()) or
        (k2 in n and search in n[k2].lower()) or
        (k3 in n and any(map(lambda t: search in t.lower(), n[k3])))
    )


@bp.route("/<search>", methods=["GET"])
@jwt_required()
def search(search: str) -> tuple[dict, int]:
    """Get all the notebooks and notes of the request user that match a text.

    This operation requires the following header with an access token:
        "Authorization: Bearer access_token"

    Request parameters:
        - search (string): Search text.

    Response status codes:
        - 200 (Success)
        - 400 (Bad Request)
        - 401 (Unauthorized)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.
        - result (object): Data of the notebooks, tags and notes found.

    :param search: Search text.
    :return: Tuple containing the response data and the response status code.
    """
    # Validate the search text. A "marshmallow.ValidationError" exception is
    # raised if the text is invalid, which produces a 400 response.
    search = search_schema.load({"search": search})["search"].lower()

    # JWT payload data
    req_user_id = get_jwt()["user_id"]

    # Notebooks
    db = get_main_db()
    notebooks = db.notebooks.get_by_user(req_user_id)
    res_notebooks = [n for n in notebooks if search in n["name"].lower()]

    # Notes
    res_notes = []

    for n in notebooks:
        notes = db.notes.get_by_filter(n["id"])
        notes = list(filter(lambda n: _select_note(n, search), notes))

        res_notes.extend(notes)

    result = {
        "notebooks": nb_get_list_schema.dump(res_notebooks),
        "notes": note_get_list_schema.dump(res_notes)
    }

    c = len(res_notebooks) + len(res_notes)
    m = RETRIEVED_1 if c == 1 else RETRIEVED_N.format(c)

    return get_response_data(m, OK, result), 200
