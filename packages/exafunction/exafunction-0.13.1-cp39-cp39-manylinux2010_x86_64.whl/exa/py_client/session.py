# Copyright Exafunction, Inc.
"""Defines the Session class."""

from dataclasses import dataclass
import inspect
import sys
from typing import Dict, List, Optional, Sequence

import numpy as np

from exa import _C
from exa.common_pb.common_pb2 import IpcStatsResponse
from exa.common_pb.common_pb2 import ValueMetadata
from exa.py_client.module import Module
from exa.py_client.profiler import Profiler
from exa.py_value.value import Value
from exa.py_value.value import ValueCompressionType
from exa.session_pb import session_pb2


@dataclass
class ModuleContextSpec:
    """Specification for a single module context"""

    module_tag: Optional[str] = None
    """The module tag. Should be left empty if module hash is specified."""
    module_hash: Optional[str] = None
    """The module hash. Should be left empty if module tag is specified."""
    cpu_memory_limit_mb: int = 0
    """
    The CPU memory limit for the module context in MiB. The interpretation of this is
    module-dependent.
    """
    gpu_memory_limit_mb: int = 0
    """
    The GPU memory limit for the module context in MiB. The interpretation of this is
    module-dependent.
    """
    ignore_exec_serialize: bool = False
    """
    If set to true, we always run modules in this module context without
    serializing with other "RunMethod" calls even if serialize_all is set to
    true in the config file.
    """
    config_map: Optional[Dict[str, str]] = None
    """
    Extra configuration options. These depend on the type of module loaded.
    These are merged with and can override the config map specified when
    registering the module (eg. through ModuleRepository.register_native_module).
    """
    per_runner_replicas: int = 0
    """
    The number of replicas that should be created on a single runner. If a value of 0 is
    provided, it will be treated as if the value was 1. Having > 1 replica is undefined
    behavior for stateful modules.
    """

    module_server_uid: Optional[str] = None
    """
    This can be used to force instantiation of a separate module server process.
    """

    def _to_proto(self) -> session_pb2.ModuleContextSpec:
        return session_pb2.ModuleContextSpec(
            module_tag=self.module_tag,
            module_hash=self.module_hash,
            cpu_memory_limit_mb=self.cpu_memory_limit_mb,
            gpu_memory_limit_mb=self.gpu_memory_limit_mb,
            ignore_exec_serialize=self.ignore_exec_serialize,
            config_map=self.config_map,
            per_runner_replicas=self.per_runner_replicas,
            module_server_uid=self.module_server_uid,
        )


@dataclass
class PlacementGroupSpec:
    """Specification for a placement group.

    A placement group contains one or more module contexts that will be placed on the
    same runner.
    """

    module_contexts: List[ModuleContextSpec]
    """List of module contexts within this placement group"""

    value_pool_size: int = 100 * 1024 * 1024
    """Remote memory pool size (default is 100 MiB)"""

    runner_fraction: float = 0.1
    """Estimated fraction of a runner that will be consumed by this placement
    group in terms of compute resources. This is used by the autoscaler as
    a hint for how many sessions can be placed on a single runner for this
    placement group."""

    constraint_config: Optional[Dict[str, str]] = None
    """Constraint configuration used to constrain runner (i.e. where it runs,
    resources used). These configurations can be used to override the default
    service config map."""

    load_balancing_enabled: bool = False
    """If set to true, load balancing is enabled. The load from each client
    on this placement group will be distributed evenly across multiple runners.
    Note that the scheduler must also have load balancing enabled in the config
    map, or else this setting is ignored."""

    autoscaling_enabled: bool = False
    """If set to true, autoscaling is enabled. The system will measure the
    actual load from each client on this placement group and adjust the number
    of clients per runner accordingly. Note that the scheduler must also have
    autoscaling enabled in the config map, or else this setting is ignored."""

    migration_disabled: bool = False
    """If set to true, migration is disabled. In this case, the system will not
    migrate the placement group, which is usually done to scale down
    underutilized runners. Migration is implicitly disabled if disable_fault_tolerance
    is set to true for the Session. This flag should only be set if the modules
    in the placement group are very expensive to migrate."""

    aggressive_migration: bool = False
    """If set to true, subsession migrations will occur more frequently"""

    max_cpu_pool_size: int = 0
    """If this is set, defines the total CPU memory pool size for the placement group.
    Otherwise, the value will default to
    `ceil(value_pool_size / runner_fraction)`. It must be the case that
    `max_cpu_pool_size >= max_gpu_pool_size >= value_pool_size`."""

    max_gpu_pool_size: int = 0
    """If this is set, defines the total GPU memory pool size for the placement group.
    Otherwise, the value will default to
    `ceil(value_pool_size / runner_fraction)`. It must be the case that
    `max_cpu_pool_size >= max_gpu_pool_size >= value_pool_size`."""

    default_compression_type: ValueCompressionType = ValueCompressionType.UNCOMPRESSED
    """Default compression type for all values being pushed to the placement group.
    If this value is set to something other than UNCOMPRESSED, it will overwrite the
    session's defualt compression type."""

    runner_shm_message_queue_block_size: int = 4096
    """Controls the message queue size used by the runner for this placement group."""

    max_concurrent_run_method_calls: int = 0
    """
    Controls the number of concurrent run method calls. If set to 0, there is no limit.
    """

    max_gpu_locked_memory: int = 0
    """If this is set, defines the maximum locked memory per session. It must be the
    case that `max_gpu_locked_memory <= max_gpu_pool_size`."""

    per_session_cpu_allocator: bool = False
    """If true, each session will be allocated its own chunk of memory in CPU pool,
    equivalent to value_pool_size, and not be allowed to exceed it. It is the user's
    responsibility to set an appropriate runner_fraction to prevent the sum of
    value_pool_size across sessions to exceed max_cpu_pool_size. This should only be
    done with applications that want deterministic memory allocation failures because
    this is a pessimization; concurrent sessions can never share allocated regions if
    this is true."""

    def _to_proto(self, name) -> session_pb2.PlacementGroupSpec:
        return session_pb2.PlacementGroupSpec(
            name=name,
            # pylint: disable=protected-access
            module_contexts=[mc._to_proto() for mc in self.module_contexts],
            value_pool_size=self.value_pool_size,
            runner_fraction=self.runner_fraction,
            constraint_config=self.constraint_config,
            load_balancing_enabled=self.load_balancing_enabled,
            autoscaling_enabled=self.autoscaling_enabled,
            migration_disabled=self.migration_disabled,
            aggressive_migration=self.aggressive_migration,
            max_cpu_pool_size=self.max_cpu_pool_size,
            max_gpu_pool_size=self.max_gpu_pool_size,
            default_compression_type=_C.Session.value_compression_type_to_proto(
                self.default_compression_type
            ),
            # pylint: disable=line-too-long
            runner_shm_message_queue_block_size=self.runner_shm_message_queue_block_size,
            max_concurrent_run_method_calls=self.max_concurrent_run_method_calls,
            max_gpu_locked_memory=self.max_gpu_locked_memory,
            per_session_cpu_allocator=self.per_session_cpu_allocator,
        )


# Hack to override inspect.getfile to work in IPython
def _new_getfile(obj, _old_getfile=inspect.getfile):
    if not inspect.isclass(obj):
        return _old_getfile(obj)

    # Lookup by parent module (as in current inspect)
    if hasattr(obj, "__module__"):
        object_ = sys.modules.get(obj.__module__)
        if hasattr(object_, "__file__"):
            return object_.__file__

    # If parent module is __main__, lookup by methods (NEW)
    for _, member in inspect.getmembers(obj):
        if (
            inspect.isfunction(member)
            and obj.__qualname__ + "." + member.__name__ == member.__qualname__
        ):
            return inspect.getfile(member)
    raise TypeError(f"Source for {obj!r} not found")


inspect.getfile = _new_getfile


class Session:
    """The Session object manages all Exafunction resources for a given session."""

    def __init__(
        self,
        scheduler_address: str,
        external_scheduler: bool = False,
        placement_groups: Optional[Dict[str, PlacementGroupSpec]] = None,
        disable_fault_tolerance: bool = False,
        profile_log_file_path: str = "",
        local_pool_size: int = 2 * 1024 * 1024 * 1024,
        pin_local_pool: bool = False,
        # pylint: disable=line-too-long
        default_compression_type: ValueCompressionType = ValueCompressionType.UNCOMPRESSED,
        save_run_method_history: bool = False,
        colocated_with_runner: bool = False,
        tmp_dir: str = "/tmp/exafunction/session",
        runner_rpc_retry_timeout_seconds: float = -1.0,
        module_repository_rpc_retry_timeout_seconds: float = 3.0,
        new_session_timeout_seconds: float = 3600.0 * 24,
        job_id: str = "",
        runner_grpc_timeout_seconds: float = 600.0,
        dns_server: str = "",
        daemon_shm_message_queue_block_size=4096,
        unique_id: str = "",
        autostart_daemon: bool = True,
        session_suspend_timeout_seconds=0.0,
        existing_session_id: Optional[int] = None,
    ):
        """
        Creates an Exafunction session.

        :param scheduler_address:
            Exafunction scheduler address (eg. "scheduler-service:1234").
        :param external_scheduler:
            Set to true if client is not running in the same Kubernetes cluster as the
            scheduler.
        :param placement_groups: The placement groups required by this session.
        :param disable_fault_tolerance: Whether to run with fault tolerance.
        :param profile_log_path: Optional path to log profiling stats.
        :param local_pool_size: Maximum allocation size for local values.
        :param pin_local_pool:
            Whether to pin the memory (mainly useful for CUDA applications).
        :param default_compression_type:
            Default compression used for all values sent from client.
        :param save_run_method_history:
            If set to true, the scheduler saves metadata for the history of all
            RunMethod calls. There is performance overhead if this is set to true (i.e.
            from hashing of input values).
        :param colocated_with_runner:
            Specifies whether runner and client are colocated and can pass data over
            shared memory.
        :param tmp_dir: Temporary directory for session data.
        :param runner_rpc_retry_timeout_seconds:
            RPC timeout for runners with retrying. If less than 0, we never retry these
            RPCs.
        :param module_repository_rpc_retry_timeout_seconds:
            RPC timeout for module repository. If less than 0, we never retry these
            RPCs.
        :param new_session_timeout_seconds:
            RPC timeout for scheduler new session requests. Defaults to 1 day.
        :param job_id:
            Client job identifier for the session which can be used to aggregate runner
            usage by client job.
        :param runner_grpc_timeout_seconds:
            Grpc retry timeout for the runner. Defaults to 10 minutes.
        :param daemon_shm_message_queue_block_size:
            Controls the message queue size used by the client with the daemon.
        :param unique_id:
            Alphanumeric unique ID used to distinguish each job from others. Optional
            unless the client is multi-process, or there are multiple sessions in one
            machine.
        :param existing_session_id:
            If specified, the session will be created from an existing session.
        :param autostart_daemon: If set to false, the daemon must be manually started.
        :param session_suspend_timeout_seconds:
            Timeout before we automatically suspend the session, in seconds.
            Default value of 0 indicates we do not automatically suspend the session.
        """
        if placement_groups is None:
            placement_groups = {}
        if not isinstance(default_compression_type, ValueCompressionType):
            raise TypeError(
                "default_compression_type must be of type ValueCompressionType"
            )
        self.session_config = session_pb2.SessionConfig(
            scheduler_address=scheduler_address,
            external_scheduler=external_scheduler,
            placement_groups=[v._to_proto(name=k) for k, v in placement_groups.items()],
            disable_fault_tolerance=disable_fault_tolerance,
            profile_log_file_path=profile_log_file_path,
            local_pool_size=local_pool_size,
            pin_local_pool=pin_local_pool,
            default_compression_type=_C.Session.value_compression_type_to_proto(
                default_compression_type
            ),
            save_run_method_history=save_run_method_history,
            colocated_with_runner=colocated_with_runner,
            runner_rpc_retry_timeout_seconds=runner_rpc_retry_timeout_seconds,
            # pylint: disable=line-too-long
            module_repository_rpc_retry_timeout_seconds=module_repository_rpc_retry_timeout_seconds,
            new_session_timeout_seconds=new_session_timeout_seconds,
            tmp_dir=tmp_dir,
            job_id=job_id,
            runner_grpc_timeout_seconds=runner_grpc_timeout_seconds,
            dns_server=dns_server,
            daemon_shm_message_queue_block_size=daemon_shm_message_queue_block_size,
            unique_id=unique_id,
            autostart_daemon=autostart_daemon,
            session_suspend_timeout_seconds=session_suspend_timeout_seconds,
        )

        self._c = _C.Session(
            self.session_config.SerializeToString(), existing_session_id
        )

    @property
    def id(self) -> int:
        """Returns the session ID.

        :return: The session ID.
        """
        self._check_closed()
        return self._c.session_id

    def close(self):
        """Closes the session. Using the context manager interface is preferred."""
        self._c = None

    def suspend(self):
        """Suspends the session."""
        self._check_closed()
        self._c.suspend()

    def resume(self):
        """Resumes the session."""
        self._check_closed()
        self._c.resume()

    def is_suspended(self):
        self._check_closed()
        return self._c.is_suspended()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def _check_closed(self):
        if self._c is None:
            raise ValueError("Session is closed")

    def session_id(self) -> int:
        """
        Returns the session id.

        :return: The session id.
        """
        return self.id

    def new_module(
        self,
        module_tag: str,
        config: Optional[Dict[str, bytes]] = None,
        placement_group_name: Optional[str] = None,
    ) -> Module:
        """
        Creates a new instance of a module from a module tag.

        :param module_tag: The module tag.
        :param config: The module configuration dictionary.
        :param placement_group_name: The name of the placement group. If empty,
            an arbitrary placement group with matching module hash is selected.
        :return: The created module instance.
        """
        if config is None:
            config = {}
        if placement_group_name is None:
            placement_group_name = ""
        self._check_closed()
        return Module(self._c.new_module(module_tag, config, placement_group_name))

    def new_module_from_hash(
        self,
        module_hash: str,
        config: Optional[Dict[str, bytes]] = None,
        placement_group_name: Optional[str] = None,
    ) -> Module:
        """
        Creates a new instance of a module from a module hash.

        :param module_hash: The module hash.
        :param config: The module configuration dictionary.
        :param placement_group_name: The name of the placeent group. If empty,
            an arbitrary placement group with matching module hash is selected.
        :return: The created module instance.
        """
        if config is None:
            config = {}
        if placement_group_name is None:
            placement_group_name = ""
        self._check_closed()
        return Module(
            self._c.new_module_from_hash(module_hash, config, placement_group_name)
        )

    def new_module_from_cls(
        self,
        module_cls,
        module_tag: Optional[str] = None,
        module_hash: Optional[str] = None,
        config: Optional[Dict[str, bytes]] = None,
    ):
        """
        Creates a new instance of a module from a Python class.

        Note that a python interpreter module must be included in the session's
        placement groups to use this function.

        :param module_cls: The module class. Must derive from exa.BaseModule.
        :param module_tag: The module tag for the python interpreter module. If
            specified, module_hash should not be specified.
        :param module_hash: The module hash for the python interpreter module.
            If specified, module_tag should not be specified.
        :param config: Optional; the module configuration dictionary.
        :return: The created module instance.
        """
        if config is None:
            config = {}
        config = config.copy()
        for invalid_key in ["_py_module_cls", "_py_module_name"]:
            if invalid_key in config:
                raise ValueError(
                    "Config for python interpreter module may not contain key "
                    + invalid_key
                )
        config["_py_module_cls"] = inspect.getsource(module_cls).encode()
        config["_py_module_name"] = module_cls.__name__.encode()
        if (module_tag is not None) + (module_hash is not None) != 1:
            raise ValueError(
                "Exactly one of module_tag and module_hash must be specified"
            )
        if module_tag is not None:
            return self.new_module(module_tag, config)
        return self.new_module_from_hash(module_hash, config)  # type: ignore

    def existing_module(self, module_id: int) -> Module:
        """
        Retrieve an existing module.

        :param module_id: The module id.
        :return: The existing module instance.
        """
        return Module(self._c.existing_module(module_id))

    def _allocate_value(self, metadata: ValueMetadata):
        ser_metadata = b""
        if metadata is not None:
            ser_metadata = metadata.SerializeToString()
        return Value(self._c.allocate_value(ser_metadata))

    def _existing_value(self, value_id: int, metadata: ValueMetadata):
        ser_metadata = b""
        if metadata is not None:
            ser_metadata = metadata.SerializeToString()
        return Value(self._c.existing_value(value_id, ser_metadata))

    def allocate_bytes(self, size: int) -> Value:
        """
        Creates an empty value representing a byte array.

        These values are mapped to Exafunction Bytes values.

        :param size: The size of the byte array
        :return: The created value.
        """
        self._check_closed()
        metadata = ValueMetadata()
        metadata.size = size
        metadata.bytes.SetInParent()
        return self._allocate_value(metadata)

    def from_bytes(self, val: bytes) -> Value:
        """
        Creates a new Exafunction value by copying an existing byte array.

        These values are mapped to Exafunction Bytes values.

        :param val: The byte array
        :return: The created value.
        """
        self._check_closed()
        v = self.allocate_bytes(len(val))
        v.set_bytes(val)
        return v

    def existing_bytes(self, value_id: int, size: int) -> Value:
        """Retrieves an existing Bytes value."""
        self._check_closed()
        metadata = ValueMetadata()
        metadata.size = size
        metadata.bytes.SetInParent()
        return self._existing_value(value_id, metadata)

    def _allocate_numpy(
        self,
        dtype: np.dtype,
        shape: Sequence[int],
    ) -> Value:
        """
        Creates an empty Exafunction value representing a NumPy array.

        These values are mapped to Exafunction Tensor values.

        :param dtype: The array datatype
        :param shape: The shape of the array
        :return: The created value.
        """
        # pylint: disable=protected-access
        metadata = Value._get_tensor_metadata(dtype, shape)
        v = self._allocate_value(metadata)
        return v

    def from_numpy(self, val: np.ndarray) -> Value:
        """
        Creates an empty Exafunction value by copying an existing NumPy array.

        These values are mapped to Exafunction Tensor values.

        :param val: The byte array
        :return: The created value.
        """
        self._check_closed()
        v = self._allocate_numpy(val.dtype, val.shape)
        v.numpy()[:] = val
        return v

    def existing_tensor(
        self, value_id: int, dtype: np.dtype, shape: Sequence[int]
    ) -> Value:
        """Retrieves an existing Tensor value."""
        self._check_closed()
        # pylint: disable=protected-access
        metadata = Value._get_tensor_metadata(dtype, shape)
        return self._existing_value(value_id, metadata)

    def start_profiling(self) -> Profiler:
        """
        Creates a new profiler.

        :return: The created profiler.
        """
        return Profiler(self._c.start_profiling())

    def _enable_glog_stacktrace(self):
        self._check_closed()
        # pylint: disable=protected-access
        self._c._enable_glog_stacktrace()

    def _get_ipc_stats(self):
        stats = IpcStatsResponse()
        stats.ParseFromString(self._c.get_ipc_stats())
        return stats

    def _state(self):
        state = session_pb2.SessionState()
        state.ParseFromString(self._c.state())
        return state
