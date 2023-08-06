# Copyright Exafunction, Inc.

"""Client for the Exafunction module repository."""

# pylint: disable=too-many-lines

import base64
import hashlib
import io
import logging
import os
import pathlib
import shutil
import stat
import tempfile
from typing import Any, Dict, IO, List, Optional, Set, Tuple, Union
from warnings import warn
import zipfile

import grpc
import requests

from exa.module_repository_pb import module_repository_pb2
from exa.module_repository_pb import module_repository_pb2_grpc

_REGISTER_BLOB_CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB
_GET_ALL_TAGS_WITH_OBJECT_IDS_LIMIT = 1000
_ZIPFILE_PREFIX = "exafunction_module_repository"
_SMALL_FILE_THRESHOLD = 262144  # 256 KiB
_PY_MODULE_PIP_REQUIREMENTS_CONFIG_KEY = "_py_module_pip_requirements"

_module_repository_clear_allowed = False


def _allow_module_repository_clear():
    global _module_repository_clear_allowed  # pylint: disable=global-statement
    _module_repository_clear_allowed = True


class ModuleRepositoryObject:
    """A generic object in the module repository"""

    def __init__(self, type_name: str, serialized_proto: Optional[bytes]):
        self._generic_proto = module_repository_pb2.Metadata()
        self._id: Optional[str] = None
        self._serialized: Optional[bytes] = None
        if serialized_proto is not None:
            self._generic_proto.ParseFromString(serialized_proto)
            self._id = _generate_data_id(io.BytesIO(serialized_proto))
            self._serialized = serialized_proto

        assert (
            serialized_proto is None
            or self._generic_proto.WhichOneof("metadata_oneof") == type_name
        )
        self._proto = getattr(self._generic_proto, type_name)

    @staticmethod
    def from_serialized_proto(serialized_proto: bytes) -> "ModuleRepositoryObject":
        """Creates an Object from a serialized protobuf."""
        proto = module_repository_pb2.Metadata()
        proto.ParseFromString(serialized_proto)
        case = proto.WhichOneof("metadata_oneof")
        if case == "module":
            return ModuleRepositoryModule(serialized_proto)
        if case == "shared_object":
            return ModuleRepositorySharedObject(serialized_proto)
        if case == "runner_image":
            return ModuleRepositoryRunnerImage(serialized_proto)
        if case == "hermetic_module_plugin":
            return ModuleRepositoryHermeticModulePlugin(serialized_proto)
        raise ValueError(f"Unknown metadata type: {case}")

    @property
    def id(self) -> str:
        """Returns the object ID if available."""
        if self._id is None:
            raise ValueError("Cannot get ID of mutable object.")
        return self._id

    def override_id(self, object_id):
        """Overrides the computed object ID."""
        self._id = object_id
        self._serialized = None

    def is_mutable(self) -> bool:
        """Returns whether the object is still mutable"""
        return self._id is None

    @property
    def serialized(self) -> bytes:
        """Returns the serialized proto if available."""
        if self._serialized is None:
            raise ValueError(
                "Cannot get serialized form of mutable object, "
                + "or serialized data is invalid."
            )
        return self._serialized

    def _freeze(self):
        self._serialized = self._generic_proto.SerializeToString(deterministic=True)
        self._id = _generate_data_id(io.BytesIO(self._serialized))

    def clone(self) -> "ModuleRepositoryObject":
        """Returns a clone of the object. Note that the serialized
        proto is not copied, so the clone will be mutable and may serialize
        to a different object ID."""

        # pylint: disable=no-value-for-parameter
        clone_obj = self.__class__()  # type: ignore
        # pylint: disable=protected-access
        clone_obj._generic_proto.MergeFrom(self._generic_proto)
        return clone_obj

    @classmethod
    def _forward(cls, field_name):
        def getter(self):
            # pylint: disable=protected-access
            return getattr(self._proto, field_name)

        def setter(self, value):
            if not self.is_mutable():
                raise RuntimeError("Immutable object cannot be mutated.")
            # pylint: disable=protected-access
            setattr(self._proto, field_name, value)

        return property(getter, setter)

    def __repr__(self):
        if self._id is not None:
            return f"{self.__class__} (id={self._id})"
        return f"{self.__class__} (mutable)"

    def direct_subobject_ids(self) -> Set[str]:
        # pylint: disable=no-self-use
        """Returns the set of direct (not transitive) subobject IDs."""
        return set()

    def direct_blob_ids(self) -> Set[str]:
        # pylint: disable=no-self-use
        """Returns the set of direct (not transitive) blob IDs."""
        return set()


class ModuleRepositoryModule(ModuleRepositoryObject):
    """A module in the module repository"""

    def __init__(self, serialized_proto: Optional[bytes] = None):
        super().__init__("module", serialized_proto)

    module_name: str = ModuleRepositoryObject._forward("module_name")
    module_class: str = ModuleRepositoryObject._forward("module_class")
    hermetic_module_plugin_id: str = ModuleRepositoryObject._forward(
        "hermetic_module_plugin_id"
    )
    shared_object_ids: List[str] = ModuleRepositoryObject._forward("shared_object_ids")
    config: Dict[str, bytes] = ModuleRepositoryObject._forward("config")
    blob_id: str = ModuleRepositoryObject._forward("blob_id")

    def direct_subobject_ids(self) -> Set[str]:
        """Returns the set of direct (not transitive) subobject IDs."""
        ids = set()
        if self.hermetic_module_plugin_id != "":
            ids.add(self.hermetic_module_plugin_id)
        ids.update(self.shared_object_ids)
        return ids

    def direct_blob_ids(self) -> Set[str]:
        """Returns the set of direct (not transitive) blob IDs."""
        return {self.blob_id} if self.blob_id != "" else set()


class ModuleRepositorySharedObject(ModuleRepositoryObject):
    """A shared object in the module repository"""

    def __init__(self, serialized_proto: Optional[bytes] = None):
        super().__init__("shared_object", serialized_proto)

    so_name: str = ModuleRepositoryObject._forward("so_name")
    blob_id: str = ModuleRepositoryObject._forward("blob_id")

    def direct_blob_ids(self) -> Set[str]:
        """Returns the set of direct (not transitive) blob IDs."""
        return {self.blob_id} if self.blob_id != "" else set()


class ModuleRepositoryRunnerImage(ModuleRepositoryObject):
    """A runner image in the module repository"""

    def __init__(self, serialized_proto: Optional[bytes] = None):
        super().__init__("runner_image", serialized_proto)

    image_hash: str = ModuleRepositoryObject._forward("image_hash")


class ModuleRepositoryHermeticModulePlugin(ModuleRepositoryObject):
    """A hermetic module plugin in the module repository"""

    def __init__(self, serialized_proto: Optional[bytes] = None):
        super().__init__("hermetic_module_plugin", serialized_proto)

    shared_object_path: str = ModuleRepositoryObject._forward("shared_object_path")
    runfiles_env_var_names: List[str] = ModuleRepositoryObject._forward(
        "runfiles_env_var_names"
    )
    runner_image_id: str = ModuleRepositoryObject._forward("runner_image_id")
    runfiles_packs: List[
        module_repository_pb2.RunfilesPack
    ] = ModuleRepositoryObject._forward("runfiles_packs")

    def direct_subobject_ids(self) -> Set[str]:
        """Returns the set of direct (not transitive) subobject IDs."""
        return {self.runner_image_id} if self.runner_image_id != "" else set()

    def direct_blob_ids(self) -> Set[str]:
        """Returns the set of direct (not transitive) blob IDs."""
        blob_ids = set()
        for pack in self.runfiles_packs:
            blob_ids.add(pack.blob_id)
        return blob_ids


class ModuleRepository:
    # pylint: disable=too-many-public-methods

    """Client for the Exafunction module repository."""

    def __init__(
        self,
        repository_address: str,
        dns_server: Optional[str] = None,
        test_stub: Any = None,
    ):
        """
        Creates a connection to the Exafunction module repository.

        :param repository_address: The address of the module repository.
        """
        self.stub: module_repository_pb2_grpc.ModuleRepositoryStub
        if test_stub is None:
            if dns_server is None:
                uri = repository_address
            else:
                uri = f"dns://{dns_server}/{repository_address}"
            self.channel = grpc.insecure_channel(uri)
            self.stub = module_repository_pb2_grpc.ModuleRepositoryStub(self.channel)
        else:
            self.channel = None
            self.stub = test_stub
        self._default_runner_image: Optional[ModuleRepositoryRunnerImage] = None

    def __enter__(self):
        return self

    def close(self):
        """Closes the connection to the module repository."""
        if self.channel:
            self.channel.close()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def set_default_runner_image(
        self, runner_image: Union[ModuleRepositoryRunnerImage, str]
    ):
        """
        Sets the default runner image for future module registrations by this object.

        :param runner_image: The runner image to use for future module registrations.
        """
        runner_image_obj = self._get_object_from_tag_or_id_or_object(
            runner_image, ModuleRepositoryRunnerImage
        )
        assert isinstance(runner_image_obj, ModuleRepositoryRunnerImage)
        self._default_runner_image = runner_image_obj

    def ignore_runner_image(self):
        """Deprecated, do not use."""
        warn(
            "ignore_runner_image should no longer be used and will be removed. "
            + "It is now the default behavior.",
            DeprecationWarning,
        )

    def get_all_tags_with_object_ids(self) -> Dict[str, str]:
        """
        :return: A map from all tags to their corresponding object id
        """
        start_tag = ""
        tags_with_object_ids = {}
        while True:
            req = module_repository_pb2.GetAllTagsWithObjectIdsRequest()
            req.start_tag = start_tag
            req.limit = _GET_ALL_TAGS_WITH_OBJECT_IDS_LIMIT
            resp = self.stub.GetAllTagsWithObjectIds(req)
            num_tags = len(resp.sorted_tags)
            if num_tags > 0:
                start_tag = resp.sorted_tags[-1]
            for tag, object_id in zip(resp.sorted_tags, resp.object_ids):
                tags_with_object_ids[tag] = object_id
            if num_tags < req.limit:
                break
        return tags_with_object_ids

    def get_object_id_from_tag(self, tag: str) -> str:
        """
        Gets an object id from a tag.

        :param tag: The tag to get the object id for
        :return: The object id
        """
        name, version = _parse_tag(tag)
        req = module_repository_pb2.GetObjectIdFromTagRequest()
        req.tag = _generate_tag(name, version)
        try:
            resp = self.stub.GetObjectIdFromTag(req)
        except grpc.RpcError as e:
            raise ValueError(f"Could not get object ID from tag {req.tag}") from e

        return resp.object_id

    def get_object_from_id(self, object_id: str) -> ModuleRepositoryObject:
        """
        Gets an object from an object ID.

        :param object_id: The object id to get the object for
        :return: The object
        """
        try:
            req = module_repository_pb2.GetSerializedObjectMetadataRequest()
            req.object_id = object_id
            resp = self.stub.GetSerializedObjectMetadata(req)
            serialized_metadata = resp.serialized_metadata
            object_ = ModuleRepositoryObject.from_serialized_proto(serialized_metadata)
        except grpc.RpcError:
            logging.warning(
                "Module repository does not support fetching serialized metadata."
            )
            logging.warning("Some functionality like object dumping will not work.")

            try:
                req = module_repository_pb2.GetObjectMetadataRequest()
                req.object_id = object_id
                resp = self.stub.GetObjectMetadata(req)
            except grpc.RpcError as e2:
                raise ValueError(
                    f"Could not get object metadata for object ID {object_id}"
                ) from e2

            serialized_metadata = resp.metadata.SerializeToString()
            object_ = ModuleRepositoryObject.from_serialized_proto(serialized_metadata)
            object_.override_id(object_id)

        assert object_.id == object_id
        return object_

    def get_object_from_tag(self, tag: str) -> ModuleRepositoryObject:
        """
        Gets an object from a tag.

        :param tag: The tag to get the object for
        :return: The object
        """
        object_id = self.get_object_id_from_tag(tag)
        return self.get_object_from_id(object_id)

    def add_tag(
        self, tag: str, object_to_tag: Union[str, ModuleRepositoryObject]
    ) -> None:
        """
        Adds or overwrites a tag to point to an object id.

        :param tag: The tag to add or overwrite
        :param object_to_tag: The object that the tag should point to. Can be
            provided as an object, object id or an existing tag. Note that if
            an existing tag is provided, this tag becomes a copy of that tag.
        """
        name, version = _parse_tag(tag)

        obj = self._get_object_from_tag_or_id_or_object(object_to_tag)
        add_tag_req = module_repository_pb2.AddTagForObjectIdRequest()
        add_tag_req.tag = _generate_tag(name, version)
        add_tag_req.object_id = obj.id
        self.stub.AddTagForObjectId(add_tag_req)

    def tag_exists(self, tag: str) -> bool:
        """
        Returns whether a tag exists.

        :param tag: The tag to check
        :return: Whether the tag exists
        """
        name, version = _parse_tag(tag)
        req = module_repository_pb2.GetObjectIdFromTagRequest()
        req.tag = _generate_tag(name, version)
        try:
            self.stub.GetObjectIdFromTag(req)
        except grpc.RpcError as e:
            # The module repository returns an unknown error if the object
            # tag does not exist.
            # pylint: disable=no-member
            if e.code() == grpc.StatusCode.UNKNOWN:
                return False
            raise
        return True

    def object_id_exists(self, object_id):
        """
        Returns whether an object id exists.

        :param object_id: The object id to check
        :return: Whether the object id exists
        """
        req = module_repository_pb2.GetObjectMetadataRequest()
        req.object_id = object_id
        try:
            self.stub.GetObjectMetadata(req)
            return True
        except grpc.RpcError as e:
            # The module repository returns an unknown error if the object
            # does not exist.
            # pylint: disable=no-member
            if e.code() == grpc.StatusCode.UNKNOWN:
                return False
            raise

    def register_shared_object(
        self,
        filename: str,
        tag: Optional[str] = None,
        so_name: Optional[str] = None,
    ) -> ModuleRepositorySharedObject:
        """
        Registers a shared object.

        :param filename: The filename of the shared object
        :param tag: Optional; the tag to use for the shared object
        :param so_name: Optional; the SONAME to use for the shared object
        :return: The object id of the shared object
        """
        shared_object = ModuleRepositorySharedObject()
        if so_name is None:
            so_name = os.path.basename(filename)
        shared_object.so_name = so_name

        with open(filename, "rb") as f:
            data = f.read()

        shared_object.blob_id = self._register_blob(data)

        self._register_object(shared_object, tag)
        return shared_object

    def register_runner_image(
        self,
        docker_image: str,
        tag: Optional[str] = None,
    ) -> ModuleRepositoryRunnerImage:
        """
        Registers a Docker image for the runner.

        :param docker_image: The Docker image name of the image.
            Using a Docker image name without a cryptographic digest (eg. SHA256)
            is not recommended as it is possible for the image referenced by the
            name to be modified.

            Examples:
                gcr.io/examplerepository:mytag@sha256:1234567890abcdef (recommended)
                gcr.io/examplerepository:mytag (not recommended)

        :param tag: Optional; the Exafunction tag to add for the image
        """
        runner_image = ModuleRepositoryRunnerImage()
        runner_image.image_hash = docker_image

        self._register_object(runner_image, tag)
        return runner_image

    # pylint: disable=too-many-arguments
    def register_plugin(
        self,
        runfiles_dir: str,
        shared_object_path: str,
        tag: Optional[str] = None,
        runner_image: Optional[Union[ModuleRepositoryRunnerImage, str]] = None,
        runfiles_env_var_names: Optional[List[str]] = None,
    ) -> ModuleRepositoryHermeticModulePlugin:
        """
        Registers a hermetic module plugin containing one or more native
        modules.  The hermetic module plugin contains a runfiles directory
        created from a build system like Bazel.

        :param runfiles_dir: The runfiles directory containing the module plugin.
        :param shared_object_path: The shared object path.
            This path should be relative to the runfiles directory that
            implements the module plugin.
        :param tag: Optional; the tag to use for the module plugin
        :param runner_image: Optional; the runner image for this plugin. May
            be passed in as an object, tag or object id.
            If not specified, the default runner image is used.
        :param runfiles_env_var_names: Optional; a list of environment variables
            to to expose the runfiles; defaults to ["EXAFUNCTION_RUNFILES"]
        """

        plugin = ModuleRepositoryHermeticModulePlugin()

        if os.path.isabs(shared_object_path):
            raise ValueError("shared_object_path must be a relative path")
        joined_path = os.path.join(runfiles_dir, shared_object_path)
        if not os.path.exists(joined_path):
            raise ValueError(f"{joined_path} does not exist")

        plugin.shared_object_path = shared_object_path

        if runfiles_env_var_names is None:
            runfiles_env_var_names = ["EXAFUNCTION_RUNFILES"]
        assert runfiles_env_var_names is not None
        plugin.runfiles_env_var_names.extend(runfiles_env_var_names)

        if runner_image is not None:
            runner_image_obj = self._get_object_from_tag_or_id_or_object(
                runner_image, ModuleRepositoryRunnerImage
            )
            assert isinstance(runner_image_obj, ModuleRepositoryRunnerImage)
            plugin.runner_image_id = runner_image_obj.id
        elif self._default_runner_image is not None:
            plugin.runner_image_id = self._default_runner_image.id

        runfiles_packs = self._generate_runfiles_packs(runfiles_dir)
        plugin.runfiles_packs.extend(runfiles_packs)

        self._register_object(plugin, tag)
        return plugin

    def register_hermetic_module_plugin(
        self, *args, **kwargs
    ) -> ModuleRepositoryHermeticModulePlugin:
        """Deprecated alias for register_plugin"""
        warn(
            "register_hermetic_module_plugin is deprecated; use "
            + "register_plugin instead",
            DeprecationWarning,
        )
        return self.register_plugin(*args, **kwargs)

    def _generate_runfiles_packs(
        self, directory: str, glob_list: Optional[List[str]] = None
    ) -> List[str]:
        packs: List[module_repository_pb2.RunfilesPack] = []
        small_files: List[Tuple[pathlib.Path, int]] = []

        for path in glob(directory, glob_list):
            if not os.path.isfile(path):
                continue
            file_size = path.stat().st_size
            if file_size <= _SMALL_FILE_THRESHOLD:
                small_files.append((path, file_size))
                continue

            pack = module_repository_pb2.RunfilesPack()
            pack.filenames.append(path.relative_to(directory).as_posix().encode())
            pack.offsets.append(0)
            with open(path, "rb") as f:
                pack.blob_id = self._register_blob_from_stream(f)
            packs.append(pack)

        if len(small_files) == 0:
            return packs

        pack = module_repository_pb2.RunfilesPack()
        offset = 0
        # Create a temporary file with all the small files concatenated
        with tempfile.TemporaryFile("r+b") as tmp_pack:
            for path, file_size in sorted(small_files):
                pack.filenames.append(path.relative_to(directory).as_posix().encode())
                pack.offsets.append(offset)
                offset += file_size
                with open(path, "rb") as f:
                    tmp_pack.write(f.read())
            pack.blob_id = self._register_blob_from_stream(tmp_pack)  # type: ignore

        packs.append(pack)
        return packs

    def register_plugin_with_new_runner_image(
        self,
        plugin: Union[str, ModuleRepositoryHermeticModulePlugin],
        runner_image: Union[str, ModuleRepositoryRunnerImage],
        tag: Optional[str] = None,
        override_allowed: bool = False,
    ) -> ModuleRepositoryHermeticModulePlugin:
        """
        Re-registers a hermetic module plugin with the specified runner image.

        :param plugin: The hermetic module plugin to re-register.
            May be passed in as a object, tag or object id.
        :param runner_image: The runner image to use
            May be passed in as a object, tag or object id.
        :param tag: Optional; the tag to use for the new module plugin
        :param override_allowed: By default, it is not allowed to overwrite the
            runner image on a hermetic module plugin that already has one set.
            If override_allowed is set to True, then this check is disabled.
        """

        hermetic_module_plugin_obj = self._get_object_from_tag_or_id_or_object(
            plugin, ModuleRepositoryHermeticModulePlugin
        )
        assert isinstance(
            hermetic_module_plugin_obj, ModuleRepositoryHermeticModulePlugin
        )

        if not override_allowed and hermetic_module_plugin_obj.runner_image_id:
            raise ValueError(
                "Tried to override existing runner image on "
                + f"{hermetic_module_plugin_obj} but override_allowed is False"
            )

        new_plugin_obj = hermetic_module_plugin_obj.clone()
        assert isinstance(new_plugin_obj, ModuleRepositoryHermeticModulePlugin)

        runner_image_obj = self._get_object_from_tag_or_id_or_object(
            runner_image, ModuleRepositoryRunnerImage
        )
        assert isinstance(runner_image_obj, ModuleRepositoryRunnerImage)

        # Pylint doesn't seem to know the real type of new_plugin_obj
        # pylint: disable=attribute-defined-outside-init
        new_plugin_obj.runner_image_id = runner_image_obj.id
        self._register_object(new_plugin_obj, tag)

        return new_plugin_obj

    def register_module_with_new_runner_image(
        self,
        module: Union[str, ModuleRepositoryModule],
        runner_image: Union[str, ModuleRepositoryRunnerImage],
        tag: Optional[str] = None,
        override_allowed: bool = False,
    ) -> ModuleRepositoryModule:
        """
        Re-registers a module with the specified runner image.

        :param plugin: The module to re-register.
            May be passed in as a object, tag or object id.
        :param runner_image: The runner image to use
            May be passed in as a object, tag or object id.
        :param tag: Optional; the tag to use for the new module
        :param override_allowed: By default, it is not allowed to overwrite the
            runner image on a hermetic module plugin that already has one set.
            If override_allowed is set to True, then this check is disabled.
        """

        module_obj = self._get_object_from_tag_or_id_or_object(
            module, ModuleRepositoryModule
        )
        assert isinstance(module_obj, ModuleRepositoryModule)

        if module_obj.hermetic_module_plugin_id is None:
            raise ValueError("Cannot override runner image of builtin module")

        new_plugin_obj = self.register_plugin_with_new_runner_image(
            module_obj.hermetic_module_plugin_id,
            runner_image,
            override_allowed=override_allowed,
        )

        new_module_obj = module_obj.clone()
        assert isinstance(new_module_obj, ModuleRepositoryModule)

        # Pylint doesn't seem to know the real type of new_module_obj
        # pylint: disable=attribute-defined-outside-init
        new_module_obj.hermetic_module_plugin_id = new_plugin_obj.id
        self._register_object(new_module_obj, tag)
        return new_module_obj

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    def register_native_module(
        self,
        module_tag: str,
        module_class: str,
        context_data: bytes = bytes(),
        shared_objects: Optional[List[Union[ModuleRepositorySharedObject, str]]] = None,
        plugin: Optional[Union[ModuleRepositoryHermeticModulePlugin, str]] = None,
        hermetic_module_plugin: Optional[
            Union[ModuleRepositoryHermeticModulePlugin, str]
        ] = None,
        config: Optional[Dict[str, bytes]] = None,
    ) -> ModuleRepositoryModule:
        """
        Registers a native (C/C++) module.

        :param module_tag: The tag to use for the module
        :param module_class: The class name of the module
        :param context_data: Optional; the module context data to use for the module
        :param plugin: Optional; the hermetic module plugin
            that the module depends on. May be passed in as an object, tag or
            object ID.
        :param hermetic_module_plugin: Deprecated; same as plugin
        :param shared_objects: Optional; the list of shared objects that the
            module depends on. May be passed in as objects, tags or object IDs.
        :param config: Optional; the module configuration to use for the module
        :return: The object id of the module
        """

        module_name, _ = _parse_tag(module_tag)

        module = ModuleRepositoryModule()
        module.module_name = module_name
        module.module_class = module_class
        if shared_objects is not None:
            for shared_object in shared_objects:
                shared_object_obj = self._get_object_from_tag_or_id_or_object(
                    shared_object, ModuleRepositorySharedObject
                )
                assert isinstance(shared_object_obj, ModuleRepositorySharedObject)
                module.shared_object_ids.append(shared_object_obj.id)

        if hermetic_module_plugin is not None:
            warn(
                "The hermetic_module_plugin parameter is deprecated for "
                + "register_native_module and will be removed in a future "
                + "release. Please use the plugin parameter instead, which "
                + "has the same behavior.",
                DeprecationWarning,
            )
            if plugin is not None:
                raise ValueError(
                    "Cannot specify both plugin and hermetic_module_plugin"
                )
            plugin = hermetic_module_plugin

        if plugin is not None:
            hermetic_module_plugin_obj = self._get_object_from_tag_or_id_or_object(
                plugin, ModuleRepositoryHermeticModulePlugin
            )
            assert isinstance(
                hermetic_module_plugin_obj, ModuleRepositoryHermeticModulePlugin
            )
            module.hermetic_module_plugin_id = hermetic_module_plugin_obj.id

        if config is not None:
            module.config.update(config)

        blob_id = self._register_blob(context_data)
        module.blob_id = blob_id

        self._register_object(module, module_tag)
        return module

    # pylint: disable=too-many-arguments
    def register_py_module(
        self,
        module_tag: str,
        module_class: str,
        module_import: str,
        module_context_class: str = "BaseModuleContext",
        module_context_import: str = "exa",
        pip_requirements_list: Optional[List[str]] = None,
        pip_requirements_file: Optional[str] = None,
        context_data: bytes = bytes(),
        config: Optional[Dict[str, bytes]] = None,
        **kwargs,
    ) -> ModuleRepositoryModule:
        """
        Registers a Python module.

        For internal use only.
        """

        full_config = {
            "_py_module_type": b"builtin",
            "_py_module_context_import": module_context_import.encode(),
            "_py_module_context_class": module_context_class.encode(),
            "_py_module_import": module_import.encode(),
            "_py_module_class": module_class.encode(),
        }

        pip_requirements = b""
        if pip_requirements_list is not None and pip_requirements_file is not None:
            raise ValueError(
                "Both pip_requirements_file and pip_requirements_list cannot be set"
            )
        if pip_requirements_list is not None:
            pip_requirements = "\n".join(pip_requirements_list).encode()
        elif pip_requirements_file is not None:
            with open(pip_requirements_file, "rb") as f:
                pip_requirements = f.read()
        full_config[_PY_MODULE_PIP_REQUIREMENTS_CONFIG_KEY] = pip_requirements

        if config is not None:
            for k, v in config.items():
                if k in full_config:
                    raise ValueError(
                        f"Configuration key {k} is not allowed in register_py_module"
                    )
                full_config[k] = v

        return self.register_native_module(
            module_tag,
            "PyModule",
            context_data=context_data,
            config=full_config,
            **kwargs,
        )

    def register_py_interpreter_module(
        self,
        module_tag: str,
        pip_requirements_list: Optional[List[str]] = None,
        pip_requirements_file: Optional[str] = None,
        **kwargs,
    ) -> ModuleRepositoryModule:
        """
        Registers a python interepreter module.

        :param module_tag: The tag to use for the module
        :param pip_requirements_list: Optional; list of strings for pip requirements.
            Example: ["boto3", "joblib==1.1.0"]
        :param pip_requirements_file: Optional; file containing pip requirements.
            Either requirements_list or a requirements_file must be provided.
        :return: The object id of the module
        """
        return self.register_py_module(
            module_tag,
            module_class="InterpreterModule",
            module_import="exa.py_interpreter_module",
            pip_requirements_list=pip_requirements_list,
            pip_requirements_file=pip_requirements_file,
            **kwargs,
        )

    # pylint: disable=too-many-arguments
    def register_tf_savedmodel(
        self,
        module_tag: str,
        savedmodel_dir: str,
        use_tensorflow_cc: bool = True,
        signature: Optional[str] = None,
        tags: Optional[str] = None,
        **kwargs,
    ) -> ModuleRepositoryModule:
        """
        Registers a TensorFlow SavedModel.

        :param module_tag: The tag to use for the module
        :param savedmodel_dir: The directory containing the TensorFlow SavedModel
        :param use_tensorflow_cc: Whether to use the C++ TensorFlow implementation
        :param signature: Optional; the SavedModel serving signature to use
        :param tags: Optional; the set of SavedModel serving tags to use
        :param kwargs: Additional arguments to pass to register_native_module
        :return: The object id of the module
        """
        savedmodel_buffer = _zip_directory(savedmodel_dir)

        config = {}
        if signature is not None:
            config["_tf_signature"] = signature.encode()
        if tags is not None:
            config["_tf_tags"] = tags.encode()

        if not use_tensorflow_cc:
            raise ValueError("use_tensorflow_cc must be set to True")
        return self.register_native_module(
            module_tag,
            "TensorFlowModule",
            context_data=savedmodel_buffer,
            config=config,
            **kwargs,
        )

    def register_torchscript(
        self,
        module_tag: str,
        torchscript_file: str,
        input_names: List[str],
        output_names: List[str],
        **kwargs,
    ) -> ModuleRepositoryModule:
        """
        Registers a TorchScript model.

        :param module_tag: The tag to use for the module
        :param torchscript_file: The file containing the TorchScript model
        :param input_names: The names of the input tensors. Must match the TorchScript
            model. If a specific input is actually a dictionary from int64 to tensor,
            prefix it with `"int64map:"` (e.g., `"int64map:foo"` instead of `"foo"`).
        :param output_names: The names of the output tensors. Must match the
            TorchScript model.
        :param kwargs: Additional arguments to pass to register_native_module
        :return: The object id of the module
        """
        if any("," in x for x in input_names):
            raise ValueError("TorchScript input names may not contain commas")
        if any("," in x for x in output_names):
            raise ValueError("TorchScript output names may not contain commas")

        config = {
            "_torchscript_input_names": ",".join(input_names).encode(),
            "_torchscript_output_names": ",".join(output_names).encode(),
        }

        with open(torchscript_file, "rb") as f:
            data = f.read()

        return self.register_native_module(
            module_tag,
            "TorchModule",
            context_data=data,
            config=config,
            **kwargs,
        )

    def register_tensorrt_engine(
        self,
        module_tag: str,
        engine_path: str,
        plugin_v1_factory_symbol: Optional[str] = None,
        **kwargs,
    ) -> ModuleRepositoryModule:
        """
        Registers a serialized TensorRT engine.

        :param module_tag: The tag to use for the module
        :param engine_path: The path to the serialized TensorRT engine
        :param plugin_v1_factory_symbol: Optional; the symbol of the plugin
            factory function
        :param kwargs: Additional arguments to pass to register_native_module
        :return: The object id of the module
        """
        with open(engine_path, "rb") as f:
            data = f.read()

        config = {}
        if plugin_v1_factory_symbol is not None:
            config["_trt_plugin_v1_factory_symbol"] = plugin_v1_factory_symbol.encode()

        return self.register_native_module(
            module_tag,
            "TensorRTModule",
            context_data=data,
            config=config,
            **kwargs,
        )

    def register_onnx(
        self,
        module_tag: str,
        onnx_file: str,
        **kwargs,
    ) -> ModuleRepositoryModule:
        """
        Registers an ONNX model.

        :param module_tag: The tag to use for the module
        :param onnx_file: The file containing the ONNX model
        :param kwargs: Additional arguments to pass to register_native_module
        :return: The object id of the module
        """
        with open(onnx_file, "rb") as f:
            data = f.read()

        return self.register_py_module(
            module_tag,
            "OnnxModule",
            "exa.py_onnx_module",
            "OnnxModuleContext",
            "exa.py_onnx_module",
            context_data=data,
            **kwargs,
        )

    def register_function_wrapper_module(
        self,
        module_tag: str,
        module_class: str,
        runfiles_dir: str,
        shared_object_path: str,
        runner_image: Optional[str] = None,
        runfiles_env_var_names: Optional[List[str]] = None,
        **kwargs,
    ) -> ModuleRepositoryModule:
        """
        Registers a function wrapper shared object and runfiles directory as a
        module.

        :param module_tag: The tag to use for the module
        :param module_class: The class name of the module
        :param runfiles_dir: The runfiles directory
            This directory should contain the function wrapper shared object.
        :param shared_object_path: The path to the function wrapper shared object.
            This path should be relative to the runfiles directory.
        :param runner_image: Optional; the runner image for this plugin. May
            be passed in as an object, tag or object id.
            If not specified, the default runner image is used.
        :param runfiles_env_var_names: Optional; a list of environment variables
            to to expose the runfiles; defaults to ["EXAFUNCTION_RUNFILES"]
        :return: An object representing the plugin
        """
        plugin = self.register_plugin(
            runfiles_dir,
            shared_object_path,
            runner_image=runner_image,
            runfiles_env_var_names=runfiles_env_var_names,
        )
        return self.register_native_module(
            module_tag,
            module_class=module_class,
            plugin=plugin,
            **kwargs,
        )

    def register_hermetic_function_wrapper_module(
        self, *args, **kwargs
    ) -> ModuleRepositoryModule:
        """Deprecated alias for register_function_wrapper_module"""
        warn(
            "register_hermetic_function_wrapper_module is deprecated; use "
            + "register_function_wrapper_module instead",
            DeprecationWarning,
        )
        return self.register_function_wrapper_module(*args, **kwargs)

    def clear(self):
        """
        Clears the module repository.

        Do not use.
        """
        if not _module_repository_clear_allowed:
            raise PermissionError("Can't clear module repository")
        req = module_repository_pb2.ClearDataRequest()
        self.stub.ClearData(req)

    def _blob_id_exists(self, blob_id):
        req = module_repository_pb2.ExistsBlobRequest()
        req.blob_id = blob_id
        resp = self.stub.ExistsBlob(req)
        return resp.exists

    def _get_object_from_tag_or_id_or_object(
        self,
        tag_or_id_or_object: Union[str, ModuleRepositoryObject],
        expected_type: Optional[type] = None,
    ) -> ModuleRepositoryObject:
        if isinstance(tag_or_id_or_object, str):  # Tag or ID
            if tag_or_id_or_object.startswith("@"):  # ID
                object_id = tag_or_id_or_object
            else:  # Tag
                object_id = self.get_object_id_from_tag(tag_or_id_or_object)
            object_ = self.get_object_from_id(object_id)
        else:  # Object
            object_ = tag_or_id_or_object

        if expected_type is not None and not isinstance(object_, expected_type):
            raise ValueError(
                f"Expected object of type {expected_type}, got {type(object_)} instead"
            )
        return object_

    def _register_blob_from_stream(self, stream: IO[bytes]) -> str:
        stream.seek(0)
        blob_id = _generate_data_id(stream)
        # See if this blob already exists, if so we can skip pushing
        if self._blob_id_exists(blob_id):
            return blob_id

        stream.seek(0)

        def generate_data_chunks():
            while True:
                req = module_repository_pb2.RegisterBlobStreamingRequest()
                req.data_chunk = stream.read(_REGISTER_BLOB_CHUNK_SIZE)
                if len(req.data_chunk) == 0:
                    return
                yield req

        data_chunk_iterator = generate_data_chunks()
        resp = self.stub.RegisterBlobStreaming(data_chunk_iterator)
        if blob_id != resp.blob_id:
            raise AssertionError(
                "Returned blob id does not match locally computed value"
            )
        return resp.blob_id

    def _register_blob(self, data_bytes: bytes) -> str:
        return self._register_blob_from_stream(io.BytesIO(data_bytes))

    def _save_blob_to_stream(self, blob_id: str, stream: IO[bytes]) -> None:
        stream.seek(0)
        req = module_repository_pb2.GetBlobRequest()
        req.blob_id = blob_id
        for resp in self.stub.GetBlob(req):
            stream.write(resp.data_chunk)

    def _register_object(
        self, object_: ModuleRepositoryObject, tag: Optional[str] = None
    ) -> None:
        # Serialize and generate the object id
        object_._freeze()  # pylint: disable=protected-access

        # See if this object already exists, if so we can skip pushing
        if not self.object_id_exists(object_.id):
            req = module_repository_pb2.RegisterObjectRequest()
            req.serialized_metadata = object_.serialized
            resp = self.stub.RegisterObject(req)
            if object_.id != resp.object_id:
                raise AssertionError(
                    "Returned object id does not match locally computed value"
                )
        if tag is not None:
            self.add_tag(tag, object_.id)

    def _ping(self):
        try:
            resp = self.stub.HealthCheck(module_repository_pb2.HealthCheckRequest())
        except grpc.RpcError:
            return False
        return resp.healthy

    def _transitive_objects(
        self, obj: ModuleRepositoryObject
    ) -> Dict[str, ModuleRepositoryObject]:
        if obj.is_mutable():
            raise RuntimeError("Cannot compute transitive objects of mutable object.")
        objects = {obj.id: obj}
        for object_id in obj.direct_subobject_ids():
            subobject = self.get_object_from_id(object_id)
            objects.update(self._transitive_objects(subobject))
        return objects

    def save_zip(
        self,
        path: str,
        objects_to_save: List[Union[ModuleRepositoryObject, str]],
        allow_overwrite=False,
        compression=zipfile.ZIP_STORED,
        compresslevel=None,
    ) -> None:
        """
        Saves the specified objects and tags from the module repository into a
        zipfile that can be restored using load_zip.

        :param path: The path to write the zipfile.
        :param objects_to_save: A list of objects, object IDs or tags to save
            into the zipfile.
        :param allow_overwrite: Whether to allow overwriting the zipfile.
        :param compression: Compression to use for the zipfile; defaults to none.
        """

        if os.path.exists(path):
            if allow_overwrite:
                os.remove(path)
            else:
                raise FileExistsError(f"File {path} already exists")

        # Compute all transitive objects
        all_objects: Dict[str, ModuleRepositoryObject] = {}
        tags: Dict[str, str] = {}
        for obj in objects_to_save:
            object_ = self._get_object_from_tag_or_id_or_object(obj)
            if isinstance(obj, str) and not obj.startswith("@"):  # is a tag
                canonical_tag = _generate_tag(*_parse_tag(obj))
                tags[canonical_tag] = object_.id
            all_objects.update(self._transitive_objects(object_))

        # Compute all blobs
        blob_ids: Set[str] = set()
        for object_ in all_objects.values():
            blob_ids.update(object_.direct_blob_ids())

        logging.info(
            "Saving %d objects, %d tags and %d blobs to %s",
            len(all_objects),
            len(tags),
            len(blob_ids),
            path,
        )

        # Generate a protobuf with all the objects
        # Also generate a human readable manifest for debugging purposes
        zipdata = module_repository_pb2.SavedMetadata()
        manifest = []
        for tag in sorted(tags):
            zipdata.tags[tag] = tags[tag]
            manifest.append(f"tag: {tag} -> {tags[tag]}")
        for object_id in sorted(all_objects):
            object_ = all_objects[object_id]
            zipdata.serialized_metadatas.append(object_.serialized)
            manifest.append(f"object: {object_}")
        for blob_id in sorted(blob_ids):
            zipdata.blob_ids.append(blob_id)
            manifest.append(f"blob: {blob_id}")

        with zipfile.ZipFile(
            path, mode="w", compression=compression, compresslevel=compresslevel
        ) as arc:
            arc.writestr(f"{_ZIPFILE_PREFIX}/data.pb", zipdata.SerializeToString())
            arc.writestr(f"{_ZIPFILE_PREFIX}/manifest", "\n".join(manifest))
            for blob_id in sorted(blob_ids):
                with tempfile.NamedTemporaryFile(mode="w+b") as f:
                    self._save_blob_to_stream(blob_id, f)
                    f.flush()
                    arc.write(f.name, arcname=f"{_ZIPFILE_PREFIX}/blobs/{blob_id}")

        zipfile_size = os.path.getsize(path)
        logging.info("Saved %d bytes to %s", zipfile_size, path)

    def load_zip(
        self, path: str, load_tags: bool = True
    ) -> Tuple[List[ModuleRepositoryObject], List[str]]:
        """
        Loads the specified zipfile into the repository, returning all loaded
        objects and tags. Note that this will overwrite any existing tags.

        :param path: The path to read the zipfile.
        :param load_tags: Whether to load tags from the zipfile, overwriting
            existing tags if they exist. Defaults to true.
        :return: A tuple with a list of all objects and a list of all
            tags pairs in the zip file (even if load_tags == False).
        """

        zipfile_size = os.path.getsize(path)
        logging.info("Loading %d bytes from %s", zipfile_size, path)

        with zipfile.ZipFile(path, mode="r") as arc:
            # Read data
            with tempfile.TemporaryDirectory() as tmpdir:
                arcpath = _ZIPFILE_PREFIX + "/data.pb"
                arc.extract(arcpath, tmpdir)
                with open(os.path.join(tmpdir, arcpath), "rb") as f:
                    zipdata = module_repository_pb2.SavedMetadata()
                    zipdata.ParseFromString(f.read())

            # Read and register blobs
            for blob_id in zipdata.blob_ids:
                with tempfile.TemporaryDirectory() as tmpdir:
                    arcpath = f"{_ZIPFILE_PREFIX}/blobs/{blob_id}"
                    arc.extract(arcpath, tmpdir)
                    with open(os.path.join(tmpdir, arcpath), "rb") as f:
                        self._register_blob_from_stream(f)

        # Register objects
        objects = []
        for serialized_metadata in zipdata.serialized_metadatas:
            object_ = ModuleRepositoryObject.from_serialized_proto(serialized_metadata)
            self._register_object(object_)
            objects.append(object_)

        # Register tags
        tags = []
        for tag in zipdata.tags:
            if load_tags:
                self.add_tag(tag, zipdata.tags[tag])
            tags.append(tag)

        logging.info(
            "Loaded %d objects, %d tags and %d blobs from %s",
            len(zipdata.serialized_metadatas),
            len(zipdata.tags) if load_tags else 0,
            len(zipdata.blob_ids),
            path,
        )

        return objects, tags

    def load_zip_from_url(
        self, url: str, load_tags: bool = True
    ) -> Tuple[List[ModuleRepositoryObject], List[str]]:
        """
        Loads the specified zipfile into the repository from a URL, returning
        all loaded objects and tags.

        :param url: A URL to a zipfile.
        :param load_tags: Whether to load tags from the zipfile, overwriting
            existing tags if they exist. Defaults to true.
        :return: A tuple with a list of all loaded objects and a list of all tags
        """
        with tempfile.NamedTemporaryFile(mode="w+b") as f:
            with requests.get(url, stream=True) as r:
                with open(f.name, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
            return self.load_zip(f.name, load_tags)


def _parse_tag(tag: str) -> Tuple[str, str]:
    for c in tag:
        char_idx = ord(c)
        if char_idx < 0x20 or char_idx > 0x7E:
            raise ValueError(
                "Module tag contains non-printable or non-ASCII characters"
            )

    if ":" in tag:
        name_and_version = tag.split(":")
        if len(name_and_version) != 2:
            raise ValueError(f"Invalid module tag {tag}")
        name = name_and_version[0]
        version = name_and_version[1]
    else:
        name = tag
        version = "latest"
    return name, version


def _generate_tag(name: str, version: Optional[str] = None) -> str:
    if version is None:
        return name + "latest"
    return f"{name}:{version}"


def _generate_data_id(stream: IO[bytes]) -> str:
    m = hashlib.sha256()
    while True:
        chunk = stream.read(_REGISTER_BLOB_CHUNK_SIZE)
        if len(chunk) == 0:
            break
        m.update(chunk)
    digest = m.digest()[:15]  # Keep only 120 bits
    return "@" + base64.urlsafe_b64encode(digest).decode("utf-8")


def _make_zip_info(filename, arcname=None):
    """Construct a ZipInfo, but without reading the file timestamp"""
    if isinstance(filename, os.PathLike):
        filename = os.fspath(filename)
    st = os.stat(filename)
    isdir = stat.S_ISDIR(st.st_mode)
    date_time = (1980, 1, 1, 0, 0, 0)

    # Create ZipInfo instance to store file information
    if arcname is None:
        arcname = filename
    arcname = os.path.normpath(os.path.splitdrive(arcname)[1])
    while arcname[0] in (os.sep, os.altsep):
        arcname = arcname[1:]
    if isdir:
        arcname += "/"
    zinfo = zipfile.ZipInfo(arcname, date_time)
    zinfo.external_attr = (st.st_mode & 0xFFFF) << 16  # Unix attributes
    if isdir:
        zinfo.file_size = 0
        zinfo.external_attr |= 0x10  # MS-DOS directory flag
    else:
        zinfo.file_size = st.st_size

    return zinfo


def glob(directory: str, glob_list: Optional[List[str]] = None) -> List[pathlib.Path]:
    """
    Returns a list of file and directory paths in the given directory,
    optionally using the list of glob patterns. If the list is not provided then
    all files and directories are returned.

    :param directory: The directory to search
    :param glob_list: A list of glob patterns to use
    :return: A list of file and directory paths matching the glob patterns
    """

    # Walk directories to make sure we have permissions to read them
    # Otherwise we may miss files when globbing
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"No such directory {directory}")
    if not os.access(directory, os.R_OK):
        raise PermissionError(f"Cannot access {directory}")
    for dirpath, dirnames, _ in os.walk(directory):
        for dirname in dirnames:
            path = os.path.join(dirpath, dirname)
            if not os.access(path, os.R_OK):
                raise PermissionError(f"Cannot access {path}")

    if glob_list is None:
        glob_list = ["**/*"]  # Include everything

    directory_path = pathlib.Path(directory)
    glob_files_set: Set[pathlib.Path] = set()
    for glob_pattern in glob_list:
        files = directory_path.glob(glob_pattern)
        glob_files_set.update(files)

    return list(sorted(glob_files_set))  # Ensure file order is deterministic


def _zip_directory(directory: str, glob_list: Optional[List[str]] = None) -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a") as zipf:
        for path in glob(directory, glob_list):
            if not os.path.isfile(path):
                continue
            arcname = os.path.relpath(path, directory)
            zinfo = _make_zip_info(path, arcname)
            with open(path, "rb") as f:
                zipf.writestr(zinfo, f.read(), zipfile.ZIP_STORED)
    return zip_buffer.getvalue()


def get_bazel_runfiles_root():
    """Get the Bazel runfiles directory root"""
    runfiles_root = os.environ.get("RUNFILES_DIR")
    if runfiles_root is None:
        runfiles_manifest = os.environ.get("RUNFILES_MANIFEST_FILE")
        assert runfiles_manifest.endswith("_manifest")
        runfiles_root = runfiles_manifest[: -len("_manifest")]
    assert runfiles_root is not None
    return runfiles_root
