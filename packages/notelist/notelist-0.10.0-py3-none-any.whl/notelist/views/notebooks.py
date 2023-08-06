"""Notebook views module."""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt

from notelist.schemas.notebooks import NotebookSchema
from notelist.db import get_main_db

from notelist.responses import (
    USER_UNAUTHORIZED, OK, ERROR_UNAUTHORIZED_USER, ERROR_ITEM_EXISTS,
    get_response_data
)


# Messages
RETRIEVED_1 = "1 notebook retrieved"
RETRIEVED_N = "{} notebooks retrieved"
RETRIEVED = "Notebook retrieved"
CREATED = "Notebook created"
EXISTS = "The user already has a notebook with the same name"
UPDATED = "Notebook updated"
DELETED = "Notebook deleted"

# Blueprint object
bp = Blueprint("notebooks", __name__)

# Schemas
schema = NotebookSchema()

set_schema = NotebookSchema(
    exclude=["id", "user_id", "created", "last_modified"]
)

get_list_schema = NotebookSchema(many=True, exclude=["user_id"])
get_schema = NotebookSchema(exclude=["user_id"])
id_schema = NotebookSchema(only=["id"])


@bp.route("/notebooks", methods=["GET"])
@jwt_required()
def get_notebooks() -> tuple[dict, int]:
    """Get all the notebooks of the request user.

    This operation requires the following header with an access token:
        "Authorization: Bearer access_token"

    Response status codes:
        - 200 (Success)
        - 401 (Unauthorized)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.
        - result (list): Notebooks data.

    :return: Tuple containing the response data and the response status code.
    """
    # JWT payload data
    req_user_id = get_jwt()["user_id"]

    # Get notebooks
    db = get_main_db()
    notebooks = db.notebooks.get_by_user(req_user_id)

    c = len(notebooks)
    m = RETRIEVED_1 if c == 1 else RETRIEVED_N.format(c)

    notebooks = get_list_schema.dump(notebooks)
    return get_response_data(m, OK, notebooks), 200


@bp.route("/notebook/<notebook_id>", methods=["GET"])
@jwt_required()
def get_notebook(notebook_id: str) -> tuple[dict, int]:
    """Get an existing notebook's data.

    The user can call this operation only for their own notebooks. This
    operation requires the following header with an access token:
        "Authorization: Bearer access_token"

    Request parameters:
        - notebook_id (string): Notebook ID.

    Response status codes:
        - 200 (Success)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.
        - result (object): Notebook data.

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

    # Check that the notebook exists and the permissions
    if notebook is None or req_user_id != notebook["user_id"]:
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    notebook = get_schema.dump(notebook)
    return get_response_data(RETRIEVED, OK, notebook), 200


@bp.route("/notebook", methods=["POST", "PUT"])
@jwt_required()
def create_notebook() -> tuple[dict, int]:
    """Create a new notebook.

    This operation requires the following header with an access token:
        "Authorization: Bearer access_token"

    Request data (JSON string):
        - user_id (string): User ID.
        - name (string): Notebook name.
        - tag_colors (dictionary): Tag-color dictionary.

    Response status codes:
        - 201 (Success)
        - 400 (Bad Request)
        - 401 (Unauthorized)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.
        - result (object): Notebook ID.

    :return: Tuple containing the response data and the response status code.
    """
    # JWT payload data
    req_user_id = get_jwt()["user_id"]

    # Get the request data
    notebook = request.get_json() if request.data else {}

    # Validate the request data. A "marshmallow.ValidationError" exception is
    # raised if the data is invalid, which produces a 400 error response.
    notebook = set_schema.load(notebook)

    # Check that the user doesn't have another notebook with the same name
    db = get_main_db()

    if db.notebooks.get_by_name(req_user_id, notebook["name"]):
        return get_response_data(EXISTS, ERROR_ITEM_EXISTS), 400

    # Add User ID
    notebook["user_id"] = req_user_id

    # Load/deserialize the data with the standard schema to generate the values
    # of the ID, Created and Last Modified fields and process all the fields.
    notebook = schema.load(notebook)

    # Create notebook
    db.notebooks.put(notebook)
    result = {"id": notebook["id"]}

    return get_response_data(CREATED, OK, result), 201


@bp.route("/notebook/<notebook_id>", methods=["PUT"])
@jwt_required()
def update_notebook(notebook_id: str) -> tuple[dict, int]:
    """Update an existing notebook.

    The user can call this operation only for their own notebooks. This
    operation requires the following header with an access token:
        "Authorization: Bearer access_token"

    Request parameters:
        - notebook_id (string): Notebook ID.

    Request data (JSON string):
        - name (string): Notebook name.
        - tag_colors (dictionary): Tag-color dictionary.

    Response status codes:
        - 200 (Success)
        - 400 (Bad Request)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.

    :param notebook_id: Notebook ID.
    :return: Tuple containing the response data and the response status code.
    """
    # Validate the ID. A "marshmallow.ValidationError" exception is raised if
    # the ID is invalid, which produces a 400 response.
    notebook_id = id_schema.load({"id": notebook_id})["id"]

    # JWT payload data
    req_user_id = get_jwt()["user_id"]

    # Get the request data
    notebook = request.get_json() if request.data else {}

    # Validate the request data. A "marshmallow.ValidationError" exception is
    # raised if the data is invalid, which produces a 400 error response.
    notebook = set_schema.load(notebook)

    # Get existing notebook
    db = get_main_db()
    cu_nb = db.notebooks.get_by_id(notebook_id)

    # Check that the notebook exists and the permissions
    if cu_nb is None or req_user_id != cu_nb["user_id"]:
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    # Check that the user doesn't have another notebook with the same name
    k = "name"
    cu_name = cu_nb[k]
    name = notebook[k]

    if name != cu_name and db.notebooks.get_by_name(req_user_id, name):
        return get_response_data(EXISTS, ERROR_ITEM_EXISTS), 400

    # Keep the values of the ID, User ID and Created fields of the current
    # notebook document.
    for k in ("id", "user_id", "created"):
        notebook[k] = cu_nb[k]

    # Load/deserialize the data with the standard schema to generate the value
    # of the Last Modified field and process all the fields.
    notebook = schema.load(notebook)

    # Update notebook
    db.notebooks.put(notebook)

    return get_response_data(UPDATED, OK), 200


@bp.route("/notebook/<notebook_id>", methods=["DELETE"])
@jwt_required(fresh=True)
def delete_notebook(notebook_id: str) -> tuple[dict, int]:
    """Delete an existing notebook.

    The user can call this operation only for their own notebooks. This
    operation requires the following header with a fresh access token:
        "Authorization: Bearer fresh_access_token"

    Request parameters:
        - notebook_id (string): Notebook ID.

    Response status codes:
        - 200 (Success)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.

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

    # Check that the notebook exists and the permissions
    if notebook is None or notebook["user_id"] != req_user_id:
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    # Delete notebook
    db.notebooks.delete(notebook_id)

    # Delete all notebook's notes
    for n in db.notes.get_by_filter(notebook_id):
        db.notes.delete(n["id"])

    return get_response_data(DELETED, OK), 200
