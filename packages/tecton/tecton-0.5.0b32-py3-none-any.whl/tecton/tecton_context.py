from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import pandas
import pendulum
import pyspark

import tecton.interactive.data_frame
from tecton._internals import errors
from tecton._internals.sdk_decorators import sdk_public_method
from tecton._internals.spark_utils import get_or_create_spark_session
from tecton_core import logger as logger_lib
from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition


logger = logger_lib.get_logger("TectonContext")


class TectonContext:
    """
    Execute Spark SQL queries; access various utils.
    """

    _current_context_instance = None
    _config: Dict[str, Any] = {}

    def __init__(self, spark):
        self._spark = spark

    @classmethod
    def _set_config(cls, custom_spark_options=None):
        """
        Sets the configs for TectonContext instance.
        To take effect it must be called before any calls to TectonContext.get_instance().

        :param custom_spark_options: If spark session gets created by TectonContext, custom spark options/
        """
        cls._config = {"custom_spark_options": custom_spark_options}

    @classmethod
    @sdk_public_method
    def get_instance(cls) -> "TectonContext":
        """
        Get the singleton instance of TectonContext.
        """
        # If the instance doesn't exist, creates a new TectonContext from
        # an existing Spark context. Alternatively, creates a new Spark context on the fly.
        if cls._current_context_instance is not None:
            return cls._current_context_instance
        else:
            return cls._generate_and_set_new_instance()

    @classmethod
    def _generate_and_set_new_instance(cls) -> "TectonContext":
        logger.debug(f"Generating new Spark session")
        spark = get_or_create_spark_session(
            cls._config.get("custom_spark_options"),
        )
        cls._current_context_instance = cls(spark)
        return cls._current_context_instance

    def _list_tables(self):
        """
        Lists the registered tables.

        :return: An array of tables.
        """
        tables = []
        spark_databases = self._spark.catalog.listDatabases()

        for db in spark_databases:
            spark_tables = self._spark.catalog.listTables(db.name)
            for t in spark_tables:
                if db.name == "default":
                    tables.append(t.name)
                else:
                    tables.append("{database}.{table}".format(database=db.name, table=t.name))
        return tables

    # A user-facing validation method
    @classmethod
    def validate_spine_type(cls, spine: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, None]):
        if not isinstance(spine, (pyspark.sql.dataframe.DataFrame, pandas.DataFrame, type(None))):
            raise errors.INVALID_SPINE_TYPE(type(spine))

    # Validates and returns a spark df constructed from the spine.
    # This is an internal method and supports more types than what we support in the user-facing
    # methods, see validate_spine_type
    def _get_spine_df(
        self,
        spine: Union[str, dict, pyspark.sql.dataframe.DataFrame, list, pandas.DataFrame, pyspark.RDD, None],
    ):
        df = None

        # sql
        if isinstance(spine, str):
            df = self._spark.sql(spine)
        # entity dict
        elif isinstance(spine, dict):
            # TODO(there is probably a much more efficient way to have spark join against temporary single row tables)
            df = self._spark.createDataFrame(pandas.DataFrame([spine]))
        elif isinstance(spine, tecton.interactive.data_frame.DataFrame):
            df = spine.to_spark()
        elif isinstance(spine, pyspark.sql.dataframe.DataFrame):
            df = spine
        elif isinstance(spine, (pandas.DataFrame, list, pyspark.RDD)):
            df = self._spark.createDataFrame(spine)
        elif spine is None:
            pass
        else:
            raise errors.INVALID_SPINE_TYPE(type(spine))
        return df

    def _register_temp_views_for_feature_view(
        self,
        fd: FeatureDefinition,
        register_stream=False,
        raw_data_time_limits: Optional[pendulum.Period] = None,
    ):
        for ds in fd.data_sources:
            self._register_temp_view_for_data_source(
                ds, register_stream=register_stream, raw_data_time_limits=raw_data_time_limits
            )

    def _register_temp_view_for_data_source(
        self,
        data_source_proto,
        register_stream=False,
        raw_data_time_limits: Optional[pendulum.Period] = None,
    ):
        from tecton_spark.data_source_helper import register_temp_view_for_data_source

        name = data_source_proto.fco_metadata.name

        register_temp_view_for_data_source(
            self._spark,
            data_source_proto,
            register_stream=register_stream,
            raw_data_time_limits=raw_data_time_limits,
            name=name,
        )

    def _get_spark(self):
        return self._spark
