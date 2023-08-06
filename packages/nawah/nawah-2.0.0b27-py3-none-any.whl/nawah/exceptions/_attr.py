"""Provides exceptions related to Attr Type"""


class InvalidAttrTypeException(Exception):
    """Raied by 'validate_type' Utility if Attr Type object is not valid"""

    def __init__(self, *, attr_type):
        super().__init__(f"Unknown or invalid Attr Type '{attr_type}'")


class InvalidAttrTypeRefException(Exception):
    """Raied by 'validate_type' Utility if Attr Type 'TYPE' object referes to invalid type"""

    def __init__(self, *, attr_type):
        super().__init__(f"Attr Type '{attr_type}' refers to invalid 'type'")


class InvalidAttrTypeArgException(Exception):
    """Raised by 'validate_arg' Utility if Attr Type Arg value is invalid"""

    def __init__(self, *, arg_name: str, arg_type, arg_val):
        super().__init__(
            f"Invalid Attr Type Arg for '{arg_name}' expecting type '{arg_type}' but got "
            f"'{arg_val}'."
        )


class JSONPathNotFoundException(Exception):
    """Raised by \'extract_attr\' Utility if provided didn't match any attr in 'scope'"""

    status = 400

    def __init__(self, *, scope, attr_path):
        super().__init__(f"Failed to extract {attr_path} from scope: {scope}")
