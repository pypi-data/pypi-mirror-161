# Copyright Exafunction, Inc.

""" Module repository stub """

# pylint: disable=missing-function-docstring,missing-class-docstring

import io
from typing import Dict, Iterable

import grpc

from exa.module_repository_pb import module_repository_pb2
from exa.py_module_repository.module_repository import _generate_data_id


class RpcError(grpc.RpcError):
    def __init__(self, code, msg):
        super().__init__(f"(code={code}) {msg}")
        self._code = code

    def code(self):
        return self._code


class ModuleRepositoryStub:
    def __init__(self):
        self.objects: Dict[str, bytes] = {}  # object id -> serialized objects
        self.tags: Dict[str, str] = {}
        self.blobs: Dict[str, bytes] = {}  # blob id -> blob contents

    def GetSerializedObjectMetadata(
        self, req: module_repository_pb2.GetSerializedObjectMetadataRequest
    ) -> module_repository_pb2.GetSerializedObjectMetadataResponse:
        if req.object_id not in self.objects:
            # TODO(douglas): the Go module repository returns UNKNOWN instead
            # of NOT_FOUND
            raise RpcError(
                grpc.StatusCode.UNKNOWN, f"object {req.object_id} does not exist"
            )
        return module_repository_pb2.GetSerializedObjectMetadataResponse(
            serialized_metadata=self.objects[req.object_id]
        )

    def GetObjectMetadata(
        self, req: module_repository_pb2.GetObjectMetadataRequest
    ) -> module_repository_pb2.GetObjectMetadataResponse:
        if req.object_id not in self.objects:
            # TODO(douglas): the Go module repository returns UNKNOWN instead
            # of NOT_FOUND
            raise RpcError(
                grpc.StatusCode.UNKNOWN, f"object {req.object_id} does not exist"
            )
        obj = module_repository_pb2.Metadata()
        obj.ParseFromString(self.objects[req.object_id])
        return module_repository_pb2.GetObjectMetadataResponse(metadata=obj)

    def RegisterObject(
        self, req: module_repository_pb2.RegisterObjectRequest
    ) -> module_repository_pb2.RegisterObjectResponse:
        # Verify that the object id matches the object
        object_id = _generate_data_id(io.BytesIO(req.serialized_metadata))
        self.objects[object_id] = req.serialized_metadata
        return module_repository_pb2.RegisterObjectResponse(object_id=object_id)

    def AddTagForObjectId(
        self, req: module_repository_pb2.AddTagForObjectIdRequest
    ) -> module_repository_pb2.AddTagForObjectIdResponse:
        self.tags[req.tag] = req.object_id
        return module_repository_pb2.AddTagForObjectIdResponse()

    def GetObjectIdFromTag(
        self, req: module_repository_pb2.GetObjectIdFromTagRequest
    ) -> module_repository_pb2.GetObjectIdFromTagResponse:
        if req.tag not in self.tags:
            # TODO(douglas): the Go module repository returns UNKNOWN instead
            # of NOT_FOUND
            raise RpcError(grpc.StatusCode.UNKNOWN, f"tag {req.tag} does not exist")
        return module_repository_pb2.GetObjectIdFromTagResponse(
            object_id=self.tags[req.tag]
        )

    def ExistsBlob(
        self, req: module_repository_pb2.ExistsBlobRequest
    ) -> module_repository_pb2.ExistsBlobResponse:
        return module_repository_pb2.ExistsBlobResponse(
            exists=req.blob_id in self.blobs
        )

    def RegisterBlobStreaming(
        self, iterator: Iterable[module_repository_pb2.RegisterBlobStreamingRequest]
    ) -> module_repository_pb2.RegisterBlobStreamingResponse:
        data = io.BytesIO()
        for req in iterator:
            data.write(req.data_chunk)
        data.seek(0)
        blob_id = _generate_data_id(data)
        data.seek(0)
        self.blobs[blob_id] = data.read()
        return module_repository_pb2.RegisterBlobStreamingResponse(blob_id=blob_id)

    def GetBlob(
        self, req: module_repository_pb2.GetBlobRequest
    ) -> Iterable[module_repository_pb2.GetBlobResponse]:
        # TODO(douglas): simulate chunking?
        return [
            module_repository_pb2.GetBlobResponse(data_chunk=self.blobs[req.blob_id])
        ]

    def ClearData(
        self, req: module_repository_pb2.ClearDataRequest
    ) -> module_repository_pb2.ClearDataResponse:
        # pylint: disable=unused-argument
        self.objects.clear()
        self.tags.clear()
        self.blobs.clear()
