"""Provides Exception classes for 'session' Nawah Module"""

from typing import Literal


class InvalidCredentialsException(Exception):
    """Raised by callable of 'session/auth' endpoint if provided credentials are invalid"""

    status = 403

    def __init__(self):
        super().__init__("Wrong auth credentials")


class InvalidUserException(Exception):
    """Raised by callable of 'session/auth' endpoint if credentials point to a user who is
    'banned', 'deleted', or with 'disabled_password'"""

    status = 403

    def __init__(self, *, reason: Literal["banned", "deleted", "disabled_password"]):
        if reason == "disabled_password":
            msg = "User password is disabled"
        else:
            msg = f"User is {reason}"

        super().__init__(msg)


class AnonReauthException(Exception):
    """Raised by callable of 'session/reauth' endpoint if attempting to reauth ANON user"""

    status = 400

    def __init__(self):
        super().__init__("Reauth is not allowed for ANON user")


class InvalidSessionException(Exception):
    """Raised by callable of 'session/reauth' endpoint if attempting to reauth with invalid
    session _id, or session token, or by callable of 'session/signout' endpoint of attempting
    to sign-out with invalid session"""

    status = 403

    def __init__(self):
        super().__init__("Invalid session")


class ExpiredSessionException(Exception):
    """Raised by callable of 'session/reauth' endpoint if attempting to reauth with expired
    session"""

    status = 403

    def __init__(self):
        super().__init__("Session had expired")


class AnonSignoutException(Exception):
    """Raised by callable of 'session/signout' endpoint if attempting to sign-out ANON user"""

    status = 400

    def __init__(self):
        super().__init__("Sign-out is not allowed for ANON user")
