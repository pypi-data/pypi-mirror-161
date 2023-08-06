from typing import Optional


# NOTE: When adding a new format, change data_source_helper.py:_partition_value_for_time if needed
class DatetimePartitionColumn:
    """
    Helper class to tell Tecton how underlying flat files are date/time partitioned for Hive/Glue data sources. This can translate into a significant performance increase.

    You will generally include an object of this class in the `datetime_partition_columns` option in a `HiveConfig` object.
    """

    # pass zero_padded=True if the partition column is a string that is zero-padded
    def __init__(self, column_name, datepart: str, zero_padded: bool = False, format_string: Optional[str] = None):
        """
        Instantiates a new DatetimePartitionColumn configuration object.


        :param column_name: The name of the column in the Glue/Hive schema that corresponds to the underlying date/time partition folder. Note that if you do not explicitly specify a name in your partition folders, Glue will name the column of the form ``partition_0``.
        :param datepart: The part of the date that this column specifies. Can be one of "year", "month", "day", "hour", or the full "date". If used with ``format_string``, this should be the size of partition being represented, e.g. ``datepart="month"`` for ``format_string="%Y-%m"``.
        :param zero_padded: Whether the ``datepart`` has a leading zero if less than two digits. This must be set to True if ``datepart="date"``. (Should not be set if ``format_string`` is set.)
        :param format_string:
            A ``datetime.strftime`` format string override for "non-default" partition columns formats. E.g. ``"%Y%m%d"`` for ``datepart="date"`` instead of the Tecton default ``"%Y-%m-%d"``, or ``"%Y-%m"`` for ``datepart="month"`` instead of the Tecton default ``"%m"``.

            IMPORTANT: This format string must convert python datetimes (via ``datetime.strftime(format)``) to strings that are sortable in time order. For example, ``"%m-%Y"`` would be an invalid format string because ``"09-2019" > "05-2020"``.

            See https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes for format codes.

        Example definitions:

            Assume you have an S3 bucket with parquet files stored in the following structure: ``s3://mybucket/2022/05/04/<multiple parquet files>`` , where ``2022`` is the year, ``05`` is the month, and ``04`` is the day of the month. In this scenario, you could use the following definition:

            .. code-block:: python

                datetime_partition_columns = [
                    DatetimePartitionColumn(column_name="partition_0", datepart="year", zero_padded=True),
                    DatetimePartitionColumn(column_name="partition_1", datepart="month", zero_padded=True),
                    DatetimePartitionColumn(column_name="partition_2", datepart="day", zero_padded=True),
                ]

            Example using the ``format_string`` parameter. Assume your data is partitioned by ``"YYYY-MM"``, e.g. ``s3://mybucket/2022-05/<multiple parquet files>``. Tecton's default month format is ``"%m"``, which would fail to format datetime strings that are comparable to your table's partition column, so the definition needs to specify an override.

            .. code-block:: python

                datetime_partition_columns = [
                    DatetimePartitionColumn(column_name="partition_1", datepart="month", format_string="%Y-%m"),
                ]

        :return: DatetimePartitionColumn instantiation
        """
        self.column_name = column_name
        self.datepart = datepart
        self.zero_padded = zero_padded
        self.format_string = format_string
