"""Error handlers module."""

from flask import Flask
from marshmallow import ValidationError

from werkzeug.exceptions import (
    NotFound, MethodNotAllowed, BadRequest, TooManyRequests,
    InternalServerError
)

from notelist.responses import (
    URL_NOT_FOUND, METHOD_NOT_ALLOWED, TOO_MANY_REQUESTS, BAD_REQUEST,
    INTERNAL_SERVER_ERROR, ERROR_URL_NOT_FOUND, ERROR_METHOD_NOT_ALLOWED,
    ERROR_TOO_MANY_REQUESTS, ERROR_BAD_REQUEST, ERROR_VALIDATION,
    ERROR_INTERNAL_SERVER, get_response_data
)


def not_found_handler(e: NotFound) -> tuple[dict, int]:
    """Handle 404 errors (Not Found).

    :param e: Exception object.
    :return: Tuple containing the response data and the response status code.
    """
    return get_response_data(URL_NOT_FOUND, ERROR_URL_NOT_FOUND), 404


def method_not_allowed_handler(e: MethodNotAllowed) -> tuple[dict, int]:
    """Handle 405 errors (Method Not Allowed).

    :param e: Exception object.
    :return: Tuple containing the response data and the response status code.
    """
    d = get_response_data(METHOD_NOT_ALLOWED, ERROR_METHOD_NOT_ALLOWED)
    return d, 405


def too_many_requests_error_handler(e: TooManyRequests) -> tuple[dict, int]:
    """Handle 429 errors (Too Many Requests).

    :param e: Exception object.
    :return: Tuple containing the response data and the response status code.
    """
    u = "second" if e.retry_after == 1 else "seconds"
    mv = TOO_MANY_REQUESTS.format(e.retry_after, u)

    return get_response_data(mv, ERROR_TOO_MANY_REQUESTS), 429


def bad_request_handler(e: BadRequest) -> tuple[dict, int]:
    """Handle 400 errors (Bad Request).

    :param e: Exception object.
    :return: Tuple containing the response data and the response status code.
    """
    return get_response_data(BAD_REQUEST, ERROR_BAD_REQUEST), 400


def validation_error_handler(error: ValidationError) -> tuple[dict, int]:
    """Handle validation errors (`marshmallow.ValidationError` exceptions).

    :param error: Object containing the error messages.
    :return: Tuple containing the response data and the response status code.
    """
    m = [str(i) + ": " + str(v) for i, v in error.messages.items()]
    m = " - ".join(m)

    return get_response_data(m, ERROR_VALIDATION), 400


def internal_server_error_handler(e: InternalServerError) -> tuple[dict, int]:
    """Handle 500 errors (Internal Server Error).

    :param e: Exception object.
    :return: Tuple containing the response data and the response status code.
    """
    d = get_response_data(INTERNAL_SERVER_ERROR, ERROR_INTERNAL_SERVER)
    return d, 500


def register_error_handlers(app: Flask):
    """Register the error handlers.

    :param app: Flask application object.
    """
    for e, f in (
        (NotFound, not_found_handler),
        (MethodNotAllowed, method_not_allowed_handler),
        (TooManyRequests, too_many_requests_error_handler),
        (BadRequest, bad_request_handler),
        (ValidationError, validation_error_handler),
        (InternalServerError, internal_server_error_handler)
    ):
        app.register_error_handler(e, f)
