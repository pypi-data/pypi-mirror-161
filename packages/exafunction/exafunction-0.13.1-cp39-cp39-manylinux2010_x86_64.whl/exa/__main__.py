# Copyright Exafunction, Inc.

""" Entry point into Exafunction's Python tooling """

import argparse
import logging
import sys

from exa.py_docker import docker_tool
from exa.py_local_e2e import local_e2e_tool
from exa.py_module_repository import module_repository_tool
from exa.py_utils.argparse_utils import ExtendAction

logging.basicConfig(level=logging.INFO)


def _main():
    parser = argparse.ArgumentParser()
    parser.register("action", "extend", ExtendAction)

    # No global arguments yet

    subparsers = parser.add_subparsers(
        title="Subcommands", description="Valid subcommands"
    )

    module_repository_parser = subparsers.add_parser(
        "module_repository",
        aliases=["mr"],
        help="Commands for manipulating the module repository",
    )
    module_repository_parser.set_defaults(tool_main=module_repository_tool.main)
    module_repository_parser.set_defaults(tool_parser=module_repository_parser)
    module_repository_tool.setup_parser(module_repository_parser)

    local_e2e_parser = subparsers.add_parser(
        "local_e2e",
        help="Runs the local e2e container",
    )
    local_e2e_parser.set_defaults(tool_main=local_e2e_tool.main)
    local_e2e_parser.set_defaults(tool_parser=local_e2e_parser)
    local_e2e_tool.setup_parser(local_e2e_parser)

    docker_parser = subparsers.add_parser(
        "docker",
        help="Commands to assemble Docker images for common use cases",
    )
    docker_parser.set_defaults(tool_main=docker_tool.main)
    docker_parser.set_defaults(tool_parser=docker_parser)
    docker_tool.setup_parser(docker_parser)

    args = parser.parse_args()

    # Ideally we would use add_subparsers(required=True) but Python 3.6
    # doesn't have it.
    # TODO(douglas): revisit this later
    if not hasattr(args, "tool_main"):
        parser.print_help()
        logging.error("error: missing subcommand")
        sys.exit(-1)

    args.tool_main(args)


if __name__ == "__main__":
    _main()
