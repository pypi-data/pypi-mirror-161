from ai.h2o.featurestore.api.v1 import CoreService_pb2 as pb

INGEST = pb.JobType.Ingest
RETRIEVE = pb.JobType.Retrieve
EXTRACT_SCHEMA = pb.JobType.ExtractSchema
REVERT_INGEST = pb.JobType.Revert
MATERIALIZATION_ONLINE = pb.JobType.MaterializationOnline
COMPUTE_STATISTICS = pb.JobType.ComputeStatistics
COMPUTE_RECOMMENDATION_CLASSIFIERS = pb.JobType.ComputeRecommendationClassifiers
