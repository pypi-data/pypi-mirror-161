"""
Defines the different types of exceptions corresponding to the API errors:
401, 403, 404, 429, 500
"""

from enum import Enum
from pymarketstack.responses import Error


class PyMarketException(RuntimeError):
    """The base exception for the different API errors."""
    pass


class UnspecifiedException(RuntimeError):
    """The type of error isn't clear, doesn't necessarily correspond to any API error."""
    pass


class NoDataException(PyMarketException):
    """If the download returned no data."""
    pass


class TokenException(PyMarketException):
    """
    Corresponds to invalid API tokens.

    Error code: 401

    API Types: invalid_access_key, missing_access_key
    """
    def __init__(self, error: Error):
        message = f"[{error.code}]: {error.message}"

        super(PyMarketException, self).__init__(message)
        self.message = message


class AccessException(PyMarketException):
    """
    Corresponds to restricted access errors.

    Error code: 403

    API Types: https_access_restricted, function_access_restricted
    """

    def __init__(self, error: Error):
        message = f"[{error.code}]: {error.message}"

        super(PyMarketException, self).__init__(message)
        self.message = message


class EndpointException(PyMarketException):
    """
    Corresponds to invalid api requests, such as invalid URLs and so on.

    Error code: 404

    API Types: invalid_api_function, 404_not_found
    """

    def __init__(self, error: Error):
        message = f"[{error.code}]: {error.message}"

        super(PyMarketException, self).__init__(message)
        self.message = message


class BatchException(PyMarketException):
    """
    Corresponds to a failed batch, e.g if an entire download batch contained only invalid symbols.

    Error code: 422.

    API Types: no_valid_symbols_provided
    """
    def __init__(self, error: Error):
        message = f"[{error.code}]: {error.message}"

        super(PyMarketException, self).__init__(message)
        self.message = message


class LimitException(PyMarketException):
    """
    Limits being reached, either rate limit, quota limits or both.

    Error code: 429

    API Types: usage_limit_reached, rate_limit_reached
    """
    def __init__(self, error: Error):
        message = f"[{error.code}]: {error.message}"

        super(PyMarketException, self).__init__(message)
        self.message = message


class InternalException(PyMarketException):
    """
    Corresponds to an internal error.

    Error code: 500

    API types: internal_error
    """
    def __init__(self, error: Error):
        message = f"[{error.code}]: {error.message}"

        super(PyMarketException, self).__init__(message)
        self.message = message


class ApiCodes(Enum):
    """API code constants."""

    OK = 200
    TOKEN = 401
    ACCESS = 403
    ENDPOINT = 404
    BATCH = 422
    LIMIT = 429
    INTERNAL = 500
