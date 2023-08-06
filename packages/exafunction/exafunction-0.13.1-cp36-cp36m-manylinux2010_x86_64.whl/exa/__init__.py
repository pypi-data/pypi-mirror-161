# Copyright Exafunction, Inc.

# pylint: disable=useless-import-alias

from exa.common_pb.common_pb2 import DataType as DataType
from exa.common_pb.common_pb2 import ModuleContextInfo as ModuleContextInfo
from exa.common_pb.common_pb2 import ModuleInfo as ModuleInfo
from exa.common_pb.common_pb2 import ValueMetadata as ValueMetadata
from exa.py_module_repository.module_repository import (
    _allow_module_repository_clear as _allow_module_repository_clear,
)
from exa.py_module_repository.module_repository import (
    get_bazel_runfiles_root as get_bazel_runfiles_root,
)
from exa.py_module_repository.module_repository import glob as glob
from exa.py_module_repository.module_repository import (
    ModuleRepository as ModuleRepository,
)

# Enable partial distribution without actual client
try:
    from exa.py_client.module import Module as Module
    from exa.py_client.session import ModuleContextSpec as ModuleContextSpec
    from exa.py_client.session import PlacementGroupSpec as PlacementGroupSpec
    from exa.py_client.session import Session as Session
    from exa.py_module.base_module import BaseModule as BaseModule
    from exa.py_module.base_module import export as export
    from exa.py_module.base_module_context import BaseModuleContext as BaseModuleContext
    from exa.py_module.base_module_context import wrap_call as wrap_call
    from exa.py_module.method_context import MethodContext as MethodContext
    from exa.py_value.value import Value as Value
    from exa.py_value.value import ValueCompressionType as ValueCompressionType
except ImportError as e:
    import os

    if os.environ.get("EXA_DEBUG_IMPORT", False):
        print("Failed to import Exafunction modules")
        raise e

# Enable extra module distribution without dependencies
try:
    from exa.ffmpeg_pb.ffmpeg_pb2 import DecoderParameters as DecoderParameters
    from exa.ffmpeg_pb.ffmpeg_pb2 import DecoderType as DecoderType
    from exa.ffmpeg_pb.ffmpeg_pb2 import EncoderParameters as EncoderParameters
    from exa.ffmpeg_pb.ffmpeg_pb2 import EncoderType as EncoderType
    from exa.py_ffmpeg.ffmpeg import VideoDecoder as VideoDecoder
    from exa.py_ffmpeg.ffmpeg import VideoEncoder as VideoEncoder
except ImportError as e:
    import os

    if os.environ.get("EXA_DEBUG_IMPORT_EXTRAS", False):
        print("Failed to import Exafunction extras modules")
        raise e
