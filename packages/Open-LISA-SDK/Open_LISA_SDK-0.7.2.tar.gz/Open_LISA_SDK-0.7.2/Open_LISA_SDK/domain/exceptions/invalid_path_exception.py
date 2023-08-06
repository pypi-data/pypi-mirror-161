from .sdk_exception import OpenLISAException


class InvalidPathException(OpenLISAException):
    """
    Raised when trying to manipulate an invalid path in server file system
    """

    def __init__(self, message):
        super().__init__(message)
