"""Provides 'session' Module Functions callables"""

import datetime
import secrets
from typing import TYPE_CHECKING, Optional

from bson import ObjectId
from passlib.hash import pbkdf2_sha512

from nawah.classes import Query
from nawah.config import Config
from nawah.enums import Event
from nawah.utils import call

from ._exceptions import (AnonReauthException, AnonSignoutException,
                          ExpiredSessionException, InvalidCredentialsException,
                          InvalidSessionException, InvalidUserException)

if TYPE_CHECKING:
    from nawah.types import NawahDoc, NawahSession, Results


async def _auth(
    session: "NawahSession", doc: "NawahDoc", skip_status_check: Optional[None]
) -> "Results":
    key: str
    for attr in Config.modules["user"].unique_attrs:
        if isinstance(attr, str) and attr in doc:
            key = attr
            break

    user_query = Query([{key: {"$eq": doc[key]}}], special={"$limit": 1})

    if "groups" in doc and doc["groups"]:
        user_query.append({"groups": {"$in": doc["groups"]}})
        user_query.append({"privileges": {"$eq": {"*": ["*"]}}})

    user_results = await call(
        "user/read",
        skip_events=[Event.PERM],
        session=session,
        query=user_query,
        args={"skip_sanitise_results": True},
    )

    if not user_results["args"]["count"] or not pbkdf2_sha512.verify(
        doc["hash"],
        user_results["args"]["docs"][0][f"{key}_hash"],
    ):
        raise InvalidCredentialsException()

    user = user_results["args"]["docs"][0]

    if skip_status_check is not True:
        if user["status"] in ["banned", "deleted", "disabled_password"]:
            raise InvalidUserException(reason=user["status"])

    token = secrets.token_urlsafe(32)
    user_session = {
        "user": user["_id"],
        "groups": doc["groups"] if "groups" in doc.keys() else [],
        "host_add": session["conn"]["REMOTE_ADDR"],
        "user_agent": session["conn"]["HTTP_USER_AGENT"],
        "expiry": (
            datetime.datetime.utcnow() + datetime.timedelta(days=30)
        ).isoformat(),
        "token_hash": pbkdf2_sha512.using(rounds=100000).hash(token),
    }

    results = await call(
        "session/create", skip_events=[Event.PERM], session=session, doc=user_session
    )
    if results["status"] != 200:
        return results

    user_session["_id"] = results["args"]["docs"][0]["_id"]
    user_session["user"] = user
    del user_session["token_hash"]
    user_session["token"] = token
    results["args"]["docs"][0] = user_session

    # read user privileges and return them
    user_results = await call(
        "user/read_privileges",
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": user["_id"]}}]),
    )
    if user_results["status"] != 200:
        return user_results
    results["args"]["docs"][0]["user"] = user_results["args"]["docs"][0]

    return {
        "status": 200,
        "msg": "You were successfully authed.",
        "args": {"session": results["args"]["docs"][0]},
    }


async def _reauth(session: "NawahSession", query: "Query") -> "Results":
    if str(query["_id:$eq"][0]) == "f00000000000000000000012":
        raise AnonReauthException()

    session_query = Query([{"_id": {"$eq": query["_id:$eq"][0]}}])
    if query["groups:$eq"][0]:
        session_query.append({"groups": {"$in": query["groups:$eq"][0]}})
    results = await call(
        "session/read", skip_events=[Event.PERM], session=session, query=session_query
    )
    if not results["args"]["count"]:
        raise InvalidSessionException()

    if not pbkdf2_sha512.verify(
        query["token:$eq"][0], results["args"]["docs"][0]["token_hash"]
    ):
        raise InvalidSessionException()

    del results["args"]["docs"][0]["token_hash"]
    results["args"]["docs"][0]["token"] = query["token:$eq"][0]

    if results["args"]["docs"][0]["expiry"] < datetime.datetime.utcnow().isoformat():
        results = await call(
            "session/delete",
            skip_events=[Event.PERM, Event.SOFT],
            session=session,
            query=Query([{"_id": {"$eq": session["_id"]}}]),
        )
        raise ExpiredSessionException()

    # update user's last_login timestamp
    await call(
        "user/update",
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": results["args"]["docs"][0]["user"]["_id"]}}]),
        doc={"login_time": datetime.datetime.utcnow().isoformat()},
    )
    await call(
        "session/update",
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": results["args"]["docs"][0]["_id"]}}]),
        doc={
            "expiry": (
                datetime.datetime.utcnow() + datetime.timedelta(days=30)
            ).isoformat()
        },
    )
    # read user privileges and return them
    user_results = await call(
        "user/read_privileges",
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": results["args"]["docs"][0]["user"]["_id"]}}]),
    )
    results["args"]["docs"][0]["user"] = user_results["args"]["docs"][0]

    return {
        "status": 200,
        "msg": "You were successfully reauthed.",
        "args": {"session": results["args"]["docs"][0]},
    }


async def _signout(session: "NawahSession", query: "Query") -> "Results":
    if str(query["_id:$eq"][0]) == "f00000000000000000000012":
        raise AnonSignoutException()

    results = await call(
        "session/read",
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": query["_id:$eq"][0]}}]),
    )

    if not results["args"]["count"]:
        raise InvalidSessionException()

    results = await call(
        "session/delete",
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": session["_id"]}}]),
    )

    return {
        "status": 200,
        "msg": "You are successfully signed-out.",
        "args": {"session": {"_id": ObjectId("f00000000000000000000012")}},
    }
