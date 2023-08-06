"""Asynchronous Python client providing Open Data information of Brussel."""


class ODPBrusselError(Exception):
    """Generic Open Data Platform Brussel exception."""


class ODPBrusselConnectionError(ODPBrusselError):
    """Open Data Platform Brussel - connection error."""
