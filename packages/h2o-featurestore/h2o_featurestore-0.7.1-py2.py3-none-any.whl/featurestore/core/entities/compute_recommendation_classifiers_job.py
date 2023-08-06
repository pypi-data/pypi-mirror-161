from .base_job import BaseJob


class ComputeRecommendationClassifiersJob(BaseJob):
    def _response_method(self, job_id):
        self._stub.GetComputeRecommendationClassifiersJobOutput(job_id)
