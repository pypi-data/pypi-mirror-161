"""Provides exceptions related to 'call' Utility"""


class InvalidCallEndpointException(Exception):
    """Raised by 'call' Utility if value for arg 'endpoint' is invalid"""

    status = 400

    def __init__(self, *, endpoint):
        super().__init__(
            f"Invliad endpoint format: '{endpoint}'",
        )


class InvalidModuleException(Exception):
    """Raised by 'call' Utility if endpoint points to non-existent Nawah Module"""

    status = 404

    def __init__(self, *, module_name):
        super().__init__(f"Nawah Module '{module_name}' is not defined")


class InvalidFuncException(Exception):
    """Raised by 'call' Utility if endpoint points to non-existent Nawah Function"""

    status = 404

    def __init__(self, *, module_name, func_name):
        super().__init__(
            f"Nawah Module '{module_name}' does not have Function '{func_name}' defined"
        )


class NotPermittedException(Exception):
    """Raised by 'check_permissions' Utility if failed to match Permissions Sets for current
    session user"""

    status = 403

    def __init__(self, *, module_name, func_name):
        super().__init__(f"Not permitted to access '{module_name}'.'{func_name}'")


class InvalidCallArgException(Exception):
    """Raised by 'call' Utility if 'Call Arg' used in call had invalid value"""

    status = 400

    def __init__(self, *, module_name, func_name, arg_name):
        super().__init__(
            f"Invalid value for 'Call Arg' '{arg_name}' of '{module_name}'.'{func_name}'",
        )


class UnknownCallArgException(Exception):
    """Raised by 'call' Utility if 'Call Arg' used in call is not defined in Nawah Function"""

    status = 400

    def __init__(self, *, module_name, func_name, arg_name):
        super().__init__(
            f"Function of '{module_name}'.'{func_name}' does not define '{arg_name}' in 'call_args'"
        )
