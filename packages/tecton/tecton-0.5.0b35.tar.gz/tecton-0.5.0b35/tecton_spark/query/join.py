from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.functions import last
from pyspark.sql.functions import lit
from pyspark.sql.window import Window

from tecton_core import conf
from tecton_core.query.nodes import AsofJoinNode
from tecton_core.query.nodes import JoinNode
from tecton_spark.query import translate
from tecton_spark.query.node import SparkExecNode


class JoinSparkNode(SparkExecNode):
    """
    A basic left join on 2 inputs
    """

    def __init__(self, node: JoinNode):
        self.left = translate.spark_convert(node.left)
        self.right = translate.spark_convert(node.right)
        self.join_cols = node.join_cols
        self.how = node.how

    def to_dataframe(self, spark: SparkSession):
        left_df = self.left.to_dataframe(spark)
        right_df = self.right.to_dataframe(spark)
        return left_df.join(right_df, how=self.how, on=self.join_cols)


class AsofJoinSparkNode(SparkExecNode):
    """
    A "basic" asof join on 2 inputs.
    LEFT asof_join RIGHT has the following behavior:
        For each row on the left side, find the latest (but <= in time) matching (by join key) row on the right side, and associate the right side's columns to that row.
    The result is a dataframe with the same number of rows as LEFT, with additional columns. These additional columns are prefixed with f"{right_prefix}_". This is the built-in behavior of the tempo library.

    There are a few ways this behavior can be implemented, but by test the best performing method has been to union the two inputs and use a "last" window function with skip_nulls.
    In order to match the rows together.
    """

    def __init__(self, node: AsofJoinNode):
        self.left = translate.spark_convert(node.left)
        self.right = translate.spark_convert(node.right)
        self.timestamp_field = node.timestamp_field
        self.join_cols = node.join_cols
        self.right_prefix = node.right_prefix

    def to_dataframe(self, spark: SparkSession):
        if conf.get_bool("ENABLE_TEMPO"):
            from tempo import TSDF

            # We'd like to do the following:
            left_df = self.left.to_dataframe(spark)
            right_df = self.right.to_dataframe(spark)
            left_tsdf = TSDF(left_df, ts_col=self.timestamp_field, partition_cols=self.join_cols)
            right_tsdf = TSDF(right_df, ts_col=self.timestamp_field, partition_cols=self.join_cols)
            # TODO(TEC-9494) - we could speed up by setting partition_ts to ttl size
            out = left_tsdf.asofJoin(right_tsdf, right_prefix=self.right_prefix, skipNulls=False).df
            return out
        else:
            left_df = self.left.to_dataframe(spark)
            right_df = self.right.to_dataframe(spark)
            # includes both fv join keys and the temporal asof join key
            common_cols = self.join_cols + [self.timestamp_field]
            left_nonjoin_cols = [x for x in left_df.columns if x not in common_cols]
            # we additionally include the right time field though we join on the left's time field.
            # This is so we can see how old the row we joined against is and later determine whether to exclude on basis of ttl
            right_nonjoin_cols = [x for x in right_df.columns if x not in self.join_cols]
            left_full_cols = (
                [lit(True).alias("is_left")]
                + [col(x) for x in common_cols]
                + [col(x) for x in left_nonjoin_cols]
                + [lit(None).alias(f"{self.right_prefix}_{x}") for x in right_nonjoin_cols]
            )
            right_full_cols = (
                [lit(False).alias("is_left")]
                + [col(x) for x in common_cols]
                + [lit(None).alias(x) for x in left_nonjoin_cols]
                + [col(x).alias(f"{self.right_prefix}_{x}") for x in right_nonjoin_cols]
            )
            left_df = left_df.select(left_full_cols)
            right_df = right_df.select(right_full_cols)
            union = left_df.union(right_df)
            window_spec = (
                Window.partitionBy(self.join_cols)
                .orderBy(col(self.timestamp_field).cast("long").asc())
                .rangeBetween(Window.unboundedPreceding, Window.currentRow)
            )
            right_window_funcs = []
            for column_name in right_nonjoin_cols:
                right_window_funcs.append(
                    last(col(f"{self.right_prefix}_{column_name}"), ignorenulls=True)
                    .over(window_spec)
                    .alias(f"{self.right_prefix}_{column_name}")
                )

            # We use the right side of asof join to find the latest values to augment to the rows from the left side.
            # Then, we drop the right side's rows.
            res = union.select(common_cols + left_nonjoin_cols + right_window_funcs).filter(f"is_left").drop("is_left")
            return res
