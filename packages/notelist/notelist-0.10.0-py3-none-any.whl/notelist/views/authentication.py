"""Authentication views module."""

from hmac import compare_digest
from datetime import timedelta

from flask import Blueprint, request

from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token, get_jwt,
    get_jwt_identity
)

from notelist.tools import get_hash
from notelist.config import SettingsManager
from notelist.schemas.auth import LoginSchema
from notelist.db import get_main_db, get_temp_db
from notelist.responses import OK, ERROR_INVALID_CREDENTIALS, get_response_data


# Messages
USER_LOGGED_IN = "User logged in"
INVALID_CREDENTIALS = "Invalid credentials"
TOKEN_REFRESHED = "Token refreshed"
USER_LOGGED_OUT = "User logged out"

# Blueprint object
bp = Blueprint("auth", __name__)

# Schema
schema = LoginSchema()


@bp.route("/login", methods=["POST"])
def login() -> tuple[dict, int]:
    """Log in.

    This operation returns a fresh access token and a refresh token. Any of the
    tokens can be provided to an API request in the following header:
        "Authorization: Bearer access_token"

    Request data (JSON string):
        - username (string): Username.
        - password (string): Password.

    Response status codes:
        - 200 (Success)
        - 400 (Bad Request)
        - 401 (Unauthorized)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.
        - result (object): User ID, access token and refresh token.

    :return: Tuple containing the response data and the response status code.
    """
    # Get the request data
    auth = request.get_json() if request.data else {}

    # Validate the request data. A "marshmallow.ValidationError" exception is
    # raised if the data is invalid, which produces a 400 error response.
    auth = schema.load(auth)

    # We get the hash of the request password, as passwords are stored
    # encrypted in the database.
    password = get_hash(auth["password"])

    # Get the user from the database
    db = get_main_db()
    user = db.users.get_by_username(auth["username"])

    # Check user and password
    if (
        not user or
        not user["enabled"] or
        not compare_digest(password, user["password"])
    ):
        d = get_response_data(INVALID_CREDENTIALS, ERROR_INVALID_CREDENTIALS)
        return d, 401

    # Create access and refresh tokens. The user ID is the Identity of the
    # tokens (not to be confused with the JTI (unique identifier) of the
    # tokens).
    user_id = user["id"]

    acc_tok = create_access_token(user_id, fresh=True)
    ref_tok = create_refresh_token(user_id)

    sm = SettingsManager()
    acc_exp = sm.get("NL_ACCESS_TOKEN_EXP")   # Acc. token expiration (minutes)
    ref_exp = sm.get("NL_REFRESH_TOKEN_EXP")  # Ref. token expiration (minutes)

    acc_exp = str(timedelta(minutes=acc_exp))  # Acc. token exp. description
    ref_exp = str(timedelta(minutes=ref_exp))  # Ref. token exp. description

    result = {
        "user_id": user_id,
        "access_token": acc_tok,
        "access_token_expiration": acc_exp,
        "refresh_token": ref_tok,
        "refresh_token_expiration": ref_exp
    }

    return get_response_data(USER_LOGGED_IN, OK, result), 200


@bp.route("/refresh", methods=["GET"])
@jwt_required(refresh=True)
def refresh() -> tuple[dict, int]:
    """Get a new, not fresh, access token.

    Refreshing the access token is needed when the token is expired. This
    operation requires the following header with a refresh token:
        "Authorization: Bearer refresh_token"

    Response status codes:
        - 200 (Success)
        - 401 (Unauthorized)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.
        - result (object): New, not fresh, access token.

    :return: Tuple containing the response data and the response status code.
    """
    # Get the request JWT Identity, which in this application is equal to the
    # ID of the request user.
    user_id = get_jwt_identity()

    # Create a new, not fresh, access token
    acc_tok = create_access_token(user_id, fresh=False)

    # Access token expiration (in minutes)
    sm = SettingsManager()
    acc_exp = sm.get("NL_ACCESS_TOKEN_EXP")

    # Access token expiration description
    acc_exp = str(timedelta(minutes=acc_exp))

    result = {
        "access_token": acc_tok,
        "access_token_expiration": acc_exp
    }

    return get_response_data(TOKEN_REFRESHED, OK, result), 200


@bp.route("/logout", methods=["GET"])
@jwt_required()
def logout() -> tuple[dict, int]:
    """Log out.

    This operation revokes an access token provided in the request. This
    operation requires the following header with the access token:
        "Authorization: Bearer access_token"

    Response status codes:
        - 200 (Success)
        - 401 (Unauthorized)
        - 422 (Unprocessable Entity)

    Response data (JSON string):
        - message (string): Message.
        - message_type (string): Message type.

    :return: Tuple containing the response data and the response status code.
    """
    # JWT payload data, which contains:
    #   - "jti" (string): The JTI is a unique identifier of the JWT token.
    #   - "exp" (integer): Expiration time in seconds of the JWT token.
    jwt = get_jwt()

    # We add the JTI of the JWT token of the current request to the Block List
    # in order to revoke the token. We use the token expiration time as the
    # expiration time for the block list token (after this time, the token is
    # removed from the block list.
    db = get_temp_db()
    db.blocklist.put(jwt["jti"], jwt["exp"])

    return get_response_data(USER_LOGGED_OUT, OK), 200
