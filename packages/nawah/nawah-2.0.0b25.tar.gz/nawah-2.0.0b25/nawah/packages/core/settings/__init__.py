"""Provides 'settings' Nawah Core Module"""

from nawah.classes import Attr, Diff, Extn, Func, Module, Perm, Var

settings = Module(
    name="settings",
    desc="'settings' module module provides data type and controller for settings in Nawah "
    "eco-system. This reflects stateful config that are needed for Nawah App to operate",
    collection="setting_docs",
    attrs={
        "var": Attr.STR(
            desc="Name of the setting. This is unique for every 'user' in the module"
        ),
        "val": Attr.ANY(desc="Value of the setting"),
        "val_type": Attr.ATTR(),
    },
    diff=Diff(condition=lambda *_: True),
    unique_attrs=["var"],
    extns={
        "val": Extn(
            module=Var.DOC("val.__extn.module"),
            attrs=Var.DOC("val.__extn.attrs"),
            force=Var.DOC("val.__extn.force"),
        ),
    },
    funcs={
        "read": Func(
            permissions=[Perm(privilege="read")],
        ),
        "create": Func(
            permissions=[
                Perm(privilege="create"),
            ],
            call_args={"raise_no_success": Attr.BOOL()},
        ),
        "update": Func(
            permissions=[
                Perm(privilege="update", query_mod={"$limit": 1}),
            ],
            query_attrs=[{"_id": Attr.ID()}, {"var": Attr.STR()}],
            call_args={"raise_no_success": Attr.BOOL()},
        ),
        "delete": Func(
            permissions=[Perm(privilege="delete", query_mod={"$limit": 1})],
            query_attrs=[{"_id": Attr.ID()}, {"var": Attr.STR()}],
        ),
        "retrieve_file": Func(
            permissions=[Perm(privilege="*")],
            get_func=True,
        ),
    },
)
