"""Asynchronous Python client providing Open Data information of Liege."""


class ODPLiegeError(Exception):
    """Generic Open Data Platform Liege exception."""


class ODPLiegeConnectionError(ODPLiegeError):
    """Open Data Platform Liege - connection error."""
