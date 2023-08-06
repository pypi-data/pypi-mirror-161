"""Authentication module."""

from flask_jwt_extended import JWTManager

from notelist.db import get_main_db, get_temp_db

from notelist.responses import (
    MISSING_TOKEN, INVALID_TOKEN, NOT_FRESH_TOKEN, EXPIRED_TOKEN,
    REVOKED_TOKEN, ERROR_MISSING_TOKEN, ERROR_INVALID_TOKEN,
    ERROR_NOT_FRESH_TOKEN, ERROR_EXPIRED_TOKEN, ERROR_REVOKED_TOKEN,
    get_response_data
)


# JWT manager
jwt = JWTManager()


@jwt.unauthorized_loader
def unauthorized_loader(error: str) -> tuple[dict, int]:
    """Handle requests with no JWT.

    :param error: Error message.
    :return: Tuple containing the response data and the response status code.
    """
    return get_response_data(MISSING_TOKEN, ERROR_MISSING_TOKEN), 401


@jwt.invalid_token_loader
def invalid_token_loader(error: str) -> tuple[dict, int]:
    """Handle requests with an invalid JWT.

    :param error: Error message.
    :return: Tuple containing the response data and the response status code.
    """
    return get_response_data(INVALID_TOKEN, ERROR_INVALID_TOKEN), 422


@jwt.needs_fresh_token_loader
def needs_fresh_token_loader(header: dict, payload: dict) -> tuple[dict, int]:
    """Handle requests with a not fresh JWT.

    :param header: JWT header data.
    :param payload: JWT payload data.
    :return: Tuple containing the response data and the response status code.
    """
    return get_response_data(NOT_FRESH_TOKEN, ERROR_NOT_FRESH_TOKEN), 401


@jwt.expired_token_loader
def expired_token_loader(header: dict, payload: dict) -> tuple[dict, int]:
    """Handle requests with an expired JWT.

    :param header: JWT header data.
    :param payload: JWT payload data.
    :return: Tuple containing the response data and the response status code.
    """
    return get_response_data(EXPIRED_TOKEN, ERROR_EXPIRED_TOKEN), 401


@jwt.revoked_token_loader
def revoked_token_loader(header: dict, payload: dict) -> tuple[dict, int]:
    """Handle requests with a revoked JWT.

    :param header: JWT header data.
    :param payload: JWT payload data.
    :return: Tuple containing the response data and the response status code.
    """
    return get_response_data(REVOKED_TOKEN, ERROR_REVOKED_TOKEN), 401


@jwt.token_in_blocklist_loader
def blocklist_loader(header: dict, payload: dict) -> bool:
    """Check if a JWT has been revoked.

    :param header: JWT header data.
    :param payload: JWT payload data.
    :return: Whether the given JWT has been revoked or not.
    """
    # JTI is a unique identifier of the JWT token
    db = get_temp_db()
    return db.blocklist.contains(payload["jti"])


@jwt.additional_claims_loader
def additional_claims_loader(identity: str) -> dict[str, str]:
    """Add additional information to the JWT payload when creating a JWT.

    :param identity: JWT identity. In this case, it's the user ID.
    :return: Dictionary with additional information about the request user.
    """
    db = get_main_db()
    user = db.users.get_by_id(identity)

    return {"user_id": user["id"], "admin": user["admin"]}
