import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

import pandas
import pendulum

from tecton_core import conf
from tecton_core import errors
from tecton_core.errors import INVALID_SPINE_SQL
from tecton_core.errors import TectonSnowflakeNotImplementedError
from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_core.feature_set_config import FeatureSetConfig
from tecton_proto.common import aggregation_function_pb2 as afpb
from tecton_proto.common import column_type_pb2
from tecton_proto.data.batch_data_source_pb2 import BatchDataSource
from tecton_proto.data.feature_view_pb2 import FeatureView as FeatureViewProto
from tecton_proto.data.feature_view_pb2 import NewTemporalAggregate
from tecton_snowflake.pipeline_helper import pipeline_to_df_with_input
from tecton_snowflake.pipeline_helper import pipeline_to_sql_string
from tecton_snowflake.pipeline_helper import SPINE_TABLE_NAME
from tecton_snowflake.templates_utils import load_template
from tecton_snowflake.utils import format_sql
from tecton_spark.materialization_context import BaseMaterializationContext
from tecton_spark.materialization_context import BoundMaterializationContext

TEMP_SPINE_TABLE_NAME = "_TEMP_SPINE_TABLE_FROM_DF"

FULL_AGGREGATION_TEMPLATE = load_template("run_full_aggregation.sql")
HISTORICAL_FEATURES_TEMPLATE = load_template("historical_features.sql")
MATERIALIZATION_TILE_TEMPLATE = load_template("materialization_tile.sql")
MATERIALIZED_FEATURE_VIEW_TEMPLATE = load_template("materialized_feature_view.sql")
ONLINE_STORE_COPIER_TEMPLATE = load_template("online_store_copier.sql")
PARTIAL_AGGREGATION_TEMPLATE = load_template("run_partial_aggregation.sql")
TIME_LIMIT_TEMPLATE = load_template("time_limit.sql")
DELETE_STAGED_FILES_TEMPLATE = load_template("delete_staged_files.sql")

# TODO(TEC-6204): Last and LastN are not currently supported
#
# Map of proto function type -> set of (output column prefix, snowflake function name)
AGGREGATION_PLANS = {
    afpb.AGGREGATION_FUNCTION_SUM: {("SUM", "SUM")},
    afpb.AGGREGATION_FUNCTION_MIN: {("MIN", "MIN")},
    afpb.AGGREGATION_FUNCTION_MAX: {("MAX", "MAX")},
    afpb.AGGREGATION_FUNCTION_COUNT: {("COUNT", "COUNT")},
    afpb.AGGREGATION_FUNCTION_MEAN: {("COUNT", "COUNT"), ("MEAN", "AVG")},
    # sample variation equation: (Σ(x^2) - (Σ(x)^2)/N)/N-1
    afpb.AGGREGATION_FUNCTION_VAR_SAMP: {("SUM", "SUM"), ("COUNT", "COUNT"), ("SUM_OF_SQUARES", "SUM_OF_SQUARES")},
    # population variation equation: Σ(x^2)/n - μ^2
    afpb.AGGREGATION_FUNCTION_VAR_POP: {("SUM", "SUM"), ("COUNT", "COUNT"), ("SUM_OF_SQUARES", "SUM_OF_SQUARES")},
    # sample standard deviation equation: √ ((Σ(x^2) - (Σ(x)^2)/N)/N-1)
    afpb.AGGREGATION_FUNCTION_STDDEV_SAMP: {("SUM", "SUM"), ("COUNT", "COUNT"), ("SUM_OF_SQUARES", "SUM_OF_SQUARES")},
    # population standard deviation equation: √ (Σ(x^2)/n - μ^2)
    afpb.AGGREGATION_FUNCTION_STDDEV_POP: {("SUM", "SUM"), ("COUNT", "COUNT"), ("SUM_OF_SQUARES", "SUM_OF_SQUARES")},
}


@dataclass
class _FeatureSetItemInput:
    """A simplified version of FeatureSetItem which is passed to the SQL template."""

    name: str
    namespace: str
    timestamp_key: str
    join_keys: Dict[str, str]
    features: List[str]
    sql: str
    aggregation: Optional[NewTemporalAggregate]
    ttl_seconds: Optional[int]


def get_historical_features_sql(
    spine_sql: Optional[str],
    feature_set_config: FeatureSetConfig,
    timestamp_key: Optional[str],
    include_feature_view_timestamp_columns: bool = False,
    start_time: datetime = None,
    end_time: datetime = None,
    session: "snowflake.snowpark.Session" = None,
    append_prefix: bool = True,  # Whether to append the prefix to the feature column name
) -> str:
    feature_set_items = feature_set_config._get_feature_definitions_and_join_configs()
    input_items = []
    if spine_sql is None:
        # Only feature view is supported when the spine is not provided.
        # Feature service should always provide the spine.
        # SDK methods should never fail this check
        assert len(feature_set_items) == 1

    # Get a list of all the join keys in the spine.
    spine_keys = {}
    for item in feature_set_items:
        fd = item.feature_definition

        if not fd.is_on_demand:
            join_keys = {key: value for key, value in item.join_keys}
            spine_keys.update(join_keys)

    for item in feature_set_items:
        fd = item.feature_definition
        if fd.is_on_demand and not conf.get_bool("ALPHA_SNOWFLAKE_SNOWPARK_ENABLED"):
            raise TectonSnowflakeNotImplementedError("On-demand features are only supported with Snowpark enabled")
        feature_view = fd.fv
        # Change the feature view name if it's for internal udf use.
        if item.namespace.startswith("_udf_internal"):
            name = item.namespace.upper()
        else:
            name = fd.name

        if not fd.is_on_demand:
            join_keys = {key: value for key, value in item.join_keys}
            features = [
                col_name
                for col_name in fd.view_schema.column_names()
                if col_name not in (list(join_keys.keys()) + [fd.timestamp_key])
            ]
            if len(fd.online_serving_index.join_keys) != len(fd.join_keys):
                raise TectonSnowflakeNotImplementedError("Wildcard is not supported for Snowflake")
            if start_time is None or (
                fd.feature_start_timestamp is not None and start_time < fd.feature_start_timestamp
            ):
                start_time = fd.feature_start_timestamp

            raw_data_start_time = start_time
            raw_dat_end_time = end_time
            if fd.is_temporal_aggregate and raw_data_start_time is not None:
                # Account for final aggregation needing aggregation window prior to earliest timestamp
                max_aggregation_window = fd.max_aggregation_window
                raw_data_start_time = raw_data_start_time - max_aggregation_window.ToTimedelta()
            sql_str = generate_run_batch_sql(
                feature_definition=fd,
                feature_start_time=raw_data_start_time,
                feature_end_time=raw_dat_end_time,
                # If the spine sql has undetermined results(LIMIT X etc.), we don't want
                # to run it twice. So we use the subquery we defined here directly.
                spine=SPINE_TABLE_NAME if spine_sql is not None else None,
                spine_timestamp_key=timestamp_key,
                session=session,
            )
            input_items.append(
                _FeatureSetItemInput(
                    name=name,
                    namespace=item.namespace or name,
                    timestamp_key=fd.timestamp_key,
                    join_keys=join_keys,
                    features=features,
                    sql=sql_str,
                    aggregation=(
                        feature_view.temporal_aggregate if feature_view.HasField("temporal_aggregate") else None
                    ),
                    ttl_seconds=(int(fd.serving_ttl.total_seconds()) if fd.is_temporal else None),
                )
            )
    if spine_sql is not None:
        sql_str = HISTORICAL_FEATURES_TEMPLATE.render(
            feature_set_items=input_items,
            spine_timestamp_key=timestamp_key,
            spine_sql=spine_sql,
            include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
            spine_keys=list(spine_keys),
            append_prefix=append_prefix,
        )
    if start_time is not None or end_time is not None:
        timestamp = timestamp_key if spine_sql is not None else fd.timestamp_key
        sql_str = TIME_LIMIT_TEMPLATE.render(
            source=sql_str, timestamp_key=timestamp, start_time=start_time, end_time=end_time
        )

    if conf.get_bool("SNOWFLAKE_DEBUG"):
        print("Generated Snowflake SQL for get_historical_features, this does not include ODFV:")
        print(sql_str)
    return format_sql(sql_str)


def get_historical_features(
    spine: Optional[Union[pandas.DataFrame, str]],
    connection: "snowflake.connector.Connection",
    feature_set_config: FeatureSetConfig,
    timestamp_key: Optional[str],
    include_feature_view_timestamp_columns: bool = False,
    start_time: datetime = None,
    end_time: datetime = None,
    append_prefix: bool = True,  # Whether to append the prefix to the feature column name
) -> pandas.DataFrame:
    cur = connection.cursor()
    spine_sql = None
    if isinstance(spine, str):
        spine_sql = spine
    elif isinstance(spine, pandas.DataFrame):
        spine_sql = generate_sql_table_from_pandas_df(df=spine, table_name=TEMP_SPINE_TABLE_NAME, connection=connection)

    sql_str = get_historical_features_sql(
        spine_sql=spine_sql,
        feature_set_config=feature_set_config,
        timestamp_key=timestamp_key,
        include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
        start_time=start_time,
        end_time=end_time,
        append_prefix=append_prefix,
    )
    cur.execute(sql_str)
    return cur.fetch_pandas_all()


def generate_sql_table_from_pandas_df(
    df: pandas.DataFrame,
    table_name: str,
    session: "snowflake.snowpark.Session" = None,
    connection: "snowflake.connector.Connection" = None,
) -> str:
    """Generate a TABLE from pandas.DataFrame. Returns the sql query to select * from the table"""
    if session is None and connection is None:
        raise ValueError("Either session or connection must be provided")

    if session is not None:
        session.sql(f"DROP TABLE IF EXISTS {table_name}").collect()
        session.write_pandas(df, table_name, auto_create_table=True, create_temp_table=True)
        return f"SELECT * FROM {table_name}"

    if connection is not None:
        from snowflake.connector.pandas_tools import write_pandas

        # Get the SQL that would be generated by the create table statement
        create_table_sql = pandas.io.sql.get_schema(df, table_name)

        # Replace the `CREATE TABLE` with `CREATE OR REPLACE TEMPORARY TABLE`
        create_tmp_table_sql = re.sub("^(CREATE TABLE)?", "CREATE OR REPLACE TEMPORARY TABLE", create_table_sql)
        cur = connection.cursor()
        cur.execute(create_tmp_table_sql)
        write_pandas(conn=connection, df=df, table_name=table_name)
        return f"SELECT * FROM {table_name}"


def validate_spine_dataframe(spine_df: "snowflake.snowpark.DataFrame", timestamp_key: str, join_keys: List[str]):
    from snowflake.snowpark import types

    if timestamp_key not in spine_df.columns:
        raise errors.TectonValidationError(
            f"Expected to find '{timestamp_key}' among available spine columns: '{', '.join(spine_df.columns)}'."
        )
    for field in spine_df.schema.fields:
        if field.name == timestamp_key and not isinstance(field.datatype, types.TimestampType):
            raise errors.TectonValidationError(
                f"Invalid type of timestamp_key column in the given spine. Expected Timestamp, got {field.datatype}"
            )
    for key in join_keys:
        if key not in spine_df.columns:
            raise errors.TectonValidationError(
                f"Expected to find '{key}' among available spine columns: '{', '.join(spine_df.columns)}'."
            )


def get_historical_features_with_snowpark(
    spine: Union[pandas.DataFrame, str, "snowflake.snowpark.DataFrame"],
    session: "snowflake.snowpark.Session",
    feature_set_config: FeatureSetConfig,
    timestamp_key: Optional[str],
    include_feature_view_timestamp_columns: bool = False,
    start_time: datetime = None,
    end_time: datetime = None,
    entities: "snowflake.snowpark.DataFrame" = None,
    append_prefix: bool = True,  # Whether to append the prefix to the feature column name
) -> "snowflake.snowpark.DataFrame":
    from snowflake.snowpark import DataFrame
    from snowflake.snowpark import types

    spine_sql = None
    if isinstance(spine, str):
        spine_sql = spine
    elif isinstance(spine, DataFrame):
        spine.write.save_as_table(TEMP_SPINE_TABLE_NAME, mode="overwrite", create_temp_table=True)
        spine_sql = f"SELECT * FROM {TEMP_SPINE_TABLE_NAME}"
    elif isinstance(spine, pandas.DataFrame):
        spine_sql = generate_sql_table_from_pandas_df(df=spine, table_name=TEMP_SPINE_TABLE_NAME, session=session)

    if spine is not None:
        # validate spine sql
        try:
            spine_df = session.sql(spine_sql)
            spine_schema = spine_df.schema
        except Exception as e:
            raise INVALID_SPINE_SQL(e)
        if timestamp_key is None:
            schema = spine_schema
            timestamp_cols = [field.name for field in schema.fields if isinstance(field.datatype, types.TimestampType)]

            if len(timestamp_cols) > 1 or len(timestamp_cols) == 0:
                raise errors.TectonValidationError(
                    f"Could not infer timestamp keys from {schema}; please specify explicitly"
                )
            timestamp_key = timestamp_cols[0]

        join_keys = [join_key for fd in feature_set_config.feature_definitions for join_key in fd.join_keys]
        validate_spine_dataframe(spine_df, timestamp_key, join_keys=join_keys)

    sql_str = get_historical_features_sql(
        spine_sql=spine_sql,
        feature_set_config=feature_set_config,
        timestamp_key=timestamp_key,
        include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
        start_time=start_time,
        end_time=end_time,
        session=session,
        append_prefix=append_prefix,
    )
    output_df = session.sql(sql_str)

    # Apply ODFV to the spine.
    for item in feature_set_config._get_feature_definitions_and_join_configs():
        fd = item.feature_definition
        if fd.is_on_demand:
            view_schema = fd.view_schema
            schema_dict = {col_name: view_schema.spark_type(col_name) for col_name in view_schema.column_names()}
            output_df = pipeline_to_df_with_input(
                session=session,
                input_df=output_df,
                pipeline=fd.pipeline,
                transformations=fd.transformations,
                output_schema=schema_dict,
                name=fd.name,
                fv_id=fd.id,
                namespace=item.namespace or fd.name,
                append_prefix=append_prefix,
            )
    columns_to_drop = [column for column in output_df.columns if "_UDF_INTERNAL_" in column]
    if len(columns_to_drop) > 0:
        output_df = output_df.drop(*columns_to_drop)
    if entities is not None:
        column_names = [field.name for field in entities.schema.fields]
        # Do an inner join on the entities to filter out rows that don't have a matching entity
        output_df = entities.join(right=output_df, using_columns=column_names, join_type="inner")
    return output_df


def generate_run_batch_sql(
    feature_definition: FeatureDefinition,
    # start is inclusive and end is exclusive
    feature_start_time: Optional[datetime] = None,
    feature_end_time: Optional[datetime] = None,
    aggregation_level: str = "full",
    # If spine is provided, it will be used to join with the output results.
    # Currently only work with full aggregation.
    spine: Optional[str] = None,
    spine_timestamp_key: Optional[str] = None,
    spine_keys: Optional[List[str]] = None,
    mock_sql_inputs: Optional[Dict[str, str]] = None,
    materialization_context: Optional[BaseMaterializationContext] = None,
    session: "snowflake.snowpark.Session" = None,
) -> str:
    feature_view = feature_definition.feature_view_proto

    # Set a default materilization_context if not provided.
    # This is following the same logic as spark.
    if materialization_context is None:
        materialization_context = BoundMaterializationContext._create_internal(
            feature_start_time or pendulum.from_timestamp(0, pendulum.tz.UTC),
            feature_end_time or pendulum.datetime(2100, 1, 1),
            pendulum.Duration(seconds=feature_view.materialization_params.schedule_interval.ToSeconds()),
        )
    if feature_definition.is_incremental_backfill:
        materialized_sql = TIME_LIMIT_TEMPLATE.render(
            source=f"SELECT * FROM {feature_view.snowflake_data.snowflake_view_name}",
            timestamp_key=feature_view.timestamp_key,
            start_time=feature_start_time,
            end_time=feature_end_time,
        )
    else:
        pipeline_sql = pipeline_to_sql_string(
            pipeline=feature_definition.pipeline,
            data_sources=feature_definition.data_sources,
            transformations=feature_definition.transformations,
            materialization_context=materialization_context,
            mock_sql_inputs=mock_sql_inputs,
            session=session,
        )
        materialized_sql = get_materialization_query(
            feature_view=feature_view,
            feature_start_time=feature_start_time,
            feature_end_time=feature_end_time,
            source=pipeline_sql,
        )
    if feature_view.HasField("temporal_aggregate"):
        if aggregation_level == "full":
            aggregated_sql_str = FULL_AGGREGATION_TEMPLATE.render(
                source=materialized_sql,
                join_keys=list(feature_view.join_keys),
                aggregation=feature_view.temporal_aggregate,
                timestamp_key=feature_view.timestamp_key,
                name=feature_view.fco_metadata.name,
                spine=spine,
                spine_timestamp_key=spine_timestamp_key,
                spine_keys=spine_keys,
            )
            return format_sql(aggregated_sql_str)
        elif aggregation_level == "partial":
            # Rename the output columns, and add tile start/end time columns
            partial_aggregated_sql_str = PARTIAL_AGGREGATION_TEMPLATE.render(
                source=materialized_sql,
                join_keys=list(feature_view.join_keys),
                aggregations=_get_feature_view_aggregations(feature_view),
                slide_interval=feature_view.temporal_aggregate.slide_interval,
                slide_interval_string=feature_view.temporal_aggregate.slide_interval_string,
                timestamp_key=feature_view.timestamp_key,
            )
            return format_sql(partial_aggregated_sql_str)
        elif aggregation_level == "disabled":
            sql_str = TIME_LIMIT_TEMPLATE.render(
                source=pipeline_sql,
                timestamp_key=feature_view.timestamp_key,
                start_time=feature_start_time,
                end_time=feature_end_time,
            )
            return format_sql(sql_str)
        else:
            raise ValueError(f"Unsupported aggregation level: {aggregation_level}")

    else:
        return format_sql(materialized_sql)


# By default Snowflake unloads numerical types as byte arrays because they have higher precision than available Parquet
# types. We could decode these in the OnlineStoreCopier, but since we will be downcasting them to the precision of
# Parquet types we might as well do it now.
#
# Snowflake docs for how casting interacts with Parquet types:
# https://docs.snowflake.com/en/user-guide/data-unload-considerations.html#explicitly-converting-numeric-columns-to-parquet-data-types
COPY_CASTS = {
    column_type_pb2.COLUMN_TYPE_UNKNOWN: None,
    column_type_pb2.COLUMN_TYPE_INT64: "BIGINT",
    column_type_pb2.COLUMN_TYPE_DOUBLE: "DOUBLE",
    column_type_pb2.COLUMN_TYPE_STRING: None,
    column_type_pb2.COLUMN_TYPE_BOOL: None,
    column_type_pb2.COLUMN_TYPE_STRING_ARRAY: None,
    # TODO(TEC-8501): Probably need to do something here
    column_type_pb2.COLUMN_TYPE_INT64_ARRAY: None,
    column_type_pb2.COLUMN_TYPE_DOUBLE_ARRAY: None,
    column_type_pb2.COLUMN_TYPE_FLOAT_ARRAY: None,
    column_type_pb2.COLUMN_TYPE_DERIVE_FROM_DATA_TYPE: None,
}


def get_materialization_query(
    feature_view: FeatureViewProto,
    source: str,
    # start is inclusive and end is exclusive
    feature_start_time: datetime = None,
    feature_end_time: datetime = None,
):
    """Returns a SQL query for time-limited materialization.

    Does not include a terminating `;` or any COPY or INSERT statements."""
    if feature_view.HasField("temporal_aggregate"):
        source = MATERIALIZATION_TILE_TEMPLATE.render(
            source=source,
            join_keys=list(feature_view.join_keys),
            aggregations=_get_feature_view_aggregations(feature_view),
            slide_interval=feature_view.temporal_aggregate.slide_interval,
            timestamp_key=feature_view.timestamp_key,
        )
    return format_sql(
        TIME_LIMIT_TEMPLATE.render(
            source=source,
            timestamp_key=feature_view.timestamp_key,
            start_time=feature_start_time,
            end_time=feature_end_time,
        )
    )


def get_delete_staged_files_sql(destination_stage: str, days: int):
    # Note the double quotes around destination_stage are required for the SQL to format properly
    script_sql = DELETE_STAGED_FILES_TEMPLATE.render(
        destination_stage=f"'{destination_stage}'",
        days=days,
    )
    sql = "\n".join(("EXECUTE IMMEDIATE", "$$", format_sql(script_sql), "$$;"))
    return format_sql(sql)


def get_materialization_copy_sql(
    feature_definition: FeatureDefinition,
    # start is inclusive and end is exclusive
    time_limits: pendulum.Period,
    destination_stage: str,
    destination_table: Optional[str],
    materialization_id: str,
    session: "snowflake.snowpark.Session" = None,
):
    """Returns a SQL query for a COPY INTO an destination_stage for materialization.

    Additionally INSERTs into destination_table for manually-materialized FeatureViews."""
    feature_view = feature_definition.feature_view_proto

    materialization_context = BoundMaterializationContext._create_internal(
        time_limits.start,
        time_limits.end,
        pendulum.Duration(seconds=feature_view.materialization_params.schedule_interval.ToSeconds()),
    )

    source = pipeline_to_sql_string(
        pipeline=feature_definition.pipeline,
        data_sources=feature_definition.data_sources,
        transformations=feature_definition.transformations,
        materialization_context=materialization_context,
        session=session,
    )
    query = get_materialization_query(
        source=source, feature_view=feature_view, feature_start_time=time_limits.start, feature_end_time=time_limits.end
    )
    common_context = dict(
        source=query,
        destination_stage=destination_stage,
        materialization_schema=feature_view.schemas.materialization_schema,
        materialization_id=materialization_id,
        cast_types=COPY_CASTS,
    )
    if destination_table:
        view_name = feature_definition.feature_view_proto.snowflake_data.snowflake_view_name
        database, schema, view = view_name.split(".")
        script_sql = MATERIALIZED_FEATURE_VIEW_TEMPLATE.render(
            destination_table=destination_table,
            workspace=f"{database}.{schema}",
            destination_view=view_name,
            **common_context,
        )
        sql = "\n".join(("EXECUTE IMMEDIATE", "$$", format_sql(script_sql), "$$;"))
    else:
        sql = ONLINE_STORE_COPIER_TEMPLATE.render(**common_context)
    return format_sql(sql)


def get_dataframe_for_data_source(
    session: "snowflake.snowpark.Session",
    data_source: BatchDataSource,
    start_time: datetime = None,
    end_time: datetime = None,
) -> "snowflake.snowpark.DataFrame":
    snowflake_args = data_source.snowflake.snowflakeArgs
    source = f"{snowflake_args.database}.{snowflake_args.schema}.{snowflake_args.table}"

    if (start_time is not None or end_time is not None) and snowflake_args.timestamp_key is None:
        raise ValueError(
            "Filtering by start_time or end_time requires the timestamp_key parameter to be set on this data source"
        )
    sql_str = TIME_LIMIT_TEMPLATE.render(
        source=source,
        timestamp_key=snowflake_args.timestamp_key,
        start_time=start_time,
        end_time=end_time,
    )
    return session.sql(sql_str)


def _get_feature_view_aggregations(feature_view: FeatureViewProto) -> Dict[str, Set[str]]:
    aggregations = defaultdict(set)
    for feature in feature_view.temporal_aggregate.features:
        aggregate_function = AGGREGATION_PLANS[feature.function]
        if not aggregate_function:
            raise TectonSnowflakeNotImplementedError(
                f"Unsupported aggregation function {feature.function} in snowflake pipeline"
            )
        aggregations[feature.input_feature_name].update(aggregate_function)

    # Need to order the functions for deterministic results.
    for key, value in aggregations.items():
        aggregations[key] = sorted(value)

    return aggregations
