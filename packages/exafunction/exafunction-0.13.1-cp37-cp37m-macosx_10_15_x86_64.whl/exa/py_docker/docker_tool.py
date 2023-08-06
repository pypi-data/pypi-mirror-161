# Copyright Exafunction, Inc.

"""Entry point for the Exafunction docker tool."""

import contextlib
import enum
import logging
import os
import os.path
import pathlib
import shutil
import sys
import tempfile

import docker


class _ExafunctionLayer(enum.Enum):
    RUNNER = enum.auto()
    LOCAL_E2E = enum.auto()


@contextlib.contextmanager
def _tmp_dockerfile(contents: str):
    path = pathlib.Path(os.getcwd()) / "exafunction.Dockerfile"
    path.write_text(contents, encoding="utf-8")
    try:
        yield {"path": str(path.parent), "dockerfile": "exafunction.Dockerfile"}
    finally:
        path.unlink()


def _build(client, **kwargs):
    try:
        return client.images.build(**kwargs)
    except docker.errors.BuildError as e:
        for line in e.build_log:
            if "stream" in line:
                logging.error(line["stream"].strip())
        raise


def _build_image(dockerfile, tag=None):
    client = docker.from_env()
    kwargs = {}
    if tag is not None:
        kwargs["tag"] = tag
    with _tmp_dockerfile(dockerfile) as path_kwargs:
        image, _ = _build(client, **path_kwargs, **kwargs)
    if tag is not None:
        logging.info("Built new image with tag %s", image.tags[0])
        print(image.tags[0])
    else:
        logging.info("Built new image with id %s", image.id)
        print(image.id)


def _apply_tar(args):
    if "runner_layer" in args.archive:
        layer = _ExafunctionLayer.RUNNER
    elif "local_e2e_layer" in args.archive:
        layer = _ExafunctionLayer.LOCAL_E2E
    else:
        raise ValueError(
            f"Unrecognized Exafunction layer type for archive [{args.archive}]"
            " (name should contain runner_layer or local_e2e_layer)"
        )
    entrypoint = {
        _ExafunctionLayer.RUNNER: "/app/exa/cmd/runner/runner",
        _ExafunctionLayer.LOCAL_E2E: "/app/exa/cmd/scheduler/local_e2e",
    }[layer]
    filename = os.path.basename(args.archive)
    if args.archive.startswith(("https://", "http://")):
        download_or_copy = f"ADD {args.archive} ."
    else:
        # Local archives are unpacked, so we can't use ADD.
        download_or_copy = f"COPY {args.archive} ."

    dockerfile = f"""
FROM {args.image}

WORKDIR /

{download_or_copy}

RUN tar -xzf {filename} && rm {filename}

ENTRYPOINT {entrypoint}

ENV RUNFILES_DIR={entrypoint}.runfiles
"""
    _build_image(dockerfile, tag=args.tag)


def _apply_requirements(args):
    if args.requirements_txt.startswith(("https://", "http://")):
        download_or_copy = f"ADD {args.requirements_txt} ./exafunction_requirements.txt"
    else:
        # Local archives are unpacked, so we can't use ADD.
        download_or_copy = (
            f"COPY {args.requirements_txt} ./exafunction_requirements.txt"
        )

    dockerfile = f"""
FROM {args.image}

{download_or_copy}

RUN python3 -m pip install --no-cache-dir -r ./exafunction_requirements.txt && rm ./exafunction_requirements.txt
"""
    _build_image(dockerfile, tag=args.tag)


_METADATA_PATH = "/tmp/exafunction/module_repository/metadata"
_CACHE_PATH = "/tmp/exafunction/module_repository/cache"


def _save_snapshot(args):
    """Copy the tmp directory over to a user-specified location"""
    # We have to copy from /tmp to a directory Docker can access with ADD.
    with tempfile.TemporaryDirectory(dir=os.getcwd()) as temp_dir:
        relative_path = temp_dir[len(os.getcwd()) :]
        shutil.copytree(
            _METADATA_PATH,
            temp_dir + "/metadata",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            _CACHE_PATH,
            temp_dir + "/cache",
            dirs_exist_ok=True,
        )
        dockerfile = f"""
FROM {args.image}

ADD {relative_path}/metadata/ {_METADATA_PATH}/

ADD {relative_path}/cache/ {_CACHE_PATH}/
"""
        _build_image(dockerfile, tag=args.tag)


def setup_parser(subparser):
    """Sets up the argument subparser"""

    subparser.add_argument(
        "--image",
        type=str,
        required=True,
        help="What you would put after FROM in the Dockerfile",
    )

    cmd_parsers = subparser.add_subparsers()
    apply_tar_parser = cmd_parsers.add_parser(
        "apply_tar", help="Add Exafunction layer archive to image"
    )
    apply_tar_parser.add_argument("--tag", type=str)
    apply_tar_parser.add_argument("archive", help="Filename or URL for the archive")
    apply_tar_parser.set_defaults(tool_cmd=_apply_tar)

    apply_requirements_parser = cmd_parsers.add_parser(
        "apply_requirements", help="Add pip requirements to image"
    )
    apply_requirements_parser.add_argument("--tag", type=str)
    apply_requirements_parser.add_argument(
        "requirements_txt", help="Filename or URL for the requirements.txt"
    )
    apply_requirements_parser.set_defaults(tool_cmd=_apply_requirements)
    snapshot_parser = cmd_parsers.add_parser(
        "snapshot_local_e2e", help="Save a snapshot of the module repository"
    )
    snapshot_parser.add_argument("--tag", type=str)
    snapshot_parser.set_defaults(tool_cmd=_save_snapshot)


def main(args):
    """The main function for this tool"""
    if not hasattr(args, "tool_cmd"):
        args.tool_parser.print_help()
        logging.error("error: missing tool command")
        sys.exit(-1)
    args.tool_cmd(args)
