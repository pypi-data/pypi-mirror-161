"""Provides 'update' Base Function callable"""

import inspect
import logging
from typing import TYPE_CHECKING, Optional, cast

import nawah.data as Data
from nawah.classes import Query
from nawah.config import Config
from nawah.enums import Event
from nawah.utils import call, validate_doc

from .exceptions import (DuplicateUniqueException, EmptyUpdateDocException,
                         NoDocUpdatedException, UpdateMultiUniqueException,
                         UtilityModuleDataCallException)

if TYPE_CHECKING:
    from nawah.types import NawahDoc, NawahEvents, NawahSession, Results

logger = logging.getLogger("nawah")


async def update(
    *,
    module_name: str,
    skip_events: "NawahEvents",
    session: "NawahSession",
    query: "Query",
    doc: "NawahDoc",
    raise_no_success: Optional[bool],
) -> "Results":
    """Updates docs for a module matching query 'query'"""

    module = Config.modules[module_name]

    if not module.collection:
        raise UtilityModuleDataCallException(
            module_name=module_name, func_name="update"
        )

    # Check presence and validate all attrs in doc args
    validate_doc(
        mode="update",
        doc=doc,
        attrs=module.attrs,
    )
    # Delete all attrs not belonging to the module
    shadow_doc = {}
    for attr_name in ["_id", *doc.keys()]:
        attr_root = attr_name.split(".")[0].split(":")[0]
        # Check root-level attr belong to module
        if attr_root not in module.attrs.keys():
            continue
        # Check attr is valid Doc Oper
        if (
            isinstance(doc[attr_name], dict)
            and doc[attr_name].keys()
            and list(doc[attr_name].keys())[0][0] == "$"
            and doc[attr_name][list(doc[attr_name].keys())[0]] is None
        ):
            continue
        # Add non-None attrs to shadow_doc
        if doc[attr_name] is not None:
            shadow_doc[attr_name] = doc[attr_name]

    doc = shadow_doc

    # Check if there is anything yet to update
    if not doc:
        if raise_no_success:
            raise EmptyUpdateDocException(module_name=module_name)

        return {"status": 200, "msg": "Nothing to update", "args": {}}
    # Find which docs are to be updated
    docs_results = await Data.read(
        session=session,
        collection_name=module.collection,
        attrs=module.attrs,
        query=query,
        skip_process=True,
    )
    # Check unique_attrs
    if module.unique_attrs:
        # If any of the unique_attrs is present in doc, and docs_results is > 1, we have duplication
        if len(docs_results["docs"]) > 1:
            unique_attrs_check = True
            for attr in module.unique_attrs:
                if isinstance(attr, str) and attr in doc:
                    unique_attrs_check = False
                    break

                if isinstance(attr, tuple):
                    for child_attr in attr:
                        if not unique_attrs_check:
                            break

                        if child_attr in doc:
                            unique_attrs_check = False
                            break

            if not unique_attrs_check:
                raise UpdateMultiUniqueException()

        # Check if any of the unique_attrs are present in doc
        if any(attr in module.unique_attrs for attr in doc):
            # Check if the doc would result in duplication after update
            unique_attrs_query = Query(
                [{"_id": {"$nin": [doc["_id"] for doc in docs_results["docs"]]}}],
                special={"$limit": 1},
            )
            unique_attrs_query_or = []
            for attr in module.unique_attrs:
                if isinstance(attr, str):
                    attr = cast(str, attr)
                    unique_attrs_query_or.append({attr: {"$eq": doc[attr]}})
                elif isinstance(attr, tuple):
                    unique_attrs_query_or.append(
                        {
                            "$and": [
                                {child_attr: {"$eq": doc[child_attr]}}
                                for child_attr in attr
                            ]
                        }
                    )

            unique_attrs_query.append({"$or": unique_attrs_query_or})

            unique_results = await call(
                "base/read",
                module_name=module_name,
                skip_events=[Event.PERM],
                session=session,
                query=unique_attrs_query,
            )
            if unique_results["args"]["count"]:
                raise DuplicateUniqueException(unique_attrs=module.unique_attrs)

    create_diff = False
    # If module has diff enabled, and Event DIFF not skipped:
    if module.diff and Event.DIFF not in skip_events:
        create_diff = True
        # Attr Type TYPE diff, call the funcion and catch InvalidAttrException
        try:
            func_params = {
                "mode": "create",
                "attr_name": "diff",
                "attr_type": module.diff,
                "attr_val": None,
                "skip_events": skip_events,
                "session": session,
                "query": query,
                "doc": doc,
                "scope": doc,
            }
            await module.diff.condition(
                **{
                    param: func_params[param]
                    for param in inspect.signature(module.diff.condition).parameters
                }
            )

        except:
            # [TODO] Implement similar error logging as in retrieve_file
            create_diff = False
            logger.debug("Skipped Diff Workflow due to failed condition")

    else:
        logger.debug(
            "Skipped Diff Workflow due to: %s, %s",
            module.diff,
            Event.DIFF not in skip_events,
        )

    results = await Data.update(
        session=session,
        collection_name=module.collection,
        docs=[doc["_id"] for doc in docs_results["docs"]],
        doc=doc,
    )

    if results["count"] and create_diff:
        for doc_result in docs_results["docs"]:
            diff_results = await Data.create(
                session=session,
                collection_name=f"{module.collection}__diff",
                doc={
                    "user": session["user"]["_id"],
                    "doc": doc_result["_id"],
                    "attrs": {
                        attr.split(".")[0]: doc_result[attr.split(".")[0]]
                        for attr in doc
                    },
                },
            )
        if not diff_results["count"]:
            logger.error("Failed to create Diff doc. Results: %s", diff_results)

    # update soft action is to only return the new created doc _id.
    if Event.SOFT in skip_events:
        read_results = await call(
            "base/read",
            module_name=module_name,
            skip_events=[Event.PERM],
            session=session,
            query=Query(
                [{"_id": {"$in": [doc["_id"] for doc in docs_results["docs"]]}}]
            ),
        )
        results = read_results["args"]

    if raise_no_success is True and results["count"] == 0:
        raise NoDocUpdatedException(module_name=module_name)

    return {"status": 200, "msg": f'Updated {results["count"]} docs', "args": results}
