from codecs import open
from os import path

from featurestore.client import Client
from featurestore.core.client_config import ClientConfig
from featurestore.core.collections.classifiers import (
    EmptyClassifier,
    RegexClassifier,
    SampleClassifier,
)
from featurestore.core.data_source_wrappers import (
    CSVFile,
    CSVFolder,
    DeltaTable,
    DeltaTableFilter,
    JdbcTable,
    JSONFile,
    JSONFolder,
    ParquetFile,
    ParquetFolder,
    PartitionOptions,
    Proxy,
    SnowflakeCursor,
    SnowflakeTable,
    SparkDataFrame,
)
from featurestore.core.schema import FeatureSchema, Schema
from featurestore.core.transformations import (
    DriverlessAIMOJO,
    JoinFeatureSets,
    SparkPipeline,
)
from featurestore.core.user_credentials import (
    AzureKeyCredentials,
    AzurePrincipalCredentials,
    AzureSasCredentials,
    PostgresCredentials,
    S3Credentials,
    SnowflakeCredentials,
    TeradataCredentials,
)


def __get_version():
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, "version.txt"), encoding="utf-8") as f:
        return f.read().strip()


__version__ = __get_version()
__all__ = [
    "Client",
    "FeatureSchema",
    "Schema",
    "CSVFile",
    "CSVFolder",
    "JSONFile",
    "JSONFolder",
    "ParquetFile",
    "ParquetFolder",
    "SnowflakeTable",
    "JdbcTable",
    "PartitionOptions",
    "SnowflakeCursor",
    "DeltaTable",
    "DeltaTableFilter",
    "Proxy",
    "JSONFolder",
    "Schema",
    "SparkDataFrame",
    "ClientConfig",
    "AzureKeyCredentials",
    "AzureSasCredentials",
    "AzurePrincipalCredentials",
    "S3Credentials",
    "TeradataCredentials",
    "SnowflakeCredentials",
    "PostgresCredentials",
    "SparkPipeline",
    "DriverlessAIMOJO",
    "JoinFeatureSets",
    "EmptyClassifier",
    "RegexClassifier",
    "SampleClassifier",
]
