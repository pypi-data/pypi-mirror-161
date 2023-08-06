from pyspark.sql import SparkSession

from tecton_core.query.nodes import FeatureViewPipelineNode
from tecton_core.query.nodes import FullAggNode
from tecton_core.query.nodes import OdfvPipelineNode
from tecton_core.query.nodes import PartialAggNode
from tecton_spark.aggregations import construct_full_tafv_df_with_anchor_time
from tecton_spark.partial_aggregations import construct_partial_time_aggregation_df
from tecton_spark.pipeline_helper import _PipelineBuilder
from tecton_spark.pipeline_helper import dataframe_with_input
from tecton_spark.query import translate
from tecton_spark.query.node import SparkExecNode
from tecton_spark.schema_spark_utils import schema_to_spark


class OdfvPipelineSparkNode(SparkExecNode):
    def __init__(self, node: OdfvPipelineNode):
        self.input_node = translate.spark_convert(node.input_node)
        self.feature_definition_wrapper = node.feature_definition_wrapper
        self.namespace = node.namespace

    def to_dataframe(self, spark: SparkSession):
        return dataframe_with_input(
            spark,
            self.feature_definition_wrapper.pipeline,
            self.input_node.to_dataframe(spark),
            schema_to_spark(self.feature_definition_wrapper.view_schema),
            transformations=self.feature_definition_wrapper.transformations,
            name=self.feature_definition_wrapper.name,
            fv_id=self.feature_definition_wrapper.id,
            namespace_separator=self.feature_definition_wrapper.namespace_separator,
            namespace=self.namespace,
        )


class PipelineEvalSparkNode(SparkExecNode):
    def __init__(self, node: FeatureViewPipelineNode):
        self.inputs_map = {key: translate.spark_convert(node.inputs_map[key]) for key in node.inputs_map}
        self.feature_definition_wrapper = node.feature_definition_wrapper
        # Needed for correct behavior on MaterializationContextNode in the pipeline
        self.feature_time_limits = node.feature_time_limits
        self.schedule_interval = node.schedule_interval

    def to_dataframe(self, spark: SparkSession):
        return _PipelineBuilder(
            spark,
            self.feature_definition_wrapper.pipeline,
            consume_streaming_data_sources=False,
            data_sources=self.feature_definition_wrapper.data_sources,
            transformations=self.feature_definition_wrapper.transformations,
            feature_time_limits=self.feature_time_limits,
            schedule_interval=self.schedule_interval,
            passed_in_inputs={k: self.inputs_map[k].to_dataframe(spark) for k in self.inputs_map},
        ).get_dataframe()


class PartialAggSparkNode(SparkExecNode):
    def __init__(self, node: PartialAggNode):
        self.input_node = translate.spark_convert(node.input_node)
        self.fdw = node.fdw

    def to_dataframe(self, spark: SparkSession):
        df = construct_partial_time_aggregation_df(
            self.input_node.to_dataframe(spark),
            list(self.fdw.join_keys),
            self.fdw.trailing_time_window_aggregation,
            self.fdw.get_feature_store_format_version,
        )
        return df


class FullAggSparkNode(SparkExecNode):
    def __init__(self, node: FullAggNode):
        self.input_node = translate.spark_convert(node.input_node)
        self.fdw = node.fdw
        self.spine = node.spine
        self.spine_time_field = node.spine_time_field
        self.spine_join_keys = node.spine_join_keys
        if self.spine_time_field is None:
            # We have not implemented the case for full agg without spine
            raise NotImplementedError

    def to_dataframe(self, spark: SparkSession):

        # convert the spine's join/time keys into the feature view's join/time key.
        converted_spine = self.spine.withColumnRenamed(self.spine_time_field, self.fdw.timestamp_key)
        for key_pair in self.spine_join_keys:
            # TODO: handle case where the same spine key maps to different fv join keys
            converted_spine = converted_spine.withColumnRenamed(key_pair[0], key_pair[1])

        res = construct_full_tafv_df_with_anchor_time(
            spark=spark,
            time_aggregation=self.fdw.trailing_time_window_aggregation,
            join_keys=self.fdw.join_keys,
            feature_store_format_version=self.fdw.get_feature_store_format_version,
            tile_interval=self.fdw.get_tile_interval,
            all_partial_aggregations_df=self.input_node.to_dataframe(spark),
            use_materialized_data=False,
            spine_df=converted_spine,
            fd=self.fdw,
            spine_join_keys=self.fdw.join_keys,
        )
        return res
