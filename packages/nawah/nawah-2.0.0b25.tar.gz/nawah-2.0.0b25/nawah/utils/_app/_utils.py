"""Provides utilties used to manage Nawah App serving"""

import asyncio
import datetime
import logging
import traceback
from functools import partial
from typing import TYPE_CHECKING

from nawah.config import Config

if TYPE_CHECKING:
    from asyncio import Future

    from nawah.classes import Job

logger = logging.getLogger("nawah")


def _populate_routes():
    get_routes = []
    post_routes = []
    for module_name, module in Config.modules.items():
        for func_name, func in module.funcs.items():
            if func.get_func:
                for get_args_set in func.query_attrs or [{}]:
                    if get_args_set:
                        get_args = f'/{{{"}/{".join(list(get_args_set.keys()))}}}'
                    else:
                        get_args = ""

                    get_routes.append(f"/{module_name}/{func_name}{get_args}")

            func.post_func = True
            if func.post_func:
                post_routes.append(f"/{module_name}/{func_name}")

    return (get_routes, post_routes)


async def _check_sessions(session_ids: list[str], /):
    for session_id in session_ids:
        try:
            session = Config.sys.sessions[session_id]
            if "last_call" not in session["conn"]:
                continue
            if datetime.datetime.utcnow() > (
                session["conn"]["last_call"]
                + datetime.timedelta(seconds=Config.conn_timeout)
            ):
                logger.debug(
                    "Session #'%s' with REMOTE_ADDR '%s' HTTP_USER_AGENT: '%s' is idle. "
                    "Closing",
                    session["conn"]["id"],
                    session["conn"]["REMOTE_ADDR"],
                    session["conn"]["HTTP_USER_AGENT"],
                )
                asyncio.create_task(_close_session(session_id))
        except Exception:
            logger.error("An error occurred. Details: %s", traceback.format_exc())


async def _close_session(session_id: str, /):
    # [TODO] Check necissity to implement session_lock for deleteing env object from sessions

    if session_id not in Config.sys.sessions:
        logger.debug("Skipped closing session #'%s'", session_id)
        return

    # Remove id from Env dict to avoid having _close_session be called from _websocket_handler
    # upon closing the websocket connection
    del Config.sys.sessions[session_id]["conn"]["id"]

    logger.debug(
        "Closing data connection for session #'%s'",
        session_id,
    )
    Config.sys.sessions[session_id]["conn"]["data"].close()

    logger.debug("Done closing data connection")
    logger.debug(
        "Websocket connection status: %s",
        not Config.sys.sessions[session_id]["conn"]["ws"].closed,
    )

    if not Config.sys.sessions[session_id]["conn"]["ws"].closed:
        await Config.sys.sessions[session_id]["conn"]["ws"].close()
    logger.debug("Websocket connection for session #'%s' closed", session_id)

    try:
        del Config.sys.sessions[session_id]
    except KeyError:
        logger.error("Failed to delete session #%s", session_id)


async def _check_ips_quota(ips: list[str], /):
    for ip in ips:
        ip_quota = Config.sys.ip_quota[ip]
        try:
            if (datetime.datetime.utcnow() - ip_quota["last_check"]).seconds > 59:
                logger.debug(
                    "IP '%s' with quota '%s' is idle. Cleaning-up",
                    ip,
                    ip_quota["counter"],
                )
                del Config.sys.ip_quota[ip]
        except Exception:
            logger.error("An error occurred. Details: %s", traceback.format_exc())


async def _execute_jobs():
    current_time = datetime.datetime.utcnow().isoformat()[:16]
    for job_name, job in Config.jobs.items():
        try:
            logger.debug("Checking: %s", job_name)
            if job.disabled:
                logger.debug("-Job is disabled. Skipping")
                continue
            # Check if job is scheduled for current_time
            if current_time >= job.next_time:
                logger.debug("-Job is due, running!")
                # Update job next_time
                job.next_time = datetime.datetime.fromtimestamp(
                    job.cron_schedule.get_next(), datetime.timezone.utc
                ).isoformat()[:16]

                job_task = asyncio.create_task(job.job(session=Config.sys.session))
                job_task.add_done_callback(
                    partial(_job_callback, job_name=job_name, job=job)
                )

            else:
                logger.debug("-Not yet due")
        except Exception:
            logger.error("An error occurred. Details: %s", traceback.format_exc())


def _job_callback(job_task: "Future", job_name: str, job: "Job"):
    try:
        job_task.result()
        logger.debug("-Job '%s' is done", job_name)
    except Exception as e:
        logger.error("Job '%s' has failed with exception", job_name)
        logger.error("Exception details:")
        logger.error(e)
        if job.prevent_disable:
            logger.warning("-Detected job prevent_disable. Skipping disabling job")
        else:
            logger.warning("-Disabling job")
            job.disabled = True
