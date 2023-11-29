"""
List of wrappers for returning API errors easily.
"""

from http import HTTPStatus

from flask import Response, make_response


def bad_request(message: str) -> Response:
    """
    Makes Flask Response as an HTTP Bad Request (400).

    :param message: Error detail as a string.
    :return: A Flask Response containing the error.
    """

    return make_response({"message": message}, HTTPStatus.BAD_REQUEST.value)