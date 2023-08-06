"""Provides Exception classes for 'user' Nawah Module"""


class InvalidUserException(Exception):
    """Raised by callable of 'user/read_privileges', 'user/add_group', 'user/delete_group'
    endpoints if user doesn't exist"""

    status = 400

    def __init__(self):
        super().__init__("User is invalid")


class InvalidGroupException(Exception):
    """Raised by callable of 'user/add_group', 'user/delete_group' endpoints if group doesn't
    exist"""

    status = 400

    def __init__(self):
        super().__init__("Group is invalid")


class GroupAddedException(Exception):
    """Raised by callable of 'user/add_group' if user already member in group"""

    status = 400

    def __init__(self):
        super().__init__("User is already a member of the group")


class GroupNotAddedException(Exception):
    """Raised by callable of 'user/delete_group' if user isn't member of group"""

    status = 400

    def __init__(self):
        super().__init__("User is not a member of the group")
