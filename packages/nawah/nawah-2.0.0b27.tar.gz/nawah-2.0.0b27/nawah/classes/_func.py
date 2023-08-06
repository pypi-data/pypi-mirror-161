"""Provides 'Func', 'Perm' dataclasses"""

from dataclasses import dataclass
from typing import (TYPE_CHECKING, Awaitable, Callable, MutableMapping,
                    MutableSequence, Optional, Type, Union)

if TYPE_CHECKING:
    from nawah.types import NawahDoc, Results

    from ._analytics import Analytics
    from ._attr import Attr
    from ._cache import Cache
    from ._module import Module
    from ._query import QueryMod


@dataclass(kw_only=True)
class Func:
    """Func dataclass serves role of defining a Nawah Module Function, which identifies set of
    configuration to expose a callable as an endpoint"""

    # pylint: disable=too-many-instance-attributes

    permissions: MutableSequence["Perm"]
    analytics: Optional["Analytics"] = None
    exceptions: Optional[MutableMapping[Type[Exception], bool]] = None
    cache: Optional["Cache"] = None
    cache_channels_update: Optional[MutableSequence[str]] = None
    cache_channels_reset: Optional[MutableSequence[str]] = None
    call_args: Optional[MutableMapping[str, "Attr"]] = None
    query_attrs: Optional[
        Union[MutableMapping[str, "Attr"], MutableSequence[MutableMapping[str, "Attr"]]]
    ] = None
    doc_attrs: Optional[
        Union[MutableMapping[str, "Attr"], MutableSequence[MutableMapping[str, "Attr"]]]
    ] = None
    strict_doc: bool = False
    get_func: bool = False
    post_func: bool = False
    callable: Optional[Callable[..., Awaitable["Results"]]] = None
    desc: Optional[str] = None

    @property
    def name(self) -> str:
        """Getter for '_name' attr"""
        return self._name

    @name.setter
    def name(self, val: str):
        """Setter for '_name' attr"""
        self._name = val

    @property
    def module(self) -> "Module":
        """Getter for '_module' attr"""
        return self._module

    @module.setter
    def module(self, val: "Module"):
        """Setter for '_module' attr"""
        self._module = val

    def __post_init__(self):
        # Create private instance attributes
        self._name = None
        self._module = None
        # Convert query_attrs, doc_attrs to list if defined as dict
        if isinstance(self.query_attrs, dict):
            self.query_attrs = [self.query_attrs]
        if isinstance(self.doc_attrs, dict):
            self.doc_attrs = [self.doc_attrs]


@dataclass(kw_only=True)
class Perm:
    """Perm dataclass serves role of defining a Permissions Set, where Nawah attempts to match
    value of 'privilege' with current 'User' privileges, and use values for 'query_mod', 'doc_mod'
    to modify respective values"""

    privilege: str
    query_mod: Optional["QueryMod"] = None
    doc_mod: Optional["NawahDoc"] = None
