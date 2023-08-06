from pyspark.sql import DataFrame

from tecton_core.query.nodes import DataNode
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.nodes import OfflineStoreScanNode
from tecton_spark import data_source_helper
from tecton_spark import offline_store
from tecton_spark.query.node import SparkExecNode


class DataSparkNode(SparkExecNode):
    def __init__(self, node: DataNode):
        self.data = node.data

    def to_dataframe(self, spark):
        if isinstance(self.data, DataFrame):
            return self.data
        else:
            raise Exception(f"Unimplemented data type: {self.data}")


class DataSourceScanSparkNode(SparkExecNode):
    def __init__(self, node: DataSourceScanNode):
        self.ds = node.ds
        self.time_filter = node.time_filter
        self.is_stream = node.is_stream

    def to_dataframe(self, spark):
        start_time = self.time_filter.start if self.time_filter else None
        end_time = self.time_filter.end if self.time_filter else None
        return data_source_helper.get_ds_dataframe(
            spark, self.ds, consume_streaming_data_source=self.is_stream, start_time=start_time, end_time=end_time
        )


class OfflineStoreScanSparkNode(SparkExecNode):
    def __init__(self, node: OfflineStoreScanNode):
        self.feature_definition_wrapper = node.feature_definition_wrapper
        self.time_filter = node.time_filter

    def to_dataframe(self, spark):
        offline_reader = offline_store.get_offline_store_reader(spark, self.feature_definition_wrapper)
        # None implies no timestamp filtering. When we implement time filter pushdown, it will go here
        return offline_reader.read(self.time_filter)
