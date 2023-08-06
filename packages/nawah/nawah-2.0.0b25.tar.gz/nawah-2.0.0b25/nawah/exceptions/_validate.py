"""Provides exceptions related to validation"""


class MissingAttrException(Exception):
    """Raised by 'validate_doc' Utility if required 'attr' is missing from 'doc'"""

    status = 400

    def __init__(self, *, attr_name):
        super().__init__(f"Missing attr '{attr_name}'")


class InvalidAttrException(Exception):
    """Raised by 'validate_attr' Utility if 'attr' has invalid value"""

    status = 400

    def __init__(self, *, attr_name, attr_type, val_type):
        super().__init__(
            f"Invalid attr '{attr_name}' of type '{val_type}' with required type '{attr_type}'"
        )
