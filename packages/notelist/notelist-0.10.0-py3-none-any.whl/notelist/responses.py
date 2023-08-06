"""Responses module."""

from typing import Any


# Messages
URL_NOT_FOUND = "The requested URL was not found"
METHOD_NOT_ALLOWED = "The method is not allowed for the requested URL"
MISSING_TOKEN = "Missing token"
INVALID_TOKEN = "Invalid token"
NOT_FRESH_TOKEN = "Not fresh token"
EXPIRED_TOKEN = "Expired token"
REVOKED_TOKEN = "Revoked token"
USER_UNAUTHORIZED = "User unauthorized"
TOO_MANY_REQUESTS = "Too many requests. Please try again after {} {}."
BAD_REQUEST = "Bad request."
INTERNAL_SERVER_ERROR = "Internal server error"

# Message types
OK = "ok"
ERROR_URL_NOT_FOUND = "error_url_not_found"
ERROR_METHOD_NOT_ALLOWED = "method_not_allowed"
ERROR_INVALID_CREDENTIALS = "error_invalid_credentials"
ERROR_MISSING_TOKEN = "error_missing_token"
ERROR_INVALID_TOKEN = "error_invalid_token"
ERROR_NOT_FRESH_TOKEN = "error_not_fresh_token"
ERROR_EXPIRED_TOKEN = "error_expired_token"
ERROR_REVOKED_TOKEN = "error_revoked_token"
ERROR_UNAUTHORIZED_USER = "error_unauthorized_user"
ERROR_ITEM_EXISTS = "error_item_exists"
ERROR_ITEM_NOT_FOUND = "error_item_not_found"
ERROR_TOO_MANY_REQUESTS = "error_too_many_requests"
ERROR_BAD_REQUEST = "error_bad_request"
ERROR_VALIDATION = "error_validation"
ERROR_INTERNAL_SERVER = "internal_server_error"


def get_response_data(
    message: str, message_type: str, result: Any = None
) -> dict:
    """Return the response data of a given request.

    The value returned is a dictionary intended to be serialized as a JSON
    string and to be sent as the response data of a given request.

    :param message: Message.
    :param message_type: Message type.
    :param result: Result (optional).
    :returns: Response data.
    """
    data = {"message": message, "message_type": message_type}

    if result is not None:
        data["result"] = result

    return data
