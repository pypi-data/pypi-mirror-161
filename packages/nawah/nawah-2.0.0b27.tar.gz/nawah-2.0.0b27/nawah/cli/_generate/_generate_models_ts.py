import datetime
import logging
import re
from typing import TYPE_CHECKING

from nawah.config import Config
from nawah.enums import AttrType

if TYPE_CHECKING:
    from nawah.classes import Attr, Module

logger = logging.getLogger("nawah")


def generate_models_typescript():
    # Initialise _api_models Config Attr
    api_models = "// Nawah Models\n"
    # Add interface for DOC, LOCALE, LOCALES, FILE typing
    api_models += "interface Doc { _id: string; };\n"
    api_models += "export interface LOCALE { "
    for locale in Config.locales:
        api_models += locale
        if locale != Config.locale:
            api_models += "?"
        api_models += ": string; "
    api_models += "};\n"
    api_models += "export type LOCALES = '" + "' | '".join(Config.locales) + "';\n"
    api_models += "export type ID<T> = string & T;\n"
    api_models += "export interface FILE<T> { name: string; lastModified: number; type: T; size: number; content: string | boolean; };\n"
    # Iterate over packages in ascending order
    for package in sorted(Config.sys.packages):
        # Add package header
        api_models += f'\n// Package: {package.replace("modules.", "")}\n'
        if not Config.sys.packages[package]:
            api_models += "// No modules\n"
        # Iterate over package modules in ascending order
        for module in sorted(Config.sys.packages[package]):
            module_class = (
                str(Config.modules[module].__class__).split(".")[-1].split("'")[0]
            )
            # Add module header
            api_models += f"// Module: {module_class}\n"

            # Add module interface definition
            api_models += f"export interface {module_class} extends String, Doc {{\n"
            # Iterate over module attrs to add attrs types, defaults (if any)
            for attr in Config.modules[module].attrs.keys():
                attr_model = ""
                if Config.modules[module].attrs[attr].desc:
                    attr_model += f"\t// @property {{__TYPE__}} {Config.modules[module].attrs[attr].desc}\n"
                attr_model += f"\t{attr}__DEFAULT__: __TYPE__;\n"
                for default_attr in Config.modules[module].defaults.keys():
                    if default_attr == attr or default_attr.startswith(f"{attr}."):
                        # Attr is in defaults, indicate the same
                        attr_model = attr_model.replace("__DEFAULT__", "?")
                # Attempt to replace __DEFAULT__ with empty string if it still exists, effectively no default value
                attr_model = attr_model.replace("__DEFAULT__", "")

                # Add typing
                attr_model = attr_model.replace(
                    "__TYPE__",
                    _generate_model_typing(
                        module=Config.modules[module],
                        attr_name=attr,
                        attr_type=Config.modules[module].attrs[attr],
                    ),
                )

                api_models += attr_model

            # Add closing braces
            api_models += "};\n"
        api_models += "\n"
    import os

    models_file = os.path.join(
        os.path.abspath("."),
        "models",
        f'NAWAH_API_MODELS_{datetime.datetime.utcnow().strftime("%d-%b-%Y")}.ts',
    )
    with open(models_file, "w") as f:
        f.write(api_models)
        logger.info(f"API models generated and saved to: '{models_file}'. Exiting.")
        exit(0)


def _generate_model_typing(*, module: "Module", attr_name: str, attr_type: "Attr"):
    if attr_type.type == AttrType.ANY:
        return "any"

    if attr_type.type == AttrType.BOOL:
        return "boolean"

    if attr_type.type == AttrType.DATE:
        return "string"

    if attr_type.type == AttrType.DATETIME:
        return "string"

    if attr_type.type == AttrType.ATTR:
        return "{ type: string; args: { [key: string]: any; }; allow_none?: boolean; default: any; }"

    if attr_type.type == AttrType.KV_DICT:
        key_typing = _generate_model_typing(
            module=module, attr_name=attr_name, attr_type=attr_type.args["key"]
        )
        val_typing = _generate_model_typing(
            module=module, attr_name=attr_name, attr_type=attr_type.args["val"]
        )
        return f"{{ [key: {key_typing}]: {val_typing} }}"

    if attr_type.type == AttrType.TYPED_DICT:
        typing = "{ "
        for child_attr_type in attr_type.args["dict"].keys():
            typing += child_attr_type
            typing += ": "
            typing += _generate_model_typing(
                module=module,
                attr_name=attr_name,
                attr_type=attr_type.args["dict"][child_attr_type],
            )
            typing += "; "
        typing += "}"
        return typing

    if attr_type.type == AttrType.EMAIL:
        return "string"

    if attr_type.type == AttrType.FILE:
        types = "string"
        if attr_type.args["types"]:
            types = "'" + "' | '".join(attr_type.args["types"]) + "'"
            if "*" in types:
                types = "string"

        return f"FILE<{types}>"

    if attr_type.type == AttrType.FLOAT:
        return "number"

    if attr_type.type == AttrType.GEO_POINT:
        return "{ type: 'Point'; coordinates: [number, number]; }"

    if attr_type.type == AttrType.ID:
        for attr in module.extns.keys():
            # [TODO] Validate whether Extension Instructions as  breaks this code
            if attr.split(".")[0].split(":")[0] == attr_name:
                # [REF]: https://dev.to/rrampage/snake-case-to-camel-case-and-back-using-regular-expressions-and-python-m9j

                extn_module_class = re.sub(
                    r"(.*?)_([a-zA-Z])",
                    lambda match: match.group(1) + match.group(2).upper(),
                    module.extns[attr].module,
                )
                return f"ID<{extn_module_class[0].upper()}{extn_module_class[1:]}>"
        return "ID<string>"

    if attr_type.type == AttrType.INT:
        return "number"

    if attr_type.type == AttrType.IP:
        return "string"

    if attr_type.type == AttrType.LIST:
        list_typings = []
        for child_attr_type in attr_type.args["list"]:
            list_typings.append(
                _generate_model_typing(
                    module=module, attr_name=attr_name, attr_type=child_attr_type
                )
            )
        list_typing = " | ".join(list_typings)
        return f"Array<{list_typing}>"

    if attr_type.type == AttrType.LOCALE:
        return "LOCALE"

    if attr_type.type == AttrType.LOCALES:
        return "LOCALES"

    if attr_type.type == AttrType.PHONE:
        return "string"

    if attr_type.type == AttrType.STR:
        return "string"

    if attr_type.type == AttrType.TIME:
        return "string"

    if attr_type.type == AttrType.URI_WEB:
        return "string"

    if attr_type.type == AttrType.LITERAL:
        return "'" + "' | '".join(attr_type.args["literal"]) + "'"

    if attr_type.type == AttrType.UNION:
        return " | ".join(
            [
                _generate_model_typing(
                    module=module, attr_name=attr_name, attr_type=child_attr_type
                )
                for child_attr_type in attr_type.args["union"]
            ]
        )

    if attr_type.type == AttrType.TYPE:
        return "any"
