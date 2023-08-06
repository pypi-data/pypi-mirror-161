"""Provides 'serve_app' Utility"""
import asyncio
from typing import TYPE_CHECKING

from nawah.utils._app import _run_app
from nawah.utils._config import config_app, setup_app

if TYPE_CHECKING:
    from nawah.classes import App


def serve(app_config: "App", /):
    """Takes 'App' Object and setup runtime for it to run"""

    setup_app(app_config, process_vars=True)
    asyncio.run(config_app())
    _run_app()
