from typing import List
from typing import Optional

import attr
import pendulum
from pyspark.sql import DataFrame
from pyspark.sql import functions
from pyspark.sql import SparkSession

from tecton_core import conf
from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_core.logger import get_logger
from tecton_core.query.builder import build_run_querytree
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.rewrite import rewrite_tree
from tecton_core.time_utils import convert_timedelta_for_version
from tecton_proto.data.feature_view_pb2 import MaterializationTimeRangePolicy
from tecton_proto.data.new_transformation_pb2 import NewTransformation as Transformation
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource
from tecton_spark.partial_aggregations import construct_partial_time_aggregation_df
from tecton_spark.partial_aggregations import TEMPORAL_ANCHOR_COLUMN_NAME
from tecton_spark.pipeline_helper import pipeline_to_dataframe
from tecton_spark.query import translate
from tecton_spark.time_utils import convert_timestamp_to_epoch

MATERIALIZED_RAW_DATA_END_TIME = "_materialized_raw_data_end_time"
TECTON_FEATURE_TIMESTAMP_VALIDATOR = "_tecton_feature_timestamp_validator"
SKIP_FEATURE_TIMESTAMP_VALIDATION_ENV = "SKIP_FEATURE_TIMESTAMP_VALIDATION"
TIMESTAMP_VALIDATOR_UDF_REGISTERED = False

logger = get_logger("MaterializationPlan")


@attr.s(auto_attribs=True)
class MaterializationPlan(object):
    _base_data_frame: DataFrame
    fd: FeatureDefinition
    query_tree: NodeRef = None
    spark: SparkSession = None
    _cached_querytree_df: Optional[DataFrame] = None

    @property
    def base_data_frame(self) -> Optional[DataFrame]:
        if conf.get_bool("ALPHA_QUERYTREE_ENABLED"):
            if self._cached_querytree_df is None:
                # can't really use a tecton.DataFrame here, but it would be nice to not have all this tree manipulation boilerplate around
                self._cached_querytree_df = translate.spark_convert(self.query_tree).to_dataframe(self.spark)
            return self._cached_querytree_df
        else:
            return self._base_data_frame

    @property
    def offline_store_data_frame(self) -> Optional[DataFrame]:
        return self.base_data_frame

    @property
    def online_store_data_frame(self) -> Optional[DataFrame]:
        online_df = self.base_data_frame

        # batch online and offline df are slightly different
        if self.fd.is_temporal and not online_df.isStreaming:
            version = self.fd.get_feature_store_format_version
            batch_mat_schedule = convert_timedelta_for_version(self.fd.batch_materialization_schedule, version)
            online_df = self.base_data_frame.withColumn(
                MATERIALIZED_RAW_DATA_END_TIME, functions.col(TEMPORAL_ANCHOR_COLUMN_NAME) + batch_mat_schedule
            ).drop(TEMPORAL_ANCHOR_COLUMN_NAME)
        return online_df


def get_batch_materialization_plan(
    *,
    spark: SparkSession,
    feature_definition: FeatureDefinition,
    feature_data_time_limits: Optional[pendulum.Period],
    data_sources: List[VirtualDataSource],
    transformations: Optional[List[Transformation]] = None,
    schedule_interval: Optional[pendulum.Duration] = None,
) -> MaterializationPlan:
    """
    NOTE: We rely on Spark's lazy evaluation model to infer partially materialized tile Schema during FeatureView
    creation time without actually performing any materialization.
    Please make sure to not perform any Spark operations under this function's code path that will actually execute
    the Spark query (e.g: df.count(), df.show(), etc.).
    """

    if feature_definition.is_temporal_aggregate:
        plan = _get_batch_materialization_plan_for_aggregate_feature_view(
            spark,
            feature_definition,
            False,
            feature_data_time_limits,
            data_sources,
            transformations or [],
            schedule_interval=schedule_interval,
        )
    elif feature_definition.is_temporal:
        assert feature_data_time_limits is not None
        plan = _get_batch_materialization_plan_for_temporal_feature_view(
            spark,
            feature_definition,
            False,
            feature_data_time_limits,
            data_sources,
            transformations or [],
            schedule_interval=schedule_interval,
        )
    else:
        raise ValueError(f"Unhandled feature view: {feature_definition.fv}")
    plan.query_tree = build_run_querytree(
        feature_definition, for_stream=False, feature_data_time_limits=feature_data_time_limits
    )
    rewrite_tree(plan.query_tree)
    plan.spark = spark
    return plan


def _get_batch_materialization_plan_for_aggregate_feature_view(
    spark: SparkSession,
    feature_definition: FeatureDefinition,
    consume_streaming_data_sources: bool,
    feature_data_time_limits: Optional[pendulum.Period],
    data_sources: List[VirtualDataSource],
    transformations: List[Transformation],
    schedule_interval: Optional[pendulum.Duration] = None,
) -> MaterializationPlan:
    df = pipeline_to_dataframe(
        spark,
        feature_definition.fv.pipeline,
        consume_streaming_data_sources,
        data_sources,
        transformations,
        feature_time_limits=feature_data_time_limits,
        schedule_interval=schedule_interval,
    )
    spark_df = _apply_or_check_feature_data_time_limits(
        spark, df, feature_definition.time_range_policy, feature_definition.timestamp_key, feature_data_time_limits
    )

    trailing_time_window_aggregation = feature_definition.trailing_time_window_aggregation
    df = construct_partial_time_aggregation_df(
        spark_df,
        list(feature_definition.join_keys),
        trailing_time_window_aggregation,
        feature_definition.get_feature_store_format_version,
    )

    return MaterializationPlan(df, feature_definition)


def _get_batch_materialization_plan_for_temporal_feature_view(
    spark: SparkSession,
    feature_definition: FeatureDefinition,
    consume_streaming_data_sources: bool,
    feature_data_time_limits: pendulum.Period,
    data_sources: List[VirtualDataSource],
    transformations: List[Transformation],
    schedule_interval: Optional[pendulum.Duration] = None,
) -> MaterializationPlan:
    df = _materialize_interval_for_temporal_feature_view(
        spark,
        feature_definition,
        feature_data_time_limits,
        data_sources,
        transformations,
        consume_streaming_data_sources,
        schedule_interval=schedule_interval,
    )

    return MaterializationPlan(df, feature_definition)


def _materialize_interval_for_temporal_feature_view(
    spark: SparkSession,
    fd: FeatureDefinition,
    feature_data_time_limits: pendulum.Period,
    data_sources: List[VirtualDataSource],
    transformations: List[Transformation],
    consume_streaming_data_sources: bool,
    schedule_interval: Optional[pendulum.Duration] = None,
) -> DataFrame:
    tile_df = pipeline_to_dataframe(
        spark,
        fd.pipeline,
        consume_streaming_data_sources,
        data_sources,
        transformations,
        feature_time_limits=feature_data_time_limits,
        schedule_interval=schedule_interval,
    )

    tile_df = _apply_or_check_feature_data_time_limits(
        spark, tile_df, fd.time_range_policy, fd.timestamp_key, feature_data_time_limits
    )

    # We infer partition column (i.e. anchor time) by looking at the feature timestamp column and grouping
    # all the features within `[anchor_time,  anchor_time + batch_schedule)` together.
    version = fd.get_feature_store_format_version
    anchor_time_val = convert_timestamp_to_epoch(functions.col(fd.timestamp_key), version)
    batch_mat_schedule = convert_timedelta_for_version(fd.batch_materialization_schedule, version)
    return tile_df.withColumn(TEMPORAL_ANCHOR_COLUMN_NAME, anchor_time_val - anchor_time_val % batch_mat_schedule)


def _apply_or_check_feature_data_time_limits(
    spark: SparkSession,
    feature_df: DataFrame,
    time_range_policy: MaterializationTimeRangePolicy,
    timestamp_key: str,
    feature_data_time_limits: Optional[pendulum.Period],
) -> DataFrame:
    if time_range_policy == MaterializationTimeRangePolicy.MATERIALIZATION_TIME_RANGE_POLICY_FAIL_IF_OUT_OF_RANGE:
        return _validate_feature_timestamps(spark, feature_df, feature_data_time_limits, timestamp_key)
    elif time_range_policy == MaterializationTimeRangePolicy.MATERIALIZATION_TIME_RANGE_POLICY_FILTER_TO_RANGE:
        return _filter_to_feature_data_time_limits(feature_df, feature_data_time_limits, timestamp_key)
    else:
        raise ValueError(f"Unhandled time range policy: {time_range_policy}")


def _filter_to_feature_data_time_limits(
    feature_df: DataFrame,
    feature_data_time_limits: Optional[pendulum.Period],
    timestamp_key: Optional[str],
) -> DataFrame:
    if feature_data_time_limits:
        feature_df = feature_df.filter(
            (feature_df[timestamp_key] >= feature_data_time_limits.start)
            & (feature_df[timestamp_key] < feature_data_time_limits.end)
        )

    return feature_df


def _ensure_timestamp_validation_udf_registered(spark):
    """
    Register the Spark UDF that is contained in the JAR files and that is part of passed Spark session.
    If the UDF was already registered by the previous calls, do nothing. This is to avoid calling the JVM
    registration code repeatedly, which can be flaky due to Spark. We cannot use `SHOW USER FUNCTIONS` because
    there is a bug in the AWS Glue Catalog implementation that omits the catalog ID.

    Jars are included the following way into the Spark session:
     - For materialization jobs scheduled by Orchestrator, they are included in the Job submission API.
       In this case, we always use the default Spark session of the spun-up Spark cluster.
     - For interactive execution (or remote over db-connect / livy), we always construct Spark session
       manually and include appropriate JARs ourselves.
    """
    global TIMESTAMP_VALIDATOR_UDF_REGISTERED
    if not TIMESTAMP_VALIDATOR_UDF_REGISTERED:
        udf_generator = spark.sparkContext._jvm.com.tecton.udfs.spark3.RegisterFeatureTimestampValidator()
        udf_generator.register(TECTON_FEATURE_TIMESTAMP_VALIDATOR)
        TIMESTAMP_VALIDATOR_UDF_REGISTERED = True


def _validate_feature_timestamps(
    spark: SparkSession,
    feature_df: DataFrame,
    feature_data_time_limits: Optional[pendulum.Period],
    timestamp_key: Optional[str],
) -> DataFrame:
    if conf.get_or_none(SKIP_FEATURE_TIMESTAMP_VALIDATION_ENV) is True:
        logger.info(
            f"Note: skipping the feature timestamp validation step because `SKIP_FEATURE_TIMESTAMP_VALIDATION` is set to true."
        )
        return feature_df

    if feature_data_time_limits:
        _ensure_timestamp_validation_udf_registered(spark)

        start_time_expr = f"to_timestamp('{feature_data_time_limits.start}')"
        # Registered feature timestamp validation UDF checks that each timestamp is within *closed* time interval: [start_time, end_time].
        # So we subtract 1 microsecond here, before passing time limits to the UDF.
        end_time_expr = f"to_timestamp('{feature_data_time_limits.end - pendulum.duration(microseconds=1)}')"
        filter_expr = f"{TECTON_FEATURE_TIMESTAMP_VALIDATOR}({timestamp_key}, {start_time_expr}, {end_time_expr}, '{timestamp_key}')"

        # Force the output of the UDF to be filtered on, so the UDF cannot be optimized away.
        feature_df = feature_df.where(filter_expr)

    return feature_df


def get_stream_materialization_plan(
    spark: SparkSession,
    data_sources: List[VirtualDataSource],
    transformations: List[Transformation],
    feature_definition: FeatureDefinition,
) -> MaterializationPlan:
    transformations = transformations or []

    df = pipeline_to_dataframe(spark, feature_definition.pipeline, True, data_sources, transformations)
    if feature_definition.is_temporal_aggregate:
        df = construct_partial_time_aggregation_df(
            df,
            list(feature_definition.join_keys),
            feature_definition.trailing_time_window_aggregation,
            feature_definition.get_feature_store_format_version,
        )

    query_tree = build_run_querytree(feature_definition, for_stream=True)
    rewrite_tree(query_tree)
    return MaterializationPlan(df, feature_definition, query_tree, spark)
