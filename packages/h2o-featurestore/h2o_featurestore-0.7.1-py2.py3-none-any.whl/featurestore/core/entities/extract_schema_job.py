from ..schema import FeatureSchema, Schema, SchemaDerivation, VersionedId
from ..transformations import Transformation
from .base_job import BaseJob


class ExtractSchemaJob(BaseJob):
    def _response_method(self, job_id):
        response = self._stub.GetExtractSchemaJobOutput(job_id)
        derivation = None
        if response.derived_from.HasField("transformation"):
            derivation = SchemaDerivation(
                [
                    VersionedId(f.id, f.major_version)
                    for f in response.derived_from.feature_set_ids
                ],
                Transformation.from_proto(response.derived_from.transformation),
            )
        return Schema(
            ExtractSchemaJob._features_schema_from_proto(response.schema),
            True,
            derivation,
        )

    @staticmethod
    def _features_schema_from_proto(schema):
        return [
            FeatureSchema(
                feature_schema.name,
                feature_schema.data_type,
                nested_features_schema=ExtractSchemaJob._features_schema_from_proto(
                    feature_schema.nested
                ),
            )
            for feature_schema in schema
        ]
