from datetime import timedelta

import pandas
import pendulum

import tecton_spark.offline_store
from tecton_athena.athena_session import AthenaSession
from tecton_athena.athena_session import AthenaTableCreationSpec
from tecton_athena.athena_session import PARTITION_TYPE_DATESTR
from tecton_athena.athena_session import PARTITION_TYPE_UNIX_EPOCH_NS
from tecton_athena.templates_utils import load_template
from tecton_core import logger as logger_lib
from tecton_core.data_types import Float64Type
from tecton_core.data_types import Int32Type
from tecton_core.data_types import Int64Type
from tecton_core.data_types import StringType
from tecton_core.data_types import TimestampType
from tecton_core.errors import TectonAthenaNotImplementedError
from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_core.schema import Schema
from tecton_proto.data.feature_store_pb2 import FeatureStoreFormatVersion

logger = logger_lib.get_logger("DataCatalogHelper")

SECONDS_TO_NANOSECONDS = 1000 * 1000 * 1000

CREATE_TABLE_TEMPLATE = load_template("create_table.sql")

TECTON_DATA_TYPE_TO_HIVE_TYPES = {
    StringType(): "string",
    Float64Type(): "double",
    Int32Type(): "integer",
    Int64Type(): "bigint",
    TimestampType(): "timestamp",
}


# Todo: Refactor. Fairly ugly function
def register_feature_view_as_athena_table_if_necessary(
    feature_definition: FeatureDefinition, session: AthenaSession
) -> AthenaTableCreationSpec:
    # Examples of how our offline store is partitioned - quite the madness:
    ### BWAFV on Delta
    # Partition Column: time_partition
    # Materialized Columns: _anchor_time, [join_keys], [feature_columns]

    ### Continuous SWAFV on Parquet
    # Partition Column: time_partition
    # Materialized Columns: timestamp, _anchor_time, [join_keys], [feature_columns]
    # Note: Very weird that we have a timestamp parquet column here - redundant with _anchor_time

    ### BWAFV on Parquet
    # Partition Column: _anchor_time
    # Materialized Columns: _anchor_time, [join_keys], [feature_columns]
    # !! In this case we need to drop the partition column from the top level columns

    ### BFV on Parquet
    # Partition Column: _anchor_time
    # Materialized Columns: ts, [join_keys], [feature_columns]

    s3_path = feature_definition.materialized_data_path
    name = feature_definition.name

    partition_type = None
    partition_by_interval_timedelta = None
    partition_by = None
    partition_by_type = None
    partition_by_format = None
    partition_by_range_from = None
    partition_by_range_to = None
    partition_by_interval = None

    offline_store_config = feature_definition.offline_store_config
    store_type = offline_store_config.WhichOneof("store_type")

    # We only support nanosecond based partitions now
    assert (
        feature_definition.get_feature_store_format_version
        == FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_TIME_NANOSECONDS
    )

    # There should be a shared implementation here between this and the offline_store module
    if store_type == "delta":
        partition_by = tecton_spark.offline_store.TIME_PARTITION

        partition_by_interval_timedelta = offline_store_config.delta.time_partition_size.ToTimedelta()
        if partition_by_interval_timedelta % timedelta(days=1) != timedelta(0):
            # We only support daily partitions now
            raise TectonAthenaNotImplementedError("Athena reader currently only supports daily delta partitions")

        partition_type = PARTITION_TYPE_DATESTR
        partition_by_type = "date"
        partition_by_format = "yyyy-MM-dd"
        partition_by_range_from = (
            pendulum.instance(feature_definition.materialization_start_timestamp).start_of("day").format("YYYY-MM-DD")
        )
        # Let's register the table with partitions up until 1 year from now. Will break if the table is registered and used for more than 1 year
        partition_by_range_to = pendulum.now("utc").add(years=1).end_of("year").format("YYYY-MM-DD")
    elif store_type == "parquet":
        partition_by = tecton_spark.offline_store.ANCHOR_TIME
        partition_by_type = "integer"
        partition_type = PARTITION_TYPE_UNIX_EPOCH_NS
        partition_by_interval_timedelta = timedelta(
            seconds=feature_definition.batch_materialization_schedule.total_seconds()
        )

        if feature_definition.is_continuous_temporal_aggregate:
            # This is utter madness - for continous temporal aggregates, we partition by TIME_PARTITION, not ANCHOR_TIME, as we do for all other Parquet based FVs
            partition_by = tecton_spark.offline_store.TIME_PARTITION

        partition_by_range_from = int(
            pendulum.instance(feature_definition.materialization_start_timestamp).start_of("day").timestamp()
            * SECONDS_TO_NANOSECONDS
        )
        partition_by_range_to = int(
            pendulum.now("utc").add(years=1).end_of("year").timestamp() * SECONDS_TO_NANOSECONDS
        )
        # The partition size should really be configured explicitly in the proto offline store config
        partition_by_interval = int(partition_by_interval_timedelta.total_seconds() * SECONDS_TO_NANOSECONDS)
    else:
        raise Exception("Unexpected offline store config")

    materialization_schema = Schema(feature_definition.fv.schemas.materialization_schema)
    hive_columns = {}
    for (col, data_type) in materialization_schema.column_name_and_data_types():
        assert data_type in TECTON_DATA_TYPE_TO_HIVE_TYPES, f"Unexpected data type {data_type}"
        hive_columns[col] = TECTON_DATA_TYPE_TO_HIVE_TYPES[data_type]

    if feature_definition.is_temporal_aggregate:
        if tecton_spark.offline_store.ANCHOR_TIME not in hive_columns:
            raise Exception("Expected to find _anchor_time in materialized FeatureView schema")
        hive_columns[
            tecton_spark.offline_store.ANCHOR_TIME
        ] = "bigint"  # We have a bug somewhere - the materialization_schema indicates that the spark type for anchor_time is 4-byte integer. But we need 8 bytes.

    if feature_definition.is_continuous_temporal_aggregate:
        if "timestamp" in hive_columns:
            # Special madness about continuous aggregates
            # The parquet files contain both a `timestamp` and an `_anchor_time` field. Same value in both, just a different type
            del hive_columns["timestamp"]

    if partition_by in hive_columns:
        del hive_columns[partition_by]

    athena_database = session.get_database()
    athena_table_spec = AthenaTableCreationSpec(
        database=athena_database,
        table=name,
        s3_location=s3_path,
        columns=hive_columns,
        partition_by=partition_by,
        partition_by_type=partition_by_type,
        partition_by_format=partition_by_format,
        partition_by_range_from=str(partition_by_range_from),
        partition_by_range_to=str(partition_by_range_to),
        partition_by_interval=partition_by_interval,
        partition_by_interval_timedelta=partition_by_interval_timedelta,
        partition_type=partition_type,
    )

    session.create_table_if_necessary(athena_table_spec)

    return athena_table_spec


def generate_sql_table_from_pandas_df(df: pandas.DataFrame, table_name: str, session: AthenaSession) -> str:
    """Generate a TABLE from pandas.DataFrame. Returns the sql query to select * from the table"""
    if session is None:
        raise ValueError("Session must be provided")

    session.sql(f"DROP TABLE IF EXISTS {table_name}")
    session.write_pandas(df, table_name)
    return f"SELECT * FROM {table_name}"
