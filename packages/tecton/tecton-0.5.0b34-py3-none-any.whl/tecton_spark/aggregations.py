from typing import List
from typing import Optional

import pendulum
from pyspark.sql import DataFrame
from pyspark.sql import functions
from pyspark.sql import SparkSession
from pyspark.sql.window import Window

from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_core.time_utils import convert_timedelta_for_version
from tecton_proto.common import aggregation_function_pb2
from tecton_proto.data.feature_store_pb2 import FeatureStoreFormatVersion
from tecton_proto.data.feature_view_pb2 import TrailingTimeWindowAggregation
from tecton_spark.aggregation_plans import get_aggregation_plan
from tecton_spark.materialization_params import MaterializationParams
from tecton_spark.partial_aggregations import TEMPORAL_ANCHOR_COLUMN_NAME


def construct_full_tafv_df_with_anchor_time(
    spark: SparkSession,
    time_aggregation: TrailingTimeWindowAggregation,
    join_keys: List[str],
    feature_store_format_version: FeatureStoreFormatVersion,
    tile_interval: pendulum.Duration,
    fd: FeatureDefinition = None,
    spine_join_keys: Optional[List[str]] = None,
    wildcard_join_keys: Optional[List[str]] = None,
    spine_df: Optional[DataFrame] = None,
    all_partial_aggregations_df: Optional[DataFrame] = None,
    use_materialized_data: bool = True,
    raw_data_time_limits: Optional[pendulum.Period] = None,
    wildcard_key_not_in_spine: bool = False,
):
    # TODO: drop anchor time concept from full aggregations. Define start & end times of the aggregation window,
    # use the new concepts for joining, and for returning the temporal aggregate feature dataframes

    if wildcard_key_not_in_spine and wildcard_join_keys:
        assert spine_join_keys is not None
        spine_join_keys.remove(wildcard_join_keys)

    if not spine_df:
        # If spine isn't provided, the fake timestamp equals to anchor time + tile_interval, s.t. the output timestamp
        # completely contains the time range of the fully aggregated window. Note, that ideally we would either subtract
        # 1 second from the timestamp, due to tiles having [start, end) format, or convert tiles in (start, end] format.
        # For now, we're not doing 1 due to it being confusing in preview, and not doing 2 due to it requiring more work
        partial_aggregations_df = all_partial_aggregations_df.withColumn(
            TEMPORAL_ANCHOR_COLUMN_NAME,
            functions.col(TEMPORAL_ANCHOR_COLUMN_NAME)
            + convert_timedelta_for_version(tile_interval, feature_store_format_version),
        )
    else:
        if not fd:
            raise ValueError("fd argument must not be None when spine_df is provided.")

        # TODO: drop anchor column and keep original spine timestamp
        # If spine is provided, round down the time key to the most recent anchor and right join on it + join_keys
        # TODO: ^ see if the above is actually even a good idea because it could hurt our ability to push down filters to the offline store.
        materialization_params = MaterializationParams.from_feature_definition(fd)
        spine_df = spine_df.select(
            materialization_params.most_recent_anchor_time(functions.to_timestamp(time_aggregation.time_key)).alias(
                TEMPORAL_ANCHOR_COLUMN_NAME
            ),
            *spine_join_keys,
        ).distinct()
        # In order to get the training dataframe, we first inner-join all_partial_aggregations_df to spine_df on join keys.
        # This ensures that the resulting df only contains the join keys that we have in spine.
        partial_aggregations_df = all_partial_aggregations_df.join(
            spine_df.select(spine_join_keys).distinct(), spine_join_keys, how="inner"
        )

        # TODO: handle wildcards
        if wildcard_key_not_in_spine and wildcard_join_keys:
            raise NotImplementedError
            """
            # Cache `partial_aggregations_df` as it is used multiple times for joining below
            partial_aggregations_df.cache()

            # If spine does not contain wildcard key, for specific fully bound join_keys and feature timestamp
            # we should find all the values of wildcard join_key that will be present in the feature aggregation
            # window ending at the feature timestamp.
            spine_with_all_join_keys = construct_spine_with_all_join_keys_for_TAFV(
                spine_df,
                partial_aggregations_df,
                fd,
                spine_join_keys,
            )
            """
        else:
            spine_with_all_join_keys = spine_df

        # Make sure the all join keys & anchor times that occur in spine exist in the partially aggregated df
        # This is necessary in the case when the exact anchor time is missing from partially aggregated df,
        # but the previous tiles belonging to the full aggregation window are available. In this case we shouldn't
        # return null, instead we need to aggregate the existing tiles and return the response.
        partial_aggregations_df = partial_aggregations_df.join(
            spine_with_all_join_keys, on=join_keys + [TEMPORAL_ANCHOR_COLUMN_NAME], how="outer"
        )

    aggregations = []
    for feature in time_aggregation.features:
        # We do + 1 since RangeBetween is inclusive, and we do not want to include the last row of the
        # previous tile. See https://github.com/tecton-ai/tecton/pull/1110
        window_duration = pendulum.Duration(seconds=feature.window.ToSeconds())
        upper_range = -(convert_timedelta_for_version(window_duration, feature_store_format_version)) + 1
        window_spec = (
            Window.partitionBy(join_keys)
            .orderBy(functions.col(TEMPORAL_ANCHOR_COLUMN_NAME).asc())
            .rangeBetween(upper_range, 0)
        )
        aggregation_plan = get_aggregation_plan(
            feature.function, feature.function_params, time_aggregation.is_continuous, time_aggregation.time_key
        )
        names = aggregation_plan.materialized_column_names(feature.input_feature_name)
        input_columns = [functions.col(name) for name in names]

        if feature.function == aggregation_function_pb2.AGGREGATION_FUNCTION_LASTN:
            # There isn't an Scala Encoder that works with a list directly, so instead we wrap the list in an object. Here we
            # strip the object to get just the list.
            agg = aggregation_plan.full_aggregation_transform(names[0], window_spec).values
        else:
            agg = aggregation_plan.full_aggregation_transform(input_columns, window_spec)

        # respect feature start time
        if fd and fd.feature_start_timestamp:
            materialization_params = MaterializationParams.from_feature_definition(fd)
            filtered_agg = functions.when(
                functions.col(TEMPORAL_ANCHOR_COLUMN_NAME)
                >= functions.lit(materialization_params.most_recent_anchor_time(fd.feature_start_timestamp)),
                agg,
            ).otherwise(functions.lit(None))
        else:
            filtered_agg = agg
        aggregations.append(filtered_agg.alias(feature.output_feature_name))

    output_df = partial_aggregations_df.select(join_keys + [TEMPORAL_ANCHOR_COLUMN_NAME] + aggregations)

    return output_df
