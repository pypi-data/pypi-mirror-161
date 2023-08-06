"""Provides function to create CLI for Nawah"""

import importlib
import os
import sys

import click

from nawah import __version__

from ._create import create
from ._generate import generate_models_dart
from ._serve import serve as serve_utility


@click.group
def cli():
    """Creates CLI for Nawah"""


@cli.command
def version():
    """Print Nawah version and exit"""
    click.echo(f"Nawah v{__version__}")


@cli.command
def serve():
    """Serve Nawah app from current working directory"""
    sys.path.insert(1, os.path.abspath("."))
    module = importlib.import_module("_app")
    serve_utility(getattr(module, "app"))


@cli.group(name="generate_models")
def generate_models():
    """Generate client apps models"""


@generate_models.command
@click.option(
    "--path", prompt=" Enter path to Nawah app", type=str, default="./models/"
)
@click.option(
    "--filename",
    prompt=" Enter filename to save models to",
    type=str,
    required=False,
    default="",
)
def dart(path, filename):
    sys.path.insert(1, os.path.abspath("."))
    module = importlib.import_module("_app")
    generate_models_dart(module.app, path, filename)

    # parser_create = subparsers.add_parser('create', help='Create new Nawah app')
    # parser_create.set_defaults(func=create)
    # parser_create.add_argument(
    #     'component',
    #     help='Type of component to create',
    #     choices=['app', 'package', 'module'],
    # )

    # parser_create.add_argument(
    #     'name',
    #     type=str,
    #     help='Name of component to create',
    # )

    # parser_create.add_argument(
    #     'path',
    #     type=str,
    #     nargs='?',
    #     help='Path to create component in [default .]',
    #     default='.',
    # )

    # parser_create.add_argument(
    #     '--standalone',
    #     help='When creating Nawah package, add this flag to create standalone Python project '
    #     'for Nawah package. This allows developing Nawah package in isolation, with ability to '
    #     'publish it as Python package and use it across multiple apps. If you are intending to '
    #     'use the package in one app only, don\'t use this flag, and point path to Nawah app '
    #     'folder, to only create project sub-package',
    #     action='store_true',
    # )

    # args = parser.parse_args()

    # if args.command:
    #     args.func(args)

    # else:
    #     parser.print_help()
