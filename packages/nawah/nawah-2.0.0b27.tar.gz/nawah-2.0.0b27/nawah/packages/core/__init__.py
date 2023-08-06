"""Provides 'core' Nawah Package"""

import os

from nawah.classes import Package

from .base import base
from .group import group
from .session import session
from .settings import settings
from .user import user

__version__ = "0.0.0"
with open(
    os.path.join(os.path.dirname(__file__), "..", "..", "version.txt"),
    encoding="UTF-8",
) as f:
    __version__ = f.read().strip()

core = Package(
    name="core",
    api_level="2.0",
    version=__version__,
    modules=[base, user, group, session, settings],
)
