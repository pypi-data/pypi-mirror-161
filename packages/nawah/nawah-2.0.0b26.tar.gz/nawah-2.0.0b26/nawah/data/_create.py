"""Provides 'create' Data Function"""

from typing import TYPE_CHECKING

from nawah.config import Config

if TYPE_CHECKING:
    from nawah.types import NawahDoc, NawahSession, ResultsArgs


async def create(
    *,
    session: "NawahSession",
    collection_name: str,
    doc: "NawahDoc",
) -> "ResultsArgs":
    """Creates 'doc' in 'collection' using connection 'data' connection in 'session'"""

    collection = session["conn"]["data"][Config.data_name][collection_name]
    results = await collection.insert_one(doc)
    _id = results.inserted_id

    # Explicitly convert _id value to str to streamline return format across all Data calls
    return {"count": 1, "docs": [{"_id": str(_id)}]}
