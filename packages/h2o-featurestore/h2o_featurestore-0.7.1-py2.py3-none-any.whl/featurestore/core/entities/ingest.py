import time

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from featurestore.core import interactive_console

from ..retrieve_holder import RetrieveHolder
from ..utils import Utils
from .revert_ingest_job import RevertIngestJob


class Ingest:
    def __init__(self, stub, feature_set, ingest):
        self._stub = stub
        self._feature_set = feature_set
        self._ingest = ingest

    def retrieve(self):
        return RetrieveHolder(
            self._stub, self._feature_set, "", "", self._ingest.ingest_id
        )

    @interactive_console.record_stats
    def revert(self):
        job = self.revert_async()
        return job.wait_for_result()

    def revert_async(self) -> RevertIngestJob:
        if self._feature_set.derived_from.HasField("transformation"):
            raise Exception("Manual revert is not allowed on derived feature set")

        request = pb.StartRevertIngestJobRequest()
        request.feature_set.CopyFrom(self._feature_set)
        request.ingest_id = self._ingest.ingest_id
        job_id = self._stub.StartRevertIngestJob(request)
        return RevertIngestJob(self._stub, job_id)

    def __repr__(self):
        return Utils.pretty_print_proto(self._ingest)
