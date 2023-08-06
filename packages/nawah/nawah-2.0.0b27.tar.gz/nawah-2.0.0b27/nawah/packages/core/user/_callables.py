"""Provides 'user' Module Functions callables"""

import copy
from typing import TYPE_CHECKING, Optional

from bson import ObjectId

from nawah.classes import Query
from nawah.config import Config
from nawah.enums import Event
from nawah.utils import call

from ._exceptions import (GroupAddedException, GroupNotAddedException,
                          InvalidGroupException, InvalidUserException)

if TYPE_CHECKING:
    from nawah.types import NawahDoc, NawahEvents, NawahSession, Results


async def _read(
    skip_events: "NawahEvents",
    session: "NawahSession",
    query: "Query",
    skip_sanitise_results: Optional[bool],
    raise_no_success: Optional[bool],
) -> "Results":
    skip_events.append(Event.PERM)
    read_results = await call(
        "base/read",
        module_name="user",
        skip_events=skip_events,
        session=session,
        query=query,
        args={
            "raise_no_success": raise_no_success,
        },
    )

    if read_results["status"] != 200:
        return read_results

    # Return results as is if both sanitise_results, user_settings are to be skipped
    if skip_sanitise_results is True:
        return read_results

    # Otherwise, iterate over results and apply not skipped action
    for i, _ in enumerate(read_results["args"]["docs"]):
        user = read_results["args"]["docs"][i]
        # Apply sanitise_results, removing hashes, if not skipped
        if skip_sanitise_results is not True:
            for user_attr_sanitise in Config.user_attrs_sanitise:
                del user[user_attr_sanitise]

    return read_results


async def _create(
    skip_events: "NawahEvents",
    session: "NawahSession",
    doc: "NawahDoc",
    raise_no_success: Optional[bool],
) -> "Results":
    if Event.ATTRS_DOC not in skip_events:
        doc["groups"] = [ObjectId("f00000000000000000000013")]

    create_results = await call(
        "base/create",
        skip_events=[Event.PERM],
        module_name="user",
        session=session,
        doc=doc,
        args={
            "raise_no_success": raise_no_success,
        },
    )

    return create_results


async def _read_privileges(session: "NawahSession", query: "Query") -> "Results":
    # Confirm _id is valid
    results = await call(
        "user/read",
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": query["_id:$eq"][0]}}]),
        args={"skip_sanitise_results": True},
    )

    if not results["args"]["count"]:
        raise InvalidUserException()

    user = results["args"]["docs"][0]
    # Loop over user's groups to extract privileges from
    for group in user["groups"]:
        group_results = await call(
            "group/read",
            skip_events=[Event.PERM],
            session=session,
            query=Query([{"_id": {"$eq": group}}]),
            args={
                "raise_no_success": True,
            },
        )
        group = group_results["args"]["docs"][0]
        for privilege in group["privileges"].keys():
            if privilege not in user["privileges"].keys():
                user["privileges"][privilege] = []
            for i in range(len(group["privileges"][privilege])):
                if (
                    group["privileges"][privilege][i]
                    not in user["privileges"][privilege]
                ):
                    user["privileges"][privilege].append(
                        group["privileges"][privilege][i]
                    )

    # Check for key asterisk in user's privileges
    if '*' in user["privileges"]:
        # Key asterisk exists, insert keys for all modules, not already added, and add key asterisk
        # value to it
        for module_name in Config.modules:
            if module_name not in user['privileges']:
                # For non-existing modules in user's privileges, copy key asterisk value
                user['privileges'][module_name] = copy.deepcopy(user['privileges']['*'])
            else:
                # Otherwise, append items of key asterisk to module user's privileges. This
                # potentially causes duplicate values in module values, but later step would
                # resolve such issue by converting module list to set then back to list
                user['privileges'][module_name].extend(user['privileges']['*'])

    # Loop over all modules to expand asterisk values، if any
    for module_name, module in Config.modules.items():
        if module_name not in user['privileges']:
            continue

        if '*' in user['privileges'][module_name]:
            user['privileges'][module_name].extend(module.privileges)
            # To avoid potential duplicates, convert to set, and back to list
            user['privileges'][module_name] = list(set(user['privileges'][module_name]))

    return results


async def _add_group(
    skip_events: "NawahEvents", session: "NawahSession", query: "Query", doc: "NawahDoc"
) -> "Results":
    # Check for list group attr
    if isinstance(doc["group"], list):
        for i in range(0, len(doc["group"]) - 1):
            await call(
                "user/add_group",
                skip_events=skip_events,
                session=session,
                query=query,
                doc={"group": doc["group"][i]},
            )
        doc["group"] = doc["group"][-1]
    # Confirm all basic args are provided
    doc["group"] = ObjectId(doc["group"])
    # Confirm group is valid
    results = await call(
        "group/read",
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": doc["group"]}}]),
    )

    if not results["args"]["count"]:
        raise InvalidGroupException()
    # Get user details
    results = await call(
        "user/read", skip_events=[Event.PERM], session=session, query=query
    )
    if not results["args"]["count"]:
        raise InvalidUserException()

    user = results["args"]["docs"][0]
    # Confirm group was not added before
    if doc["group"] in user["groups"]:
        raise GroupAddedException()

    user["groups"].append(doc["group"])
    # Update the user
    results = await call(
        "user/update",
        skip_events=[Event.PERM],
        session=session,
        query=query,
        doc={"groups": user["groups"]},
        args={
            "raise_no_success": True,
        },
    )
    # Check if the updated User doc belongs to current session and update it
    if session["user"]["_id"] == user["_id"]:
        user_results = await call(
            "user/read_privileges",
            skip_events=[Event.PERM],
            session=session,
            query=Query([{"_id": {"$eq": user["_id"]}}]),
        )
        session["user"] = user_results["args"]["docs"][0]

    return results


async def _delete_group(session: "NawahSession", query: "Query") -> "Results":
    # Confirm group is valid
    results = await call(
        "group/read",
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": query["group:$eq"][0]}}]),
    )

    if not results["args"]["count"]:
        raise InvalidGroupException()
    # Get user details
    results = await call(
        "user/read",
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": query["_id:$eq"][0]}}]),
    )

    if not results["args"]["count"]:
        raise InvalidUserException()

    user = results["args"]["docs"][0]
    # Confirm group was not added before
    if query["group:$eq"][0] not in user["groups"]:
        raise GroupNotAddedException()

    # Update the user
    results = await call(
        "user/update",
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": query["_id:$eq"][0]}}]),
        doc={"groups": {"$del_val": [query["group:$eq"][0]]}},
    )

    # if update fails, return update results
    if results["status"] != 200:
        return results

    # Check if the updated User doc belongs to current session and update it
    if session["user"]["_id"] == user["_id"]:
        user_results = await call(
            "user/read_privileges",
            skip_events=[Event.PERM],
            session=session,
            query=Query([{"_id": {"$eq": user["_id"]}}]),
        )
        session["user"] = user_results["args"]["docs"][0]

    return results
