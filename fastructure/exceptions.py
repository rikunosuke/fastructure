class ValidationError(Exception):
    pass


class ConvertError(ValidationError, ValueError):
    pass


class InvalidParameterName(Exception):
    """
    Raised when a parameter name in a method is invalid.
    """
