# Copyright Exafunction, Inc.

""" Entry point for the Exafunction local e2e tool """

import logging
import os
import pathlib
import subprocess
import sys
import tempfile

from exa.py_utils.argparse_utils import ExtendAction


def setup_parser(subparser):
    """Sets up the argument subparser"""
    subparser.register("action", "extend", ExtendAction)
    subparser.add_argument("image_name", type=str)
    subparser.add_argument("--config", type=str, action="extend", nargs="+")
    subparser.add_argument("--preloaded_container", action="store_true")
    subparser.add_argument("--no_default_config", action="store_true")
    subparser.add_argument("--cpu_only", action="store_true")


_DEFAULT_CONFIG_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), "default_config.pbtxt"
)


def _run_local_e2e(args, tmpdir):
    image_name = args.image_name

    os.makedirs("/tmp/exafunction", exist_ok=True)

    configs = []
    if not args.no_default_config:
        default_config_template = pathlib.Path(
            _DEFAULT_CONFIG_TEMPLATE_PATH
        ).read_text()
        default_config_contents = default_config_template
        replacements = {"%{cpu_only}": "true" if args.cpu_only else "false"}
        for original, replacement in replacements.items():
            default_config_contents = default_config_contents.replace(
                original, replacement
            )
        default_config_path = os.path.join(tmpdir, "default_config.pbtxt")
        pathlib.Path(default_config_path).write_text(default_config_contents)
        configs.append(default_config_path)

    if args.config is not None:
        configs.extend(args.config)

    cmd = ["docker", "run", "--net=host"]
    if not args.cpu_only:
        cmd += ["--gpus=all"]

    cmd += [
        "-it",
        "--rm",
        "--mount",
        "type=bind,source=/dev/shm,target=/dev/shm",
        "--shm-size=1024m",
    ]
    if not args.preloaded_container:
        cmd += [
            "--mount",
            "type=bind,source=/tmp/exafunction,target=/tmp/exafunction",
        ]

    for config in configs:
        real_config = os.path.realpath(config)
        cmd += ["--mount", f"type=bind,source={real_config},target={real_config}"]

    cmd += [f"{image_name}"]

    for config in configs:
        real_config = os.path.realpath(config)
        cmd += ["--config", real_config]

    logging.info("Running command %s", cmd)

    # Don't print Python stacktrace on failure, just exit with the right
    # return code.
    ret = subprocess.run(cmd, check=False)
    sys.exit(ret.returncode)


def main(args):
    """The main function for this tool"""
    with tempfile.TemporaryDirectory() as tmpdir:
        _run_local_e2e(args, tmpdir)
