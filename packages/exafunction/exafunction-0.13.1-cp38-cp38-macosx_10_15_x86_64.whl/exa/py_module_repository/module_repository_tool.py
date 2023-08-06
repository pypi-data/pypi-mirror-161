# Copyright Exafunction, Inc.

""" Entry point for the Exafunction module repository tool """

import logging
import sys

from exa.py_module_repository.module_repository import ModuleRepository
from exa.py_module_repository.module_repository import (
    ModuleRepositoryHermeticModulePlugin,
)
from exa.py_module_repository.module_repository import ModuleRepositoryModule
from exa.py_utils.argparse_utils import ExtendAction


def _load_zip(repo, args):
    is_url = args.zip_file.startswith("http://") or args.zip_file.startswith("https://")
    if is_url:
        logging.info("Downloading zip file from %s", args.zip_file)
        _, tags = repo.load_zip_from_url(args.zip_file, not args.no_load_tags)
    else:
        _, tags = repo.load_zip(args.zip_file, not args.no_load_tags)

    if not args.no_load_tags:
        for tag in tags:
            logging.info("Loaded tag %s", tag)


def _override_runner_image(repo, args):
    # Perform some validation first
    for tag in args.tags:
        obj = repo.get_object_from_tag(tag)
        if isinstance(obj, ModuleRepositoryHermeticModulePlugin):
            pass
        elif isinstance(obj, ModuleRepositoryModule):
            if obj.hermetic_module_plugin_id is None:
                raise ValueError(
                    f"Cannot override runner image of builtin module {tag}"
                )
        else:
            raise ValueError(
                f"{tag} is not a module or hermetic module plugin; is {obj}"
            )

    runner_image = repo.register_runner_image(args.runner_image_digest)

    logging.info("Using runner image %s", args.runner_image_digest)

    for tag in args.tags:
        obj = repo.get_object_from_tag(tag)
        if isinstance(obj, ModuleRepositoryHermeticModulePlugin):
            repo.register_plugin_with_new_runner_image(
                obj, runner_image, override_allowed=True
            )
            logging.info("Overrode runner image for plugin %s", tag)
        elif isinstance(obj, ModuleRepositoryModule):
            repo.register_module_with_new_runner_image(
                obj, runner_image, override_allowed=True
            )
            logging.info("Overrode runner image for module %s", tag)


def setup_parser(subparser):
    """Sets up the argument subparser"""

    subparser.add_argument("--addr", type=str, required=True)

    cmd_parsers = subparser.add_subparsers()
    load_zip_parser = cmd_parsers.add_parser(
        "load_zip",
        help="Load a zip file containing module repository objects from a "
        + "file or URL. Note that this may overwrite existing tags!",
    )
    load_zip_parser.add_argument("zip_file", help="Filename or URL for the zip file")
    load_zip_parser.add_argument(
        "--no_load_tags", action="store_true", help="Don't load tags from the zip file"
    )
    load_zip_parser.set_defaults(tool_cmd=_load_zip)

    override_runner_image_parser = cmd_parsers.add_parser(
        "override_runner_image",
        help="Override the runner image for the given set of module "
        + "or hermetic module plugin tags",
    )
    override_runner_image_parser.register("action", "extend", ExtendAction)
    override_runner_image_parser.add_argument(
        "runner_image_digest", help="The Docker image digest for the runner image"
    )
    override_runner_image_parser.add_argument(
        "tags",
        nargs="+",
        action="extend",
        help="The module or hermetic module plugin tags to override",
    )
    override_runner_image_parser.set_defaults(tool_cmd=_override_runner_image)


def main(args):
    """The main function for this tool"""

    # Ideally we would use add_subparsers(required=True) but Python 3.6
    # doesn't have it.
    # TODO(douglas): revisit this later
    if not hasattr(args, "tool_cmd"):
        args.tool_parser.print_help()
        logging.error("error: missing tool command")
        sys.exit(-1)

    with ModuleRepository(args.addr) as repo:
        args.tool_cmd(repo, args)
