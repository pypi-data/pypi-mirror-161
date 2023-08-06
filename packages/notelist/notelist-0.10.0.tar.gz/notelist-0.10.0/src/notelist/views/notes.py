"""Note views module."""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt

from notelist.schemas.notes import NoteSchema, NoteFilterSchema
from notelist.db import get_main_db

from notelist.responses import (
    USER_UNAUTHORIZED, OK, ERROR_UNAUTHORIZED_USER, get_response_data
)


# Messages
RETRIEVED_1 = "1 note retrieved"
RETRIEVED_N = "{} notes retrieved"
RETRIEVED = "Note retrieved"
CREATED = "Note created"
UPDATED = "Note updated"
DELETED = "Note deleted"

# Blueprint object
bp = Blueprint("notes", __name__)

# Schemas
filter_schema = NoteFilterSchema()
schema = NoteSchema()
set_schema = NoteSchema(exclude=["id", "created", "last_modified"])
get_list_schema = NoteSchema(many=True, exclude=["notebook_id", "body"])
id_schema = NoteSchema(only=["id"])


@bp.route("/notes/<notebook_id>", methods=["POST"])
@jwt_required()
def get_notes(notebook_id: str) -> tuple[dict, int]:
    """Get all the notes of a notebook that match a filter.

    The user can call this operation only for their own notebooks. This
    operation requires the following header with an access token:
        "Authorization: Bearer access_token"

    Request parameters:
        - notebook_id (string): Notebook ID.

    Request data (JSON string):
        - archived (boolean, optional): If `false`, only active (not archived)
            notes are returned. If `true`, only archived notes are returned. If
            this item is not present in the request data, then no filter by
            state is applied and all notes are returned regardless their state.

        - tags (list, optional): List of strings containing the tag names to
            filter the notes by. If this item is present in the request data,
            only notes than have any of these tags are returned in the result.
            If this item is not present in the request data, then no filter by
            tags is applied and all notes are returned regardless their tags.

        - no_tags (boolean, optional): This item applies only if the "tags"
            item is present in the request data too. If `true`, notes with no
            tags are returned as well. If `false` or if this item is not
            present in the request data, notes with no tags are not returned.

        - last_mod (boolean, optional): If `true`, returned notes are sorted by
            their Last Modified timestamp. If `false` or if this item is not
            present in the request data, the notes are sorted by their Created
            timestamp.

        - asc (boolean, optional): If `true` or if this item is not present in
            the request data, the order of the returned notes is ascending. If
            `false`, the order is descending.

    Response status codes:
        - 200 (Success)
        - 400 (Bad Request)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.
        - result (list): Notes data.

    :param notebook_id: Notebook ID.
    :return: Tuple containing the response data and the response status code.
    """
    # Validate the ID. A "marshmallow.ValidationError" exception is raised if
    # the ID is invalid, which produces a 400 response.
    notebook_id = id_schema.load({"id": notebook_id})["id"]

    # JWT payload data
    req_user_id = get_jwt()["user_id"]

    # Get notebook
    db = get_main_db()
    notebook = db.notebooks.get_by_id(notebook_id)

    # Check if the notebook exists and the permissions
    if notebook is None or req_user_id != notebook["user_id"]:
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    # Get the request data
    f = request.get_json() if request.data else {}

    # Validate the request data. A "marshmallow.ValidationError" exception is
    # raised if the data is invalid, which produces a 400 error response.
    f = filter_schema.load(f)

    # Get notes
    arc = f["archived"]
    tags = f["tags"]
    no_tags = f["no_tags"]
    lm = f["last_mod"]
    asc = f["asc"]

    notes = db.notes.get_by_filter(
        notebook_id, arc, tags, no_tags, lm, asc
    )

    c = len(notes)
    m = RETRIEVED_1 if c == 1 else RETRIEVED_N.format(c)

    notes = get_list_schema.dump(notes)
    return get_response_data(m, OK, notes), 200


@bp.route("/note/<note_id>", methods=["GET"])
@jwt_required()
def get_note(note_id: str) -> tuple[dict, int]:
    """Get an existing note's data.

    The user can call this operation only for their own notebooks' notes.
    This operation requires the following header with an access token:
        "Authorization: Bearer access_token"

    Request parameters:
        - note_id (string): Note ID.

    Response status codes:
        - 200 (Success)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.
        - result (object): Note data.

    :param note_id: Note ID.
    :return: Tuple containing the response data and the response status code.
    """
    # Validate the ID. A "marshmallow.ValidationError" exception is raised if
    # the ID is invalid, which produces a 400 response.
    note_id = id_schema.load({"id": note_id})["id"]

    # JWT payload data
    req_user_id = get_jwt()["user_id"]

    # Get note and notebook
    db = get_main_db()
    note = db.notes.get_by_id(note_id)

    if note is not None:
        notebook = db.notebooks.get_by_id(note["notebook_id"])
    else:
        notebook = None

    # Check that the note and the notebook exists and the permissions
    if note is None or notebook is None or req_user_id != notebook["user_id"]:
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    note = schema.dump(note)
    return get_response_data(RETRIEVED, OK, note), 200


@bp.route("/note", methods=["POST", "PUT"])
@jwt_required()
def create_note() -> tuple[dict, int]:
    """Create a new note.

    The user can call this operation only for their own notebooks. This
    operation requires the following header with an access token:
        "Authorization: Bearer access_token"

    Request data (JSON string):
        - notebook_id (string): Notebook ID.
        - archived (string, optional): Whether this note is archived (default)
          or not.
        - title (string, optional): Note title.
        - body (string, optional): Note body.
        - tags (list, optional): List of tags.

    Response status codes:
        - 201 (Success)
        - 400 (Bad Request)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.
        - result (object): Note ID.

    :return: Tuple containing the response data and the response status code.
    """
    # JWT payload data
    req_user_id = get_jwt()["user_id"]

    # Get the request data
    note = request.get_json() if request.data else {}

    # Validate the request data. A "marshmallow.ValidationError" exception is
    # raised if the data is invalid, which produces a 400 error response.
    note = set_schema.load(note)

    # Check that the notebook exists and the permissions
    db = get_main_db()
    notebook = db.notebooks.get_by_id(note["notebook_id"])

    if notebook is None or req_user_id != notebook["user_id"]:
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    # Load/deserialize the data with the standard schema to generate the values
    # of the ID, Created and Last Modified fields and process all the fields.
    note = schema.load(note)

    # Create note
    db.notes.put(note)
    result = {"id": note["id"]}

    return get_response_data(CREATED, OK, result), 201


@bp.route("/note/<note_id>", methods=["PUT"])
@jwt_required()
def update_note(note_id: str) -> tuple[dict, int]:
    """Update an existing note.

    The user can call this operation only for their own notebooks' notes
    and the notebook ID of the note cannot be changed. This operation
    requires the following header with an access token:
        "Authorization: Bearer access_token"

    Request parameters:
        - note_id (string): Note ID.

    Request data (JSON string):
        - archived (string, optional): Whether this note is archived (default)
          or not.
        - title (string, optional): Note title.
        - body (string, optional): Note body.
        - tags (list, optional): List of tags.

    Response status codes:
        - 200 (Success)
        - 400 (Bad Request)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.

    :param note_id: Note ID.
    :return: Tuple containing the response data and the response status code.
    """
    # Validate the ID. A "marshmallow.ValidationError" exception is raised if
    # the ID is invalid, which produces a 400 response.
    note_id = id_schema.load({"id": note_id})["id"]

    # JWT payload data
    req_user_id = get_jwt()["user_id"]

    # Get the request data
    note = request.get_json() if request.data else {}

    # Validate the request data. A "marshmallow.ValidationError" exception is
    # raised if the data is invalid, which produces a 400 error response.
    note = set_schema.load(note)

    # Get current note and notebook
    db = get_main_db()
    cu_note = db.notes.get_by_id(note_id)

    if cu_note is not None:
        cu_nb = db.notebooks.get_by_id(cu_note["notebook_id"])
    else:
        cu_nb = None

    # Get new notebook (it can be the same as the current one or not)
    nb = db.notebooks.get_by_id(note["notebook_id"])

    # Check that the current note, current notebook and new notebook exist and
    # the permissions.
    if (
        cu_note is None or
        cu_nb is None or
        req_user_id != cu_nb["user_id"] or
        nb is None or
        req_user_id != nb["user_id"]
    ):
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    # Keep the values of the ID and Created fields of the current note document
    for k in ("id", "created"):
        note[k] = cu_note[k]

    # Load/deserialize the data with the standard schema to generate the value
    # of the Last Modified field and process all the fields.
    note = schema.load(note)

    # Update note
    db.notes.put(note)

    return get_response_data(UPDATED, OK), 200


@bp.route("/note/<note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id: str) -> tuple[dict, int]:
    """Delete an existing note.

    The user can call this operation only for their own notebooks' notes.
    This operation requires the following header with an access token:
        "Authorization: Bearer access_token"

    Request parameters:
        - note_id (string): Note ID.

    Response status codes:
        - 200 (Success)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.

    :param note_id: Note ID.
    :return: Tuple containing the response data and the response status code.
    """
    # Validate the ID. A "marshmallow.ValidationError" exception is raised if
    # the ID is invalid, which produces a 400 response.
    note_id = id_schema.load({"id": note_id})["id"]

    # JWT payload data
    req_user_id = get_jwt()["user_id"]

    # Get note
    db = get_main_db()
    note = db.notes.get_by_id(note_id)

    # Get notebook
    if note is not None:
        notebook = db.notebooks.get_by_id(note["notebook_id"])
    else:
        notebook = None

    # Check that the note and the notebook exist and the permissions
    if note is None or notebook is None or req_user_id != notebook["user_id"]:
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    # Delete note
    db.notes.delete(note["id"])

    return get_response_data(DELETED, OK), 200
