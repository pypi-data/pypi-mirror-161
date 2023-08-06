

class FyooBaseException(Exception):
    """Base exception for fyoo library

    This exception is not to be used directly,
    but catching this error would catch a known exception raised
    by this internal library.
    """


class FyooTemplateException(FyooBaseException):
    """Exception raised when rendering templates
    """
