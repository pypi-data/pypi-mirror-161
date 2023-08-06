import os

from google.protobuf import json_format


class Utils:
    @staticmethod
    def pretty_print_proto(m):
        return json_format.MessageToJson(m, including_default_value_fields=True)

    @staticmethod
    def timestamp_to_string(timestamp):
        if timestamp.ByteSize() != 0:
            return timestamp.ToDatetime().isoformat()
        else:
            return None

    @staticmethod
    def is_running_on_databricks() -> bool:
        try:
            from pyspark.sql import SparkSession

            spark = SparkSession.getActiveSession()
            spark.conf.get("spark.databricks.clusterUsageTags.sparkVersion")
            return True
        except:
            return False

    @staticmethod
    def read_env(variable_name, source):
        value = os.environ.get(variable_name)
        if value is None:
            raise Exception(
                "Environment variable "
                + variable_name
                + " is missing, it is required to read from "
                + source
                + " data source."
            )
        else:
            return value
