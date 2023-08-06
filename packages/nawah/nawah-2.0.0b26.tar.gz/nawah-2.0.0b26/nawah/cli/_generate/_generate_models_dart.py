import datetime
import logging
import os
import string
from typing import TYPE_CHECKING

from nawah.config import Config
from nawah.enums import AttrType
from nawah.utils._config import setup_app

if TYPE_CHECKING:
    from nawah.classes import App, Attr, Module

logger = logging.getLogger("nawah")


def generate_models_dart(app_config: "App", path: str, filename: str):
    setup_app(app_config)

    # Initialise _api_models Config Attr
    api_models = "// Nawah Models\n"
    # Add interface for DOC, LOCALE, LOCALES, FILE typing
    api_models += "class Doc { String _id; }\n"
    api_models += "class LOCALE { "
    for locale in Config.locales:
        api_models += "String" + ("?" if locale != Config.locale else "") + locale
    api_models += "}\n"
    api_models += (
        "// Locales supported by API '" + "' | '".join(Config.locales) + "';\n"
    )
    api_models += "class LOCALES extends String {}\n"
    api_models += "class ID<T> extends T {}\n"
    api_models += "class FILE { String name; int lastModified; String type; int size; String ref; }\n"
    api_models += (
        "class ATTR { String type; Map args; bool? allow_none; dynamic default; }\n"
    )
    api_models += "class GEO_POINT { String type; List<int> coordinates; }"
    # Iterate over packages in ascending order
    for package in sorted(Config.sys.packages):
        # Add package header
        api_models += f'\n// Package: {package.replace("modules.", "")}\n'
        if not Config.sys.packages[package]:
            api_models += "// No modules\n"
        # Iterate over package modules in ascending order
        for module in sorted(Config.sys.packages[package]["modules"]):
            api_models += _generate_module_model(module=module)
        api_models += "\n"

    models_file = os.path.join(
        os.path.abspath(path),
        filename
        or f'NAWAH_API_MODELS_{datetime.datetime.utcnow().strftime("%d-%b-%Y")}.dart',
    )
    with open(models_file, "w", encoding="UTF-8") as f:
        f.write(api_models)
        logger.info("API models generated and saved to: '%s'", models_file)


def _generate_module_model(*, module: str):
    module_model = ""
    module_class = string.capwords(module.replace("_", " ")).replace(" ", "")
    # Add module header
    module_model += f"// Module: {module_class}\n"

    # Add module interface definition
    module_model += f"class {module_class} extends Doc {{\n"
    # Iterate over module attrs to add attrs types, defaults (if any)
    for attr_name in Config.modules[module].attrs:
        module_model += _generate_attr_model(
            module=module, module_model=module_model, attr_name=attr_name
        )

    # Add closing braces
    module_model += (
        f"\n\t{module_class}({{"
        + ", ".join(
            f"required this.{attr_name}" for attr_name in Config.modules[module].attrs
        )
        + "})\n"
    )
    module_model += (
        "\n\tMap toJson() => {"
        + ", ".join(
            f"'{attr_name}': {attr_name}" for attr_name in Config.modules[module].attrs
        )
        + "}\n"
    )
    module_model += (
        f"\n\t{module_class} fromJson(Map json) => {module_class}("
        + ", ".join(
            f"{attr_name}: json['{attr_name}']"
            for attr_name in Config.modules[module].attrs
        )
        + ")\n"
    )
    module_model += "}\n"

    return module_model


def _generate_attr_model(*, module: str, module_model: str, attr_name: str):
    attr_model = ""
    attr_model += f"\t__TYPE____DEFAULT__ {attr_name};\n"
    for default_attr in Config.modules[module].defaults.keys():
        if default_attr == attr_name or default_attr.startswith(f"{attr_name}."):
            # Attr is in defaults, indicate the same
            attr_model = attr_model.replace("__DEFAULT__", "?")
    # Attempt to replace __DEFAULT__ with empty string if it still exists, effectively no default value
    attr_model = attr_model.replace("__DEFAULT__", "")

    # Add typing
    attr_model = attr_model.replace(
        "__TYPE__",
        _generate_attr_typing(
            module_model=module_model,
            module=Config.modules[module],
            attr_name=attr_name,
            attr_type=Config.modules[module].attrs[attr_name],
        ),
    )

    if Config.modules[module].attrs[attr_name].desc:
        attr_model = (
            f"\t// {Config.modules[module].attrs[attr_name].desc}\n{attr_model}"
        )

    return attr_model


def _generate_attr_typing(
    *, module_model: str, module: "Module", attr_name: str, attr_type: "Attr"
):
    if attr_type.type == AttrType.ANY:
        return "dynamic"

    if attr_type.type == AttrType.BOOL:
        return "bool"

    if attr_type.type == AttrType.DATE:
        return "String"

    if attr_type.type == AttrType.DATETIME:
        return "String"

    if attr_type.type == AttrType.ATTR:
        return "IATTR"

    if attr_type.type == AttrType.KV_DICT:
        return "Map"

    if attr_type.type == AttrType.TYPED_DICT:
        return "Map"

    if attr_type.type == AttrType.EMAIL:
        return "String"

    if attr_type.type == AttrType.FILE:
        return "FILE"

    if attr_type.type == AttrType.FLOAT:
        return "int"

    if attr_type.type == AttrType.GEO_POINT:
        return "GEO_POINT"

    if attr_type.type == AttrType.ID:
        return "ID<String>"

    if attr_type.type == AttrType.INT:
        return "int"

    if attr_type.type == AttrType.IP:
        return "String"

    if attr_type.type == AttrType.LIST:
        return "LIST<dynamic>"

    if attr_type.type == AttrType.LOCALE:
        return "LOCALE"

    if attr_type.type == AttrType.LOCALES:
        return "LOCALES"

    if attr_type.type == AttrType.PHONE:
        return "String"

    if attr_type.type == AttrType.STR:
        return "String"

    if attr_type.type == AttrType.TIME:
        return "String"

    if attr_type.type == AttrType.URI_WEB:
        return "String"

    if attr_type.type == AttrType.LITERAL:
        return "String"

    if attr_type.type == AttrType.UNION:
        return "dynamic"

    if attr_type.type == AttrType.TYPE:
        return "dynamic"
