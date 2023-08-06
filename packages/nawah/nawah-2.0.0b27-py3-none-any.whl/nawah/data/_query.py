import copy
import logging
from typing import TYPE_CHECKING, Any, MutableMapping, Optional, Tuple, Union

from nawah.classes import Var
from nawah.config import Config

if TYPE_CHECKING:
    from nawah.classes import Attr, Query
    from nawah.types import (NawahQueryOperAnd, NawahQueryOperOr,
                             NawahQuerySpecialGroup, NawahQueryStep)

logger = logging.getLogger("nawah")


def _compile_query(
    *,
    attrs: MutableMapping[str, "Attr"],
    query: "Query",
) -> Tuple[
    Optional[int],
    Optional[int],
    MutableMapping[str, int],
    Optional[list["NawahQuerySpecialGroup"]],
    list[Any],
]:
    aggregate_prefix: list[Any] = []
    aggregate_suffix: list[Any] = []
    aggregate_query: list[Any] = []
    skip: Optional[int] = None
    limit: Optional[int] = None
    sort: MutableMapping[str, int] = {"_id": -1}
    group: Optional[list["NawahQuerySpecialGroup"]] = None
    logger.debug("attempting to process query: %s", query)

    query = copy.deepcopy(query)

    # Update variables per Query Special Args
    if "$deleted" in query and query["$deleted"] is True:
        aggregate_prefix.append({"$match": {"__deleted": {"$exists": True}}})
    else:
        aggregate_prefix.append({"$match": {"__deleted": {"$exists": False}}})
    if "$skip" in query:
        skip = query["$skip"]
    if "$limit" in query:
        limit = query["$limit"]
    if "$sort" in query:
        sort = query["$sort"]
    if "$group" in query:
        group = query["$group"]
    if "$search" in query:
        aggregate_prefix.insert(0, {"$match": {"$text": {"$search": query["$search"]}}})
        project_query: MutableMapping[str, Any] = {
            attr: "$" + attr for attr in attrs.keys()
        }
        project_query["_id"] = "$_id"
        project_query["__score"] = {"$meta": "textScore"}
        aggregate_suffix.append({"$project": project_query})
        aggregate_suffix.append({"$match": {"__score": {"$gt": 0.5}}})
    if "$geo_near" in query:
        aggregate_prefix.insert(
            0,
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": query["$geo_near"]["val"],
                    },
                    "distanceField": query["$geo_near"]["attr"] + ".__distance",
                    "maxDistance": query["$geo_near"]["dist"],
                    "spherical": True,
                }
            },
        )

    for step in query.pipe or []:
        _compile_query_step(
            query=query,
            aggregate_prefix=aggregate_prefix,
            aggregate_suffix=aggregate_suffix,
            aggregate_query=aggregate_query,
            attrs=attrs,
            step=step,
        )

    if "$attrs" in query and isinstance(query["$attrs"], list):
        group_query: dict[str, Any] = {
            "_id": "$_id",
            **{
                attr: {"$first": f"${attr}"}
                for attr in query["$attrs"]
                if attr in attrs.keys()
            },
        }
        aggregate_suffix.append({"$group": group_query})
    else:
        group_query = {
            "_id": "$_id",
            **{attr: {"$first": f"${attr}"} for attr in attrs.keys()},
        }
        aggregate_suffix.append({"$group": group_query})

    logger.debug(
        "processed query, aggregate_prefix:%s, aggregate_suffix:%s, aggregate_match:%s",
        aggregate_prefix,
        aggregate_suffix,
        aggregate_query,
    )

    aggregate_query = aggregate_prefix + aggregate_query + aggregate_suffix
    return (skip, limit, sort, group, aggregate_query)


def _compile_query_step(
    *,
    query: "Query",
    aggregate_prefix: list[Any],
    aggregate_suffix: list[Any],
    aggregate_query: list[Any],
    attrs: MutableMapping[str, "Attr"],
    step: Union["NawahQueryStep", "NawahQueryOperOr", "NawahQueryOperAnd"],
    append_query: bool = True,
) -> None:
    if append_query:
        aggregate_query.append({"$match": step})

    attr_name = list(step)[0]
    attr_val = step[attr_name]  # type: ignore

    if isinstance(attr_val, list):
        for child_attr_val in attr_val:
            _compile_query_step(
                query=query,
                aggregate_prefix=aggregate_prefix,
                aggregate_suffix=aggregate_suffix,
                aggregate_query=aggregate_query,
                attrs=attrs,
                step=child_attr_val,
                append_query=False,
            )
        return

    if "." not in attr_name:
        return

    root_attr_name = attr_name.split(".")[0]

    if root_attr_name not in attrs or not attrs[root_attr_name].extn:
        return

    # [TODO] Check if this works with EXTN as Attr Type TYPE
    # Don't attempt to extn attr that is already extended
    lookup_query = False
    for stage in aggregate_prefix:
        if "$lookup" in stage.keys() and stage["$lookup"]["as"] == root_attr_name:
            lookup_query = True
            break
    if not lookup_query:
        if isinstance(attrs[root_attr_name].extn.module, Var):
            extn_collection = (
                f'{query[f"{attrs[root_attr_name].extn.module.var}:$eq"][0]}_docs'
            )
        else:
            extn_collection = Config.modules[
                attrs[root_attr_name].extn.module
            ].collection
        aggregate_prefix.append(
            {"$addFields": {root_attr_name: {"$toObjectId": f"${root_attr_name}"}}}
        )
        aggregate_prefix.append(
            {
                "$lookup": {
                    "from": extn_collection,
                    "localField": root_attr_name,
                    "foreignField": "_id",
                    "as": root_attr_name,
                }
            }
        )
        aggregate_prefix.append({"$unwind": f"${root_attr_name}"})
        group_query: MutableMapping[str, Any] = {
            attr: {"$first": f"${attr}"} for attr in attrs.keys()
        }
        group_query[root_attr_name] = {"$first": f"${root_attr_name}._id"}
        group_query["_id"] = "$_id"
        aggregate_suffix.append({"$group": group_query})
        aggregate_suffix.append(
            {"$addFields": {root_attr_name: {"$toString": f"${root_attr_name}"}}}
        )
