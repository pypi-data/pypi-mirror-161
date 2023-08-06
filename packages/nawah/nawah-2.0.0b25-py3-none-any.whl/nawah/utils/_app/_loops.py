"""Provides loops to keep asyncio running, running minutely checks"""

import asyncio
import logging
import sys
import time
from typing import TYPE_CHECKING

import aiohttp.web

from nawah.config import Config

from ._common_handlers import (_not_allowed_handler, _not_found_handler,
                               _root_handler)
from ._http_handler import _http_handler
from ._utils import (_check_ips_quota, _check_sessions, _execute_jobs,
                     _populate_routes)
from ._websocket_handler import _websocket_handler

if TYPE_CHECKING:
    from aiohttp.web import Application

logger = logging.getLogger("nawah")


async def _jobs_loop():
    # Connection Timeout Workflow
    logger.debug("Time to check for sessions!")
    logger.debug("Current sessions: %s", Config.sys.sessions)
    session_ids = list(Config.sys.sessions)
    asyncio.create_task(_check_sessions(session_ids))

    # Calls Quota Workflow - Clean-up Sequence
    logger.debug("Time to check for IPs quotas!")
    ips = list(Config.sys.ip_quota)
    asyncio.create_task(_check_ips_quota(ips))

    # Jobs Workflow
    logger.debug("Time to check for jobs!")
    asyncio.create_task(_execute_jobs())

    # [TODO] Re-implement
    # try:
    #     logger.debug('Time to check for files timeout!')
    #     files_task = asyncio.create_task(
    #         call(
    #             'file/delete',
    #             skip_events=[Event.PERM],
    #             env=Config.sys.env,
    #             query=[
    #                 {
    #                     'create_time': {
    #                         '$lt': (
    #                             datetime.datetime.utcnow()
    #                             - datetime.timedelta(seconds=Config.file_upload_timeout)
    #                         ).isoformat()
    #                     }
    #                 }
    #             ],
    #         )
    #     )
    #     # logger.debug('Files timeout results:')
    #     # logger.debug('-status: %s', files_results['status'])
    #     # logger.debug('-msg: %s', files_results['msg'])
    #     # logger.debug('-args.docs: %s', files_results["args"]['docs'])
    # except Exception:
    #     logger.error('An error occurred. Details: %s', traceback.format_exc())


def _create_error_middleware(overrides):
    @aiohttp.web.middleware
    async def error_middleware(request, handler):
        try:
            response = await handler(request)
            override = overrides.get(response.status)
            if override:
                return await override(request)
            return response
        except aiohttp.web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override:
                return await override(request)
            raise

    return error_middleware


async def _web_loop(app: "Application", /):
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, "0.0.0.0", Config.port)
    await site.start()
    logger.info("Serving on 0.0.0.0:%s", Config.port)
    while True:
        await asyncio.sleep(60)
        asyncio.create_task(_jobs_loop())


def _run_app():
    get_routes, post_routes = _populate_routes()

    logger.debug(
        "Loaded modules: %s",
        {module_name: module.attrs for module_name, module in Config.modules.items()},
    )
    logger.debug(
        "Config has attrs: %s",
        {
            k: str(v)
            for k, v in Config.__dict__.items()
            if not isinstance(v, classmethod) and not k.startswith("_")
        },
    )
    logger.debug("Generated get_routes: %s", get_routes)
    logger.debug("Generated post_routes: %s", post_routes)

    app = aiohttp.web.Application()
    app.middlewares.append(
        _create_error_middleware(
            {
                404: _not_found_handler,
                405: _not_allowed_handler,
            }
        )
    )
    app.router.add_route("GET", "/", _root_handler)
    app.router.add_route("*", "/ws", _websocket_handler)
    for route in get_routes:
        app.router.add_route("GET", route, _http_handler)
    for route in post_routes:
        app.router.add_route("POST", route, _http_handler)
        app.router.add_route("OPTIONS", route, _http_handler)
    logger.info("Welcome to Nawah")

    try:
        asyncio.run(_web_loop(app))
    except KeyboardInterrupt:
        if time.localtime().tm_hour >= 21 or time.localtime().tm_hour <= 4:
            msg = "night"
        elif time.localtime().tm_hour >= 18:
            msg = "evening"
        elif time.localtime().tm_hour >= 12:
            msg = "afternoon"
        elif time.localtime().tm_hour >= 5:
            msg = "morning"

        logger.info("Have a great %s!", msg)

        sys.exit()
