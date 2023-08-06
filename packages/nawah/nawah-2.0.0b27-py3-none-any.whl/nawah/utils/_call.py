"""Provides 'call' Utility"""

import asyncio
import copy
import datetime
import inspect
import json
import logging
import re
import sys
import traceback
from typing import (TYPE_CHECKING, Any, Awaitable, Callable, Literal,
                    MutableMapping, MutableSequence, Type, Union, cast)

from bson import ObjectId

from nawah.classes import Query, QueryMod, Var, app_encoder
from nawah.config import Config
from nawah.enums import Event
from nawah.exceptions import (InvalidAttrException, InvalidCallArgException,
                              InvalidCallEndpointException,
                              InvalidDocAttrException, InvalidDocException,
                              InvalidFuncException, InvalidModuleException,
                              InvalidQueryAttrException, InvalidQueryException,
                              MissingDocAttrException,
                              MissingQueryAttrException,
                              UnknownCallArgException)

from ._cache import _get_cache, _set_cache, reset_cache_channel
from ._check_permissions import check_permissions as check_permissions_utility
from ._val import var_value
from ._validate import validate_attr

if TYPE_CHECKING:
    from nawah.classes import Attr
    from nawah.types import NawahDoc, NawahEvents, NawahSession, Results


logger = logging.getLogger("nawah")


async def call(
    endpoint: str,
    /,
    *,
    module_name: str = None,
    skip_events: "NawahEvents" = None,
    env=None,
    session: "NawahSession" = None,
    query: "Query" = None,
    doc: "NawahDoc" = None,
    args: MutableMapping[str, Any] = None,
) -> "Results":
    """Checks validity of an endpoint and calls Nawah Function callable at endpoint,
    returning the couroutine of the callable. If endpoint points to non-existent
    Nawah Function, raises 'InvalidFuncException'"""

    if not re.match(r"^[a-z_]+\/[a-z_]+$", endpoint):
        raise InvalidCallEndpointException(endpoint=endpoint)

    endpoint_module, endpoint_func = endpoint.split("/")

    try:
        module = Config.modules[endpoint_module]
    except KeyError as e:
        raise InvalidModuleException(module_name=endpoint_module) from e

    try:
        func = module.funcs[endpoint_func]
    except KeyError as e:
        raise InvalidFuncException(
            module_name=endpoint_module, func_name=endpoint_func
        ) from e

    # Set defaults for kwargs
    module_name = module_name or endpoint_module
    skip_events = skip_events or []
    query = query or Query()
    doc = doc or {}
    if not session:
        if env:
            session = env["session"]
        else:
            # Deep-copy system session to prevent manipulating it, but skip conn as it can't be
            # deep-copied
            session = copy.deepcopy(
                {k: v for k, v in Config.sys.session.items() if k != "conn"}
            )
            # Then add it again
            session["conn"] = Config.sys.session["conn"]
    args = args or {}

    # call Utility could be used from app handlers directly, where value for query would be
    # Query-compatible dict. Refactor onto Query
    if isinstance(query, dict) and ("$pipe" in query or "$special" in query):
        if "$pipe" not in query:
            query["$pipe"] = []
        if "$special" not in query:
            query["$special"] = {}

        query = Query(query["$pipe"], special=query["$special"])

    # [TODO] Remove when legacy query format is obsoleted
    # Convert query to Query object
    if not isinstance(query, Query):
        logger.warning("Call is using deprecated query format: %s", query)
        query_special = {}
        for step in query:
            if not isinstance(step, dict):
                continue
            for attr_name, attr_val in step.items():
                if isinstance(attr_name, str) and attr_name[0] == "$":
                    query_special[attr_name] = attr_val
        query = Query(_convert_deprecated_query(query), special=query_special)

    # Check conditions for call checks
    check_permissions = Event.PERM not in skip_events
    check_attrs_query = Event.ATTRS_QUERY not in skip_events
    check_attrs_doc = Event.ATTRS_DOC not in skip_events
    check_cache = Event.CACHE not in skip_events
    check_analytics = Event.ANALYTICS not in skip_events

    if check_permissions:
        query_mod, doc_mod = check_permissions_utility(func=func, session=session)
        if query_mod and not isinstance(query_mod, QueryMod):
            logger.warning(
                "Evaluated permission Set Query Modifier is using deprecated query format: %s",
                query,
            )
            if isinstance(query_mod, dict):
                query_mod = [query_mod]
            query_special = {}
            for step in query_mod:
                if not isinstance(step, dict):
                    continue
                for attr_name, attr_val in step.items():
                    if isinstance(attr_name, str) and attr_name[0] == "$":
                        query.special[attr_name] = attr_val
            query_mod = QueryMod(_convert_deprecated_query(query_mod))

        # Use return of check_permissions_utility to update query, doc
        if query_mod:
            for step in query_mod.pipe:
                query.append(
                    _process_query_mod(
                        query=query,
                        query_mod=cast(MutableMapping, step),
                        session=session,
                        doc=doc,
                    )
                )
            query.special.update(query_mod.special)

        if doc_mod:
            doc.update(
                _process_doc_mod(
                    doc=doc,
                    doc_mod=doc_mod,
                    session=session,
                    query=query,
                )
            )

    if check_attrs_query:
        # Sanitise $deleted Special Query Attr, if ATTRS_QUERY Event is not skipped
        if "$deleted" in query:
            del query["$deleted"]
        func.query_attrs = cast(MutableSequence, func.query_attrs)
        _check_query_attrs(query=query, query_attrs=func.query_attrs)

    if check_attrs_doc:
        func.doc_attrs = cast(MutableSequence, func.doc_attrs)
        _check_doc_attrs(doc=doc, doc_attrs=func.doc_attrs)

    if check_cache:
        cache_key, call_cache = await _get_cache(
            func=func,
            skip_events=skip_events,
            session=session,
            query=query,
        )

        if call_cache:
            return call_cache

    if check_analytics:
        # [TODO] Implement
        pass

    try:
        func_callable = cast(Callable[..., Awaitable["Results"]], func.callable)
        kwargs: MutableMapping = {
            "func": func,
            "module_name": module_name,
            "skip_events": skip_events,
            "env": {"session": session},
            "session": session,
            "query": query,
            "doc": doc,
        }

        # Iterate over call_args to set values
        for arg_name, arg_type in (func.call_args or {}).items():
            if arg_name not in args:
                kwargs[arg_name] = None
                continue

            try:
                validate_attr(
                    mode="update",
                    attr_name=arg_name,
                    attr_type=arg_type,
                    attr_val=args[arg_name],
                )
            except InvalidAttrException as e:
                raise InvalidCallArgException(
                    module_name=module_name, func_name=func.name, arg_name=arg_name
                ) from e
            # Call Arg value is value, append it to kwargs to be passed to Func callable
            kwargs[arg_name] = args[arg_name]
            # Delete arg_val from args to filter out invalid args
            del args[arg_name]

        # If after iterating over call_args, we still have values in args, declare them invalid
        if args:
            arg_name = list(args)[0]
            raise UnknownCallArgException(
                module_name=module_name, func_name=func.name, arg_name=arg_name
            )

        results = await func_callable(
            **{
                param: kwargs[param]
                for param in inspect.signature(func_callable).parameters
                if param in kwargs
            }
        )
    except Exception as e:  # pylint: disable=broad-except
        # Handling exceptions raised in callables goes in one of four conditions

        # No value, or empty dict, for Func.exceptions, such as no exceptions at all expected
        # Raise with reason=no_exceptions, will report as error
        if not func.exceptions:
            _log_and_raise(e=e, endpoint=endpoint, reason="no_exceptions")

        func.exceptions = cast(MutableMapping[Type[Exception], bool], func.exceptions)

        # Exception not in Func.exceptions, such as exception is not expected
        # Raise with reason=exception_not_in, will report as error
        if type(e) not in func.exceptions:
            _log_and_raise(e=e, endpoint=endpoint, reason="exception_not_in")

        # Exception in Func.exceptions, and set to True, such as exception is expected, but still
        # report as error
        # Raise with reason=exception_true, will report as error
        if func.exceptions[type(e)]:
            _log_and_raise(e=e, endpoint=endpoint, reason="exception_true")

        # Exception in Func.exceptions, and set to False, such as exception is expected, no report
        # required. Only scenario as such
        # Raise with reason=exception_false, will log details only
        _log_and_raise(e=e, endpoint=endpoint, reason="exception_false")

    if "args" in results and "session" in results["args"]:
        if "session" == ObjectId("f00000000000000000000012"):
            from ._config import _compile_anon_session, _compile_anon_user

            anon_session = _compile_anon_session()
            anon_session["user"] = _compile_anon_user()
            session.update(anon_session)
        else:
            session.update(json.loads(app_encoder.encode(results["args"]["session"])))

    if check_cache and cache_key:
        results["args"]["cache_key"] = cache_key
        if "cache_time" not in results["args"]:
            logger.debug("Results generated with 'cache_key'. Calling '_set_cache'.")
            results["args"]["cache_time"] = datetime.datetime.utcnow().isoformat()
        # [TODO] Add callback to handle errors
        asyncio.create_task(_set_cache(func=func, cache_key=cache_key, results=results))

    if func.cache_channels_reset:
        for channel in func.cache_channels_reset:
            # [TODO] Add callback to handle errors
            asyncio.create_task(reset_cache_channel(channel))

    return results


def _log_and_raise(
    *,
    e: Exception,
    endpoint: str,
    reason: Literal[
        "no_exceptions", "exception_true", "exception_false", "exception_not_in"
    ],
):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    logging_method = logger.error
    if reason == "exception_false":
        logging_method = logger.error

    logging_method(
        "Callable for '%s' failed with Exception of type: %s", endpoint, type(e)
    )

    logging_method("Exception traceback:")
    for line in traceback.format_exception(exc_type, exc_value, exc_traceback):
        logging_method("- %s", line)

    tb = cast(Any, exc_traceback)

    if tb.tb_next:
        logging_method("Exception frame locals:")
        logging_method(tb.tb_next.tb_frame.f_locals)

    raise e


def _process_query_mod(
    *,
    query_mod: Union[
        MutableMapping[str, Any], MutableSequence[MutableMapping[str, Any]]
    ],
    session: "NawahSession",
    query: "Query",
    doc: "NawahDoc",
):
    if not query_mod:
        return {}

    query_mod_processed: Union[
        MutableMapping[str, Any], MutableSequence[MutableMapping[str, Any]]
    ]

    if isinstance(query_mod, list):
        query_mod_processed = []
        for query_mod_child in query_mod:
            query_mod_processed.append(
                _process_query_mod(
                    query_mod=query_mod_child,
                    session=session,
                    query=query,
                    doc=doc,
                )
            )

    elif isinstance(query_mod, dict):
        query_mod_processed = {}
        for attr_name, attr_val in query_mod.items():
            if isinstance(attr_val, (list, dict)):
                query_mod_processed[attr_name] = _process_query_mod(
                    query_mod=attr_val,
                    session=session,
                    query=query,
                    doc=doc,
                )
            elif isinstance(attr_val, Var):
                query_mod_processed[attr_name] = var_value(
                    attr_val,
                    session=session,
                    doc=doc,
                    locale=session["user"]["locale"],
                )
            else:
                query_mod_processed[attr_name] = copy.deepcopy(attr_val)
    else:
        raise Exception("Unexpected non-list, non-dict value for 'query_mod'")

    return query_mod_processed


def _process_doc_mod(
    *,
    doc_mod: Union[MutableMapping[str, Any], MutableSequence[MutableMapping[str, Any]]],
    session: "NawahSession",
    query: "Query",
    doc: "NawahDoc",
):
    if not doc_mod:
        return {}

    doc_mod_processed: Union[
        MutableMapping[str, Any], MutableSequence[MutableMapping[str, Any]]
    ]

    if isinstance(doc_mod, list):
        doc_mod_processed = []
        for doc_mod_child in doc_mod:
            doc_mod_processed.append(
                _process_doc_mod(
                    doc_mod=doc_mod_child,
                    session=session,
                    query=query,
                    doc=doc,
                )
            )

    elif isinstance(doc_mod, dict):
        doc_mod_processed = {}
        for attr_name, attr_val in doc_mod.items():
            if isinstance(attr_val, (list, dict)):
                doc_mod_processed[attr_name] = _process_doc_mod(
                    doc_mod=attr_val,
                    session=session,
                    query=query,
                    doc=doc,
                )
            elif isinstance(attr_val, Var):
                doc_mod_processed[attr_name] = var_value(
                    attr_val,
                    session=session,
                    doc=doc,
                    locale=session["user"]["locale"],
                )
            else:
                doc_mod_processed[attr_name] = copy.deepcopy(attr_val)
    else:
        raise Exception("Unexpected non-list, non-dict value for 'doc_mod'")

    return doc_mod_processed


def _check_query_attrs(
    *,
    query: "Query",
    query_attrs: MutableSequence[MutableMapping[str, "Attr"]],
):
    if not query_attrs:
        return

    query_attrs_sets: MutableSequence[MutableMapping[str, str]] = []

    for query_attrs_set in query_attrs:
        query_attrs_sets.append({})
        try:
            for attr_name, attr_type in query_attrs_set.items():
                # [TODO] Remove when nawah query is obsoleted
                if ":" not in attr_name:
                    logger.warning(
                        "Detected attr for Func.query_attrs with no oper: %s", attr_name
                    )
                    attr_name = f"{attr_name}:$eq"
                if attr_name not in query:
                    query_attrs_sets[-1][attr_name] = "missing"
                    raise MissingQueryAttrException(attr_name=attr_name)

                for i, attr_val in enumerate(query[attr_name]):
                    try:
                        query[attr_name][i] = validate_attr(
                            mode="create",
                            attr_name=attr_name,
                            attr_type=attr_type,
                            attr_val=attr_val,
                        )
                    except InvalidAttrException as e:
                        query_attrs_sets[-1][attr_name] = "invalid"
                        raise InvalidQueryAttrException(
                            attr_name=attr_name,
                            attr_type=attr_type,
                            val_type=type(attr_val),
                        ) from e

                query_attrs_sets[-1][attr_name] = "valid"
            # If looped successfully over complete set, return to indicate valid Query
            return
        except (InvalidAttrException, MissingQueryAttrException):
            # If exception occur, pass it to allow checking all sets
            pass

    # If all sets are checked but failed to return, rase InvalidQueryException
    raise InvalidQueryException(query_attrs_sets=query_attrs_sets)


def _check_doc_attrs(
    *,
    doc: "NawahDoc",
    doc_attrs: MutableSequence[MutableMapping[str, "Attr"]],
):
    if not doc_attrs:
        return

    doc_attrs_sets: MutableSequence[MutableMapping[str, str]] = []

    for doc_attrs_set in doc_attrs:
        doc_attrs_sets.append({})
        try:
            for attr_name, attr_type in doc_attrs_set.items():
                if attr_name not in doc:
                    doc_attrs_sets[-1][attr_name] = "missing"
                    raise MissingDocAttrException(attr_name=attr_name)

                try:
                    doc[attr_name] = validate_attr(
                        mode="create",
                        attr_name=attr_name,
                        attr_type=attr_type,
                        attr_val=doc[attr_name],
                    )
                except InvalidAttrException as e:
                    doc_attrs_sets[-1][attr_name] = "invalid"
                    raise InvalidDocAttrException(
                        attr_name=attr_name,
                        attr_type=attr_type,
                        val_type=type(doc[attr_name]),
                    ) from e

                doc_attrs_sets[-1][attr_name] = "valid"
            # If looped successfully over complete set, return to indicate valid Doc
            return
        except (InvalidAttrException, MissingDocAttrException):
            # If exception occur, pass it to allow checking all sets
            pass

    # If all sets are checked but failed to return, rase InvalidDocException
    raise InvalidDocException(doc_attrs_sets=doc_attrs_sets)


def _convert_deprecated_query(query):
    query = copy.deepcopy(query)
    shadow_query = []
    for step in query:
        if isinstance(step, list):
            shadow_query.append({"$or": _convert_deprecated_query(step)})

        elif isinstance(step, dict):
            for attr, val in step.items():
                if attr[0] == "$":
                    continue
                if isinstance(val, dict) and (
                    len(val) and list(val)[0].startswith("$")
                ):
                    shadow_step = {attr: val}
                else:
                    shadow_step = {attr: {"$eq": val}}

                if attr == "_id":
                    if isinstance(
                        shadow_step["_id"][list(shadow_step["_id"])[0]], dict
                    ):
                        if "_id" in shadow_step["_id"][list(shadow_step["_id"])[0]]:
                            shadow_step["_id"][list(shadow_step["_id"])[0]] = ObjectId(
                                shadow_step["_id"][list(shadow_step["_id"])[0]]["_id"]
                            )
                    elif isinstance(
                        shadow_step["_id"][list(shadow_step["_id"])[0]], list
                    ):
                        shadow_step["_id"][list(shadow_step["_id"])[0]] = [
                            ObjectId(item)
                            for item in shadow_step["_id"][list(shadow_step["_id"])[0]]
                        ]
                    else:
                        shadow_step["_id"][list(shadow_step["_id"])[0]] = ObjectId(
                            shadow_step["_id"][list(shadow_step["_id"])[0]]
                        )

                shadow_query.append(shadow_step)

    return shadow_query
