"""User views module."""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt

from notelist.schemas.users import UserSchema
from notelist.db import get_main_db
from notelist.tools import get_hash

from notelist.responses import (
    USER_UNAUTHORIZED, OK, ERROR_UNAUTHORIZED_USER, ERROR_ITEM_EXISTS,
    ERROR_ITEM_NOT_FOUND, get_response_data
)


# Messages
RETRIEVED_1 = "1 user retrieved"
RETRIEVED_N = "{} users retrieved"
RETRIEVED = "User retrieved"
NOT_FOUND = "User not found"
CREATED = "User created"
EXISTS = "A user with the same username already exists"
UPDATED = "User updated"
DELETED = "User deleted"

# Blueprint object
bp = Blueprint("users", __name__)

# Schemas
schema = UserSchema()
set_cre_schema = UserSchema(exclude=["id", "created", "last_modified"])
set_upd_adm_schema = UserSchema(
    exclude=["id", "created", "last_modified"], partial=["password"])
set_upd_reg_schema = UserSchema(
    exclude=["id", "username", "admin", "enabled", "created", "last_modified"],
    partial=["password"])
get_list_schema = UserSchema(many=True, exclude=["password"])
get_schema = UserSchema(exclude=["password"])
id_schema = UserSchema(only=["id"])


@bp.route("/users", methods=["GET"])
@jwt_required()
def get_users() -> tuple[dict, int]:
    """Get all existing users.

    This operation requires administrator permissions and the following header
    with an access token:
        "Authorization: Bearer access_token"

    Response status codes:
        - 200 (Success)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.
        - result (list): Users data.

    :return: Tuple containing the response data and the response status code.
    """
    # JWT payload data
    admin = get_jwt()["admin"]

    # Check permissions
    if not admin:
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    # Get users
    db = get_main_db()
    users = db.users.get_all()

    c = len(users)
    m = RETRIEVED_1 if c == 1 else RETRIEVED_N.format(c)

    users = get_list_schema.dump(users)
    return get_response_data(m, OK, users), 200


@bp.route("/user/<user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id: str) -> tuple[dict, int]:
    """Get an existing user's data.

    The user can call this operation only for their own data, unless they are
    an administrator. This operation requires the following header with an
    access token:
        "Authorization: Bearer access_token"

    Request parameters:
        - user_id (string): User ID.

    Response status codes:
        - 200 (Success)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 404 (Not Found)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.
        - result (object): User data.

    :param user_id: User ID.
    :return: Tuple containing the response data and the response status code.
    """
    # Validate the ID. A "marshmallow.ValidationError" exception is raised if
    # the data is invalid, which produces a 400 response.
    user_id = id_schema.load({"id": user_id})["id"]

    # JWT payload data
    jwt = get_jwt()
    req_user_id = jwt["user_id"]
    admin = jwt["admin"]

    # Check permissions
    if not admin and user_id != req_user_id:
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    # Get user
    db = get_main_db()
    user = db.users.get_by_id(user_id)

    # Check that the user exists
    if user is None:
        return get_response_data(NOT_FOUND, ERROR_ITEM_NOT_FOUND), 404

    user = get_schema.dump(user)
    return get_response_data(RETRIEVED, OK, user), 200


@bp.route("/user", methods=["POST", "PUT"])
@jwt_required()
def create_user() -> tuple[dict, int]:
    """Create a new user.

    This operation requires administrator permissions and the following header
    with an access token:
        "Authorization: Bearer access_token"

    Request data (JSON string):
        - name (string): Username.
        - password (string): Password.
        - admin (boolean, optional): Whether the user is an administrator or
            not (default).
        - enabled (boolean, optional): Whether the user is enabled or not
            (default).
        - name (string, optional): Full name.
        - email (string, optional): E-mail address.

    Response status codes:
        - 201 (Success)
        - 400 (Bad Request)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.
        - result (object): User ID.

    :return: Tuple containing the response data and the response status code.
    """
    # JWT payload data
    admin = get_jwt()["admin"]

    # Check permissions
    if not admin:
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    # Get the request data
    user = request.get_json() if request.data else {}

    # Validate the request data. A "marshmallow.ValidationError" exception is
    # raised if the data is invalid, which produces a 400 error response.
    user = set_cre_schema.load(user)

    # Check that there isn't another user with the same username
    db = get_main_db()

    if db.users.get_by_username(user["username"]):
        return get_response_data(EXISTS, ERROR_ITEM_EXISTS), 400

    # Encrypt Password
    user["password"] = get_hash(user["password"])

    # Load/deserialize the data with the standard schema to generate the values
    # of the ID, Created and Last Modified fields and process all the fields.
    user = schema.load(user)

    # Create user
    db.users.put(user)
    result = {"id": user["id"]}

    return get_response_data(CREATED, OK, result), 201


@bp.route("/user/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id: str) -> tuple[dict, int]:
    """Update an existing user.

    The user, if they aren't an administrator, can call this operation only to
    update their own data, except the "username", "admin" or "enabled" fields.
    This operation requires the following header with an access token:
        "Authorization: Bearer access_token"

    Request parameters:
        - user_id (string): User ID.

    Request data (JSON string):
        - username (string, optional): Username.
        - password (string, optional): Password.
        - admin (boolean, optional): Whether the user is an administrator or
            not (default).
        - enabled (boolean, optional): Whether the user is enabled or not
            (default).
        - name (string, optional): Full name.
        - email (string, optional): E-mail address.

    Response status codes:
        - 200 (Success)
        - 400 (Bad Request)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 404 (Not Found)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.

    :param user_id: User ID.
    :return: Tuple containing the response data and the response status code.
    """
    # Validate the ID. A "marshmallow.ValidationError" exception is raised if
    # the data is invalid, which produces a 400 response.
    user_id = id_schema.load({"id": user_id})["id"]

    # JWT payload data
    jwt = get_jwt()
    req_user_id = jwt["user_id"]
    admin = jwt["admin"]

    # Get the request data
    user = request.get_json() if request.data else {}

    # Validate the request data. A "marshmallow.ValidationError" exception is
    # raised if the data is invalid, which produces a 400 error response.
    s = set_upd_adm_schema if admin else set_upd_reg_schema
    user = s.load(user)

    # Get current user
    db = get_main_db()
    cu_user = db.users.get_by_id(user_id)

    # Check the permissions and that the user exists
    if admin and cu_user is None:
        d = get_response_data(NOT_FOUND, ERROR_ITEM_NOT_FOUND)
        return d, 404

    if not admin and (user_id != req_user_id or cu_user is None):
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    # Check that there isn't another user with the same username
    if admin:
        k = "username"
        cu_username = cu_user[k]
        username = user[k]

        if username != cu_username and db.users.get_by_username(username):
            return get_response_data(EXISTS, ERROR_ITEM_EXISTS), 400

    # Keep the values of the ID and Created fields of the current user document
    for k in ("id", "created"):
        user[k] = cu_user[k]

    # If a new password is provided, we encrypt it. Otherwise, we need to set
    # the password of the new user document ("user") to the password of the
    # current user document ("cu_user") as the new document will replace the
    # current one and we need to keep the current password (which is already
    # encrypted).
    k = "password"
    user[k] = get_hash(user[k]) if k in user else cu_user[k]

    # If the request user is not an administrator, we keep the values of the
    # Username, Admin and Enabled fields of the current user document as non
    # administrator users are not allowed to modify these fields.
    if not admin:
        for k in ("username", "admin", "enabled"):
            user[k] = cu_user[k]

    # Load/deserialize the data with the standard schema to generate the value
    # of the Last Modified field and process all the fields.
    user = schema.load(user)

    # Update user
    db.users.put(user)

    return get_response_data(UPDATED, OK), 200


@bp.route("/user/<user_id>", methods=["DELETE"])
@jwt_required(fresh=True)
def delete_user(user_id: str) -> tuple[dict, int]:
    """Delete an existing user.

    This operation requires administrator permissions and the following header
    with a fresh access token:
        "Authorization: Bearer fresh_access_token"

    Request parameters:
        - user_id (string): User ID.

    Response status codes:
        - 200 (Success)
        - 401 (Unauthorized)
        - 403 (Forbidden)
        - 404 (Not Found)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.

    :param user_id: User ID.
    :return: Tuple containing the response data and the response status code.
    """
    # Validate the ID. A "marshmallow.ValidationError" exception is raised if
    # the data is invalid, which produces a 400 response.
    user_id = id_schema.load({"id": user_id})["id"]

    # JWT payload data
    admin = get_jwt()["admin"]

    # Check permissions
    if not admin:
        d = get_response_data(USER_UNAUTHORIZED, ERROR_UNAUTHORIZED_USER)
        return d, 403

    # Check that the user exists
    db = get_main_db()

    if not db.users.get_by_id(user_id):
        return get_response_data(NOT_FOUND, ERROR_ITEM_NOT_FOUND), 404

    # Delete user
    db.users.delete(user_id)

    # Delete all user's notebooks
    for nb in db.notebooks.get_by_user(user_id):
        nb_id = nb["id"]
        db.notebooks.delete(nb_id)

        # Delete all notebook's notes
        for n in db.notes.get_by_filter(nb_id):
            db.notes.delete(n["id"])

    return get_response_data(DELETED, OK), 200
