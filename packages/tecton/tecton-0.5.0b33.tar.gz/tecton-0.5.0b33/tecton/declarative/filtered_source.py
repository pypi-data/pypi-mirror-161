import datetime
from typing import Optional

from typeguard import typechecked

from tecton.declarative.base import BaseDataSource


class FilteredSource:
    """
    FilteredSource is a convenience utility that can be used to pre-filter ``sources`` in Feature View definitions.

    :param source: Data Source that this FilteredSource class wraps.
    :param start_time_offset: FilteredSource will pre-filter the data source to the time range ``[start_time + start_time_offset, end_time)``. Must be zero or negative. Defaults to zero.
    :return: A FilteredSource to pass into a Feature View.

    Filters ``source`` to the time range ``[start_time + start_time_offset, end_time)`` before executing the feature view transformation. When materializing a range, the output of FeatureViews is automatically filtered by Tecton to the range ``[start_time, end_time)``. In most cases, using a FilteredSource is a performance optimization for when the query engine fails to "push down" timestamp filtering.

    If ``source`` has configured :class:`tecton.declarative.DatetimePartitionColumn`, Tecton will automatically apply partition filters, which can significantly improve performance.

    To filter only on the end time, use ``FilteredSource(credit_scores, start_time_offset=datetime.timedelta.min)``.

    .. code-block:: python

        from tecton import batch_feature_view, BatchSource, HiveConfig, materialization_context, DatetimePartitionColumn
        from tecton import FilteredSource

        # Declare a BatchSource. `timestamp_field` is normally optional, but it is required when the source is used
        # with a FilteredSource. `datetime_partition_columns` is also recommended and will help improve time
        # filtering efficiency.
        partition_columns = [
            DatetimePartitionColumn(column_name="partition_0", datepart="year", zero_padded=True),
            DatetimePartitionColumn(column_name="partition_1", datepart="month", zero_padded=True),
            DatetimePartitionColumn(column_name="partition_2", datepart="day", zero_padded=True),
        ]
        credit_scores = BatchSource(
            name='credit_scores_batch',
            batch_config= HiveConfig(
                database='demo_fraud',
                table='credit_scores',
                timestamp_field='timestamp',
                datetime_partition_columns=partition_columns))

        # Declare a batch feature view with `credit_scores` as a source.
        @batch_feature_view(
            sources=[FilteredSource(credit_scores)],
            ...
        )
        def user_credit_score(credit_scores):
            return f'''
                SELECT user_id, timestamp, credit_score
                FROM {credit_scores}
                '''

        # The above feature view query is equivalent to:
        @batch_feature_view(
            sources=[credit_scores],
            ...
        )
        def user_credit_score(credit_scores, context=materialization_context()):
            return f'''
                WITH FILTERED_CREDIT_SCORES AS (
                    SELECT *
                    FROM {credit_scores}
                    WHERE
                        timestamp >= to_timestamp("{context.start_time}")
                        AND timestamp < to_timestamp("{context.end_time}")
                        -- AND additional clauses if the data source has datetime_partition_columns configured.
                )
                SELECT user_id, timestamp, credit_score
                FROM FILTERED_CREDIT_SCORES
                '''
    """

    @typechecked
    def __init__(self, source: BaseDataSource, start_time_offset: Optional[datetime.timedelta] = None):
        self.source = source
        if start_time_offset is None:
            start_time_offset = datetime.timedelta(0)
        self.start_time_offset = start_time_offset
