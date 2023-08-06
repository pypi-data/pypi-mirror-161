"""Provides 'delete_file' Base Function callable"""

from typing import TYPE_CHECKING

from nawah.classes import Query
from nawah.config import Config
from nawah.enums import AttrType, Event
from nawah.exceptions import InvalidAttrException
from nawah.utils import call

from .exceptions import (InvalidDeleteFileDocAttrException,
                         InvalidDeleteFileIndexException,
                         InvalidDeleteFileIndexValueException,
                         InvalidDeleteFileMismatchNameException,
                         InvalidDocException, UtilityModuleDataCallException)

if TYPE_CHECKING:
    from nawah.types import NawahDoc, NawahSession, Results


async def delete_file(
    *,
    module_name: str,
    session: "NawahSession",
    query: "Query",
    doc: "NawahDoc",
) -> "Results":
    """Removes file from existing doc in module"""

    module = Config.modules[module_name]

    if not module.collection:
        raise UtilityModuleDataCallException(
            module_name=module_name, func_name="delete_file"
        )

    # [TODO] Allow use dot-notated attr path in attr query attr
    file_attr_name = query["attr:$eq"][0]
    if (
        file_attr_name not in module.attrs
        or module.attrs[file_attr_name].type != AttrType.LIST
        or not module.attrs[file_attr_name].args["list"][0].type != AttrType.FILE
    ):
        raise InvalidAttrException(
            attr_name=file_attr_name,
            attr_type=module.attrs[file_attr_name].type
            if file_attr_name in module.attrs
            else None,
            val_type=type(doc[file_attr_name]),
        )

    read_results = await call(
        "base/read",
        module_name=module_name,
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": query["_id:$eq"][0]}}]),
    )

    if not read_results["args"]["count"]:
        raise InvalidDocException(doc_id=query["_id:$eq"][0])

    doc = read_results["args"]["docs"][0]

    if file_attr_name not in doc or not doc[file_attr_name]:
        raise InvalidDeleteFileDocAttrException(
            doc_id=query["_id:$eq"][0], attr_name=file_attr_name
        )

    if query["index:$eq"][0] not in range(len(doc[file_attr_name])):
        raise InvalidDeleteFileIndexException(
            doc_id=query["_id:$eq"][0],
            attr_name=file_attr_name,
            index=query["index:$eq"][0],
        )

    if (
        not isinstance(doc[file_attr_name][query["index:$eq"][0]], dict)
        or "name" not in doc[file_attr_name][query["index:$eq"][0]]
    ):
        raise InvalidDeleteFileIndexValueException(
            doc_id=query["_id:$eq"][0],
            attr_name=file_attr_name,
            index=query["index:$eq"][0],
            index_val_type=type(doc[file_attr_name][query["index:$eq"][0]]),
        )

    if doc[file_attr_name][query["index:$eq"][0]]["name"] != query["name:$eq"][0]:
        raise InvalidDeleteFileMismatchNameException(
            doc_id=query["_id:$eq"][0],
            attr_name=file_attr_name,
            index=query["index:$eq"][0],
            query_file_name=query["name:$eq"][0],
            index_file_name=doc[file_attr_name][query["index:$eq"][0]]["name"],
        )

    update_results = await call(
        "base/update",
        module_name=module_name,
        skip_events=[Event.PERM],
        session=session,
        query=Query([{"_id": {"$eq": query["_id:$eq"][0]}}]),
        doc={
            file_attr_name: {"$del_val": [doc[file_attr_name][query["index:$eq"][0]]]}
        },
    )

    return update_results
