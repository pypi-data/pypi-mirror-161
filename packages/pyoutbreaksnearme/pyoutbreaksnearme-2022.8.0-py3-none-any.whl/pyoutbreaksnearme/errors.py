"""Define package exceptions."""


class OutbreaksNearMeError(Exception):
    """Define a base exception."""

    pass


class RequestError(OutbreaksNearMeError):
    """Define a exception related to HTTP request errors."""

    pass
