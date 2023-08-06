import datetime
import enum
import functools
from dataclasses import dataclass
from inspect import signature
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

import attr
import pandas
import pendulum
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from typeguard import typechecked

from tecton._internals.errors import FV_INVALID_MOCK_SOURCES
from tecton._internals.fco import Fco
from tecton._internals.feature_definition import FeatureDefinition
from tecton.aggregation_functions import AggregationFunction
from tecton.declarative.base import BaseDataSource
from tecton.declarative.base import BaseEntity
from tecton.declarative.base import FWV5BaseDataSource
from tecton.declarative.base import OutputStream
from tecton.declarative.basic_info import prepare_basic_info
from tecton.declarative.data_source import BatchSource
from tecton.declarative.data_source import RequestSource
from tecton.declarative.data_source import StreamSource
from tecton.declarative.filtered_source import FilteredSource
from tecton.declarative.run import declarative_run
from tecton.declarative.run import get_transformations
from tecton.declarative.transformation import Transformation
from tecton.declarative.transformation import transformation
from tecton.feature_services.feature_service_args import FeaturesConfig
from tecton.features_common.feature_configs import DatabricksClusterConfig
from tecton.features_common.feature_configs import DeltaConfig
from tecton.features_common.feature_configs import DynamoConfig
from tecton.features_common.feature_configs import EMRClusterConfig
from tecton.features_common.feature_configs import ExistingClusterConfig
from tecton.features_common.feature_configs import MonitoringConfig
from tecton.features_common.feature_configs import ParquetConfig
from tecton.features_common.feature_configs import RedisConfig
from tecton.types import Field
from tecton.types import to_spark_schema_wrapper
from tecton_core import logger as logger_lib
from tecton_core.feature_definition_wrapper import FrameworkVersion
from tecton_core.id_helper import IdHelper
from tecton_core.pipeline_common import transformation_type_checker
from tecton_proto.args import feature_service_pb2
from tecton_proto.args import feature_view_pb2
from tecton_proto.args.feature_view_pb2 import AggregationMode as AggregationModeProto
from tecton_proto.args.feature_view_pb2 import BatchTriggerType as BatchTriggerTypeProto
from tecton_proto.args.feature_view_pb2 import EntityKeyOverride
from tecton_proto.args.feature_view_pb2 import FeatureViewArgs
from tecton_proto.args.feature_view_pb2 import FeatureViewType
from tecton_proto.args.feature_view_pb2 import MaterializedFeatureViewArgs
from tecton_proto.args.pipeline_pb2 import DataSourceNode
from tecton_proto.args.pipeline_pb2 import FeatureViewNode
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.args.pipeline_pb2 import RequestContext as RequestContextProto
from tecton_proto.args.pipeline_pb2 import RequestDataSourceNode
from tecton_proto.args.virtual_data_source_pb2 import DataSourceType
from tecton_spark.materialization_context import BaseMaterializationContext
from tecton_spark.pipeline_helper import run_mock_odfv_pipeline
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper

# This is the mode used when the feature view decorator is used on a pipeline function, i.e. one that only contains
# references to transformations and constants.
PIPELINE_MODE = "pipeline"

# This is used for the low latency streaming feature views.
CONTINUOUS_MODE = "continuous"

# FilteredSource start offsets smaller (more negative) than this offset will be considered UNBOUNDED_PRECEEDING.
MIN_START_OFFSET = datetime.timedelta(days=-365 * 100)  # 100 years

logger = logger_lib.get_logger("DeclarativeFeatureView")


# Create a parallel enum class since Python proto extensions do not use an enum class.
# Keep up-to-date with AggregationMode from tecton_proto/args/feature_view.proto.
class AggregationMode(enum.Enum):
    TIME_INTERVAL = AggregationModeProto.AGGREGATION_MODE_TIME_INTERVAL
    CONTINUOUS = AggregationModeProto.AGGREGATION_MODE_CONTINUOUS


# Keep up-to-date with BatchTriggerType from tecton_proto/args/feature_view.proto.
class BatchTriggerType(enum.Enum):
    SCHEDULED = BatchTriggerTypeProto.BATCH_TRIGGER_TYPE_SCHEDULED
    MANUAL = BatchTriggerTypeProto.BATCH_TRIGGER_TYPE_MANUAL


@attr.s(auto_attribs=True)
class Aggregation(object):
    """
    This class describes a single aggregation that is applied in a batch or stream feature view.

    :param column: Column name of the feature we are aggregating.
    :type column: str
    :param function: One of the built-in aggregation functions.
    :type function: Union[str, AggregationFunction]
    :param time_window: Duration to aggregate over. Example: ``datetime.timedelta(days=30)``.
    :type time_window: datetime.timedelta
    :param name: The name of this feature. Defaults to an autogenerated name, e.g. transaction_count_7d_1d.
    :type name: str

    `function` can be one of predefined numeric aggregation functions, namely ``"count"``, ``"sum"``, ``"mean"``, ``"min"``, ``"max"``, ``"var_samp"``, ``"var_pop"``, ``"variance"`` - alias for ``"var_samp"``, ``"stddev_samp"``, ``"stddev_pop"``, ``"stddev"`` - alias for ``"stddev_samp"``. For
    these numeric aggregations, you can pass the name of it as a string. Nulls are handled like Spark SQL `Function(column)`, e.g. SUM/MEAN/MIN/MAX/VAR_SAMP/VAR_POP/VAR/STDDEV_SAMP/STDDEV_POP/STDDEV of all nulls is null and COUNT of all nulls is 0.

    In addition to numeric aggregations, :class:`Aggregation` supports "last-n" aggregations that
    will compute the last N distinct values for the column by timestamp. Right now only string column types are supported as inputs
    to this aggregation, i.e., the resulting feature value will be a list of strings. Nulls are not included in the aggregated list.

    You can use it via the ``last_distinct()`` helper function like this:

    .. code-block:: python

        from tecton.aggregation_functions import last_distinct

        @batch_feature_view(
        ...
        aggregations=[Aggregation(
            column='my_column',
            function=last_distinct(15),
            time_window=datetime.timedelta(days=7))],
        ...
        )
        def my_fv(data_source):
            pass

    """

    column: str
    """Column name of the feature we are aggregating."""
    function: Union[str, AggregationFunction]
    """One of the built-in aggregation functions (`'count'`, `'sum'`, `'mean'`, `'min'`, `'max'`, `'var_samp'`, `'var_pop'`, `'variance'`, `'stddev_samp'`, `'stddev_pop'`, `'stddev'`)."""
    time_window: datetime.timedelta
    """Example: ``datetime.timedelta(days=30)``"""
    name: Optional[str] = None
    """Example: ``datetime.timedelta(days=30)``"""

    def _to_proto(self):
        proto = feature_view_pb2.FeatureAggregation()
        proto.column = self.column

        if isinstance(self.function, str):
            proto.function = self.function
        elif isinstance(self.function, AggregationFunction):
            proto.function = self.function.name
            for k, v in self.function.params.items():
                assert isinstance(v, int)
                proto.function_params[k].CopyFrom(feature_view_pb2.ParamValue(int64_value=v))
        else:
            raise TypeError(f"Invalid function type: {type(self.function)}")

        if self.name:
            proto.name = self.name

        proto.time_window.FromTimedelta(self.time_window)
        return proto


def get_source_input_params(user_function) -> List[str]:
    # Filter out the materailization context to avoid mapping data sources to it.
    return [
        param.name
        for param in signature(user_function).parameters.values()
        if not isinstance(param.default, BaseMaterializationContext)
    ]


def prepare_common_fv_args(basic_info, entities, pipeline_function, params_to_sources, fv_type) -> FeatureViewArgs:
    args = FeatureViewArgs()
    args.feature_view_type = fv_type
    args.feature_view_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))

    args.framework_version = FrameworkVersion.FWV5.value
    args.version = FrameworkVersion.FWV5.value

    args.info.CopyFrom(basic_info)

    args.entities.extend([EntityKeyOverride(entity_id=entity._id, join_keys=entity.join_keys) for entity in entities])

    pipeline_kwargs = sources_to_pipeline_nodes(params_to_sources)
    pipeline_fn_result = pipeline_function(**pipeline_kwargs)

    if fv_type == FeatureViewType.FEATURE_VIEW_TYPE_ON_DEMAND:
        supported_modes = ["pipeline", "pandas", "python"]
    else:
        supported_modes = ["pipeline", "spark_sql", "snowflake_sql", "pyspark"]
    transformation_type_checker(basic_info.name, pipeline_fn_result, "pipeline", supported_modes)
    args.pipeline.root.CopyFrom(pipeline_fn_result)

    return args


def test_binding_user_function(fn, inputs):
    # this function binds the top-level pipeline function only, for transformation binding, see transformation.__call__
    pipeline_signature = signature(fn)
    try:
        pipeline_signature.bind(**inputs)
    except TypeError as e:
        raise TypeError(f"while binding inputs to pipeline function, TypeError: {e}")


def sources_to_pipeline_nodes(
    params_to_sources: Dict[
        str, Union[BaseDataSource, FilteredSource, RequestSource, FeatureDefinition, FeaturesConfig]
    ]
) -> Dict[str, PipelineNode]:
    kwargs = {}
    for param_name, source in params_to_sources.items():
        # Convert FeatureDefinition to FeaturesConfig
        if isinstance(source, FeatureDefinition):
            source = FeaturesConfig(feature_view=source, namespace=source.name)

        pipeline_node = PipelineNode()
        if isinstance(source, BaseDataSource):
            node = DataSourceNode()
            node.virtual_data_source_id.CopyFrom(source._id)
            node.window_unbounded = True
            if isinstance(source, FWV5BaseDataSource) and source.data_delay:
                node.schedule_offset.FromTimedelta(source.data_delay)

            node.input_name = param_name
            pipeline_node.data_source_node.CopyFrom(node)
        elif isinstance(source, FilteredSource):
            node = DataSourceNode()
            node.virtual_data_source_id.CopyFrom(source.source._id)
            if source.start_time_offset <= MIN_START_OFFSET:
                node.window_unbounded_preceding = True
            else:
                node.start_time_offset.FromTimedelta(source.start_time_offset)

            if isinstance(source.source, FWV5BaseDataSource) and source.source.data_delay:
                node.schedule_offset.FromTimedelta(source.source.data_delay)
            node.input_name = param_name
            pipeline_node.data_source_node.CopyFrom(node)
        elif isinstance(source, RequestSource):
            node = RequestDataSourceNode()
            request_schema = source.schema
            if isinstance(request_schema, List):
                wrapper = to_spark_schema_wrapper(request_schema)
            else:
                wrapper = SparkSchemaWrapper(request_schema)
            rc = RequestContextProto(schema=wrapper.to_proto())
            node.request_context.CopyFrom(rc)
            node.input_name = param_name
            pipeline_node.request_data_source_node.CopyFrom(node)
        elif isinstance(source, FeaturesConfig):
            node = FeatureViewNode()
            node.feature_view_id.CopyFrom(source.id)
            fsfv = feature_service_pb2.FeatureServiceFeaturePackage()
            if source.override_join_keys:
                fsfv.override_join_keys.extend(
                    feature_service_pb2.ColumnPair(spine_column=k, feature_column=v)
                    for k, v in sorted(source.override_join_keys.items())
                )
            fsfv.feature_package_id.CopyFrom(source.id)
            fsfv.namespace = source.namespace
            fsfv.features.extend(source.features)
            node.feature_view.CopyFrom(fsfv)
            node.input_name = param_name
            pipeline_node.feature_view_node.CopyFrom(node)
        else:
            raise TypeError(f"Invalid source type: {type(source)}")

        kwargs[param_name] = pipeline_node

    return kwargs


class OnDemandFeatureView(FeatureDefinition):
    """
    OnDemandFeatureView class to include in Feature Services or to use in unit testing.

    **Do not instantiate this class directly.** Use :class:`tecton.declarative.on_demand_feature_view` instead.
    """

    def __init__(
        self,
        *,  # All arguments must be specified with keywords
        schema,
        transform,
        name: str,
        description: Optional[str],
        tags: Optional[Dict[str, str]],
        pipeline_function,
        owner: Optional[str],
        sources: List[Union[RequestSource, FeatureDefinition, FeaturesConfig]],
        user_function,
    ):
        """
        **Do not directly use this constructor.** Internal constructor for OnDemandFeatureView.

        :param schema: Spark schema declaring the expected output.
        :param transform: Transformation used to produce the feature values.
        :param name: Unique, human friendly name.
        :param description: A human readable description.
        :param tags: Arbitrary key-value pairs of tagging metadata.
        :param pipeline_function: Pipeline definition function.
        :param owner: Owner name, used to organize features.
        :param sources: The data source inputs to the feature view.
        :param user_function: User-defined function.

        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=None, tags=tags)

        self.fn_params = get_source_input_params(user_function)
        params_to_sources = dict(zip(self.fn_params, sources))

        args = prepare_common_fv_args(
            basic_info=basic_info,
            entities=[],
            pipeline_function=pipeline_function,
            params_to_sources=params_to_sources,
            fv_type=FeatureViewType.FEATURE_VIEW_TYPE_ON_DEMAND,
        )

        # We bind to user_function since pipeline_function may be artificially created and just accept **kwargs
        test_binding_user_function(user_function, params_to_sources)

        if isinstance(schema, list):
            wrapper = to_spark_schema_wrapper(schema)
        else:
            wrapper = SparkSchemaWrapper(schema)
        args.on_demand_args.schema.CopyFrom(wrapper.to_proto())

        self._args = args
        self.inferred_transform = transform
        self.pipeline_function = pipeline_function
        self.schema = schema
        self.sources = sources

        Fco._register(self)

    @typechecked
    def run(self, **mock_sources: Union[Dict[str, Any], pandas.DataFrame]) -> Union[Dict[str, Any], pandas.DataFrame]:
        """
        Run the OnDemandFeatureView using mock sources.

        :param mock_sources: Required. Keyword args with the same expected keys
            as the OnDemandFeatureView's inputs parameters.
            For the "python" mode, each input must be a Dictionary representing a single row.
            For the "pandas" mode, each input must be a DataFrame with all of them containing the
            same number of rows and matching row ordering.

        Example:
            .. code-block:: python

                @on_demand_feature_view(
                    sources=[transaction_request],
                    mode='python',
                    schema=output_schema,
                )
                def transaction_amount_is_high(transaction_request):
                    return {'transaction_amount_is_high': transaction_request['amount'] > 10000}

                # Test using `run` API.
                result = transaction_amount_is_high.run(transaction_request={'amount': 100})

        :return: A `Dict` object for the "python" mode and a `pandas.DataFrame` object for the "pandas" mode".
        """
        if set(self.fn_params) != set(mock_sources.keys()):
            raise FV_INVALID_MOCK_SOURCES(mock_sources.keys(), self.fn_params)

        return run_mock_odfv_pipeline(
            self._args.pipeline, get_transformations(self._args), self._args.info.name, mock_sources
        )


@typechecked
def on_demand_feature_view(
    *,
    mode: str,
    sources: List[Union[RequestSource, FeatureDefinition, FeaturesConfig]],
    schema: Union[List[Field]],
    description: Optional[str] = None,
    owner: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    name: Optional[str] = None,
):
    """
    Declare an On-Demand Feature View

    :param mode: Whether the annotated function is a pipeline function ("pipeline" mode) or a transformation function ("python" or "pandas" mode).
        For the non-pipeline mode, an inferred transformation will also be registered.
    :param sources: The data source inputs to the feature view. An input can be a RequestSource or a materialized Feature View.
    :param schema: Spark schema matching the expected output (of either a dictionary or a Pandas DataFrame).
    :param description: A human readable description.
    :param owner: Owner name (typically the email of the primary maintainer).
    :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
    :param name: Unique, human friendly name that identifies the FeatureView. Defaults to the function name.
    :return: An object of type :class:`tecton.feature_views.OnDemandFeatureView`.

    An example declaration of an on-demand feature view using Python mode.
    With Python mode, the function sources will be dictionaries, and the function is expected to return a dictionary matching the schema from `output_schema`.
    Tecton recommends using Python mode for improved online serving performance.

    .. code-block:: python

        from tecton import RequestSource, on_demand_feature_view
        from tecton.types import Field, Float64, Int64
        from pyspark.sql.types import StructType, LongType
        import pandas

        # Define the request schema
        transaction_request = RequestSource(schema=[Field("amount", Float64)])

        # Define the output schema
        output_schema = [Field("transaction_amount_is_high", Int64)]

        # This On-Demand Feature View evaluates a transaction amount and declares it as "high", if it's higher than 10,000
        @on_demand_feature_view(
            sources=[transaction_request],
            mode='pandas',
            schema=output_schema,
            owner='matt@tecton.ai',
            tags={'release': 'production', 'prevent-destroy': 'true', 'prevent-recreate': 'true'},
            description='Whether the transaction amount is considered high (over $10000)'
        )

        def transaction_amount_is_high(transaction_request):
            result = {}
            result['transaction_amount_is_high'] = int(transaction_request['amount'] >= 10000)
            return result

    An example declaration of an on-demand feature view using Pandas mode.
    With Pandas mode, the function sources will be Pandas Dataframes, and the function is expected to return a Dataframe matching the schema from `output_schema`.

    .. code-block:: python

        from tecton import RequestSource, on_demand_feature_view
        from tecton.types import Field, Float64, Int64
        from pyspark.sql.types import StructType, LongType
        import pandas

        # Define the request schema
        transaction_request = RequestSource(schema=[Field("amount", Float64)])

        # Define the output schema
        output_schema = [Field("transaction_amount_is_high", Int64)]

        # This On-Demand Feature View evaluates a transaction amount and declares it as "high", if it's higher than 10,000
        @on_demand_feature_view(
            sources=[transaction_request],
            mode='pandas',
            schema=output_schema,
            owner='matt@tecton.ai',
            tags={'release': 'production', 'prevent-destroy': 'true', 'prevent-recreate': 'true'},
            description='Whether the transaction amount is considered high (over $10000)'
        )
        def transaction_amount_is_high(transaction_request):
            import pandas as pd

            df = pd.DataFrame()
            df['transaction_amount_is_high'] = (transaction_request['amount'] >= 10000).astype('int64')
            return df
    """

    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            transform = transformation(mode=mode, description=description, owner=owner, tags=tags, name=name)(
                user_function
            )

            def pipeline_function(**kwargs):
                return transform(**kwargs)

        feature_view = OnDemandFeatureView(
            schema=schema,
            transform=transform,
            name=name or user_function.__name__,
            pipeline_function=pipeline_function,
            sources=sources,
            description=description,
            owner=owner,
            tags=tags,
            user_function=user_function,
        )
        functools.update_wrapper(wrapper=feature_view, wrapped=user_function)

        return feature_view

    return decorator


@dataclass
class MaterializedFeatureView(FeatureDefinition):
    """
    Stream/Batch Feature View class to include in Feature Services or to use in unit testing.

    **Do not instantiate this class directly.** Use a decorator-based constructor instead:

    - :class:`tecton.declarative.batch_feature_view`
    - :class:`tecton.declarative.stream_feature_view`

    """

    def __init__(
        self,
        name: str,
        pipeline_function: Callable[..., PipelineNode],
        sources: Sequence[Union[BaseDataSource, FilteredSource]],
        entities: List[BaseEntity],
        online: bool,
        offline: bool,
        offline_store: Union[ParquetConfig, DeltaConfig],
        online_store: Optional[Union[DynamoConfig, RedisConfig]],
        aggregation_interval: Optional[datetime.timedelta],
        aggregations: Optional[List[Aggregation]],
        ttl: Optional[datetime.timedelta],
        feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]],
        batch_schedule: Optional[datetime.timedelta],
        online_serving_index: Optional[List[str]],
        batch_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]],
        stream_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]],
        monitor_freshness: bool,
        expected_feature_freshness: Optional[datetime.timedelta],
        alert_email: Optional[str],
        description: Optional[str],
        owner: Optional[str],
        tags: Optional[Dict[str, str]],
        inferred_transform: Optional[Transformation],
        feature_view_type: FeatureViewType,
        timestamp_field: Optional[str],
        data_source_type: DataSourceType,
        user_function: Callable,
        incremental_backfills: bool,
        aggregation_mode: Optional[AggregationMode] = None,
        max_batch_aggregation_interval: Optional[datetime.timedelta] = None,
        output_stream: Optional[OutputStream] = None,
        batch_trigger: Optional[BatchTriggerType] = None,
    ):
        """
        **Do not directly use this constructor.** Internal constructor for materialized FeatureViews.
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=None, tags=tags)

        fn_params = get_source_input_params(user_function)
        params_to_sources = dict(zip(fn_params, sources))

        args = prepare_common_fv_args(
            basic_info,
            entities,
            pipeline_function,
            params_to_sources,
            fv_type=feature_view_type,
        )
        # we bind to user_function since pipeline_function may be artificially created and just accept **kwargs
        test_binding_user_function(user_function, params_to_sources)

        if online_serving_index:
            args.online_serving_index.extend(online_serving_index)

        monitoring = None
        if monitor_freshness:
            monitoring = MonitoringConfig(monitor_freshness, expected_feature_freshness, alert_email)

        args.online_enabled = online
        args.offline_enabled = offline
        args.materialized_feature_view_args.CopyFrom(
            self._prepare_common_materialization_args(
                args.materialized_feature_view_args,
                timestamp_field,
                feature_start_time,
                batch_trigger,
                batch_schedule,
                offline_store,
                online_store,
                batch_compute,
                stream_compute,
                monitoring,
                data_source_type,
                max_batch_aggregation_interval,
                output_stream,
                incremental_backfills=incremental_backfills,
            )
        )
        if ttl:
            args.materialized_feature_view_args.serving_ttl.FromTimedelta(ttl)

        if aggregations:
            assert (
                aggregation_interval or aggregation_mode == AggregationMode.CONTINUOUS
            ), "`aggregation_interval` or `aggregation_mode=AggregationMode.CONTINUOUS` is required if specifying aggregations"
            assert ttl is None, "`ttl` is automatically set for aggregations to the `aggregation_interval`"
            assert not incremental_backfills, "`incremental_backfills` cannot be used with aggregations"

            if aggregation_mode == AggregationMode.CONTINUOUS:
                args.materialized_feature_view_args.aggregation_interval.FromTimedelta(datetime.timedelta(seconds=0))
            if aggregation_mode == AggregationMode.TIME_INTERVAL:
                args.materialized_feature_view_args.aggregation_interval.FromTimedelta(aggregation_interval)

            args.materialized_feature_view_args.aggregation_mode = aggregation_mode.value
            args.materialized_feature_view_args.aggregations.extend([agg._to_proto() for agg in aggregations])
            args.materialized_feature_view_args.aggregation_mode = aggregation_mode.value
        else:
            assert (
                aggregation_interval is None
            ), "`aggregation_interval` can only be specified when using `aggregations`"
            assert aggregation_mode is None, "`aggregation_mode` can only be specified when using `aggregations`"

            # Default ttl to "infinity" equivalent
            ttl = ttl or datetime.timedelta.max

        self.inferred_transform = inferred_transform
        self._args = args
        self.pipeline_function = pipeline_function
        self.sources = sources

        Fco._register(self)

    def _prepare_common_materialization_args(
        self,
        args: MaterializedFeatureViewArgs,
        timestamp_field: Optional[str],
        feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]],
        batch_trigger: Optional[BatchTriggerType],
        batch_schedule: Optional[datetime.timedelta],
        offline_store: Union[ParquetConfig, DeltaConfig],
        online_store: Optional[Union[DynamoConfig, RedisConfig]],
        batch_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]],
        stream_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]],
        monitoring: Optional[MonitoringConfig],
        data_source_type: DataSourceType,
        max_batch_aggregation_interval: Optional[datetime.timedelta],
        output_stream: Optional[OutputStream],
        incremental_backfills: bool,
    ) -> MaterializedFeatureViewArgs:
        if timestamp_field:
            args.timestamp_field = timestamp_field

        if feature_start_time:
            args.feature_start_time.FromDatetime(feature_start_time)
        if batch_schedule:
            args.batch_schedule.FromTimedelta(batch_schedule)
        args.offline_store.CopyFrom(offline_store._to_proto())
        if online_store:
            args.online_store.CopyFrom(online_store._to_proto())
        if batch_compute:
            cluster_config = batch_compute._to_cluster_proto()
            args.batch_compute.CopyFrom(cluster_config)
        if stream_compute:
            cluster_config = stream_compute._to_cluster_proto()
            args.stream_compute.CopyFrom(cluster_config)

        if max_batch_aggregation_interval:
            args.max_batch_aggregation_interval.FromTimedelta(max_batch_aggregation_interval)

        if monitoring:
            args.monitoring.CopyFrom(monitoring._to_proto())
        if data_source_type:
            args.data_source_type = data_source_type

        args.incremental_backfills = incremental_backfills

        args.batch_trigger = batch_trigger.value

        if output_stream:
            args.output_stream.CopyFrom(output_stream._to_proto())
        return args

    def __hash__(self):
        return self.name.__hash__()

    def run(
        self,
        spark: SparkSession,
        start_time: Optional[datetime.datetime],
        end_time: Optional[datetime.datetime],
        aggregation_level: Optional[str] = None,
        **mock_sources: DataFrame,
    ):
        """
        Run the FeatureView using mock data sources. This requires a local spark session.

        :param start_time: The start time of the time window to materialize. If not set, defaults to `end_time` minus `batch_schedule`.

        :param end_time: The end time of the time window to materialize. If not set, defaults to `start_time` plus `batch_schedule`

        :param aggregation_level: For feature views with aggregations, `aggregation_level` configures what stage of the aggregation to run up to.

            The query for Aggregate Feature Views operates in three logical steps:

                1) The feature view query is run over the provided time range. The user defined transformations are applied over the data source.

                2) The result of #1 is aggregated into tiles the size of the aggregation_interval.

                3) The tiles from #2 are combined to form the final feature values. The number of tiles that are combined is based off of the time_window of the aggregation.

            For testing and debugging purposes, to see the output of #1, use ``aggregation_level="disabled"``. For #2, use ``aggregation_level="partial"``. For #3, use ``aggregation_level="full"``.

            ``aggregation_level="full"`` is the default behavior.

        :param \*\*mock_sources: kwargs with expected same keys as the FeatureView's inputs parameter. Each input name
            maps to a Spark DataFrame that should be evaluated for that node in the pipeline.

        Example:

        .. code-block:: python

            from datetime import datetime, timedelta
            import pandas
            from fraud.features.batch_features.user_credit_card_issuer import user_credit_card_issuer


            # The `tecton_pytest_spark_session` is a PyTest fixture that provides a
            # Tecton-defined PySpark session for testing Spark transformations and feature
            # views.
            def test_user_distinct_merchant_transaction_count_30d(tecton_pytest_spark_session):
                input_pandas_df = pandas.DataFrame({
                    "user_id": ["user_1", "user_2", "user_3", "user_4"],
                    "signup_timestamp": [datetime(2022, 5, 1)] * 4,
                    "cc_num": [1000000000000000, 4000000000000000, 5000000000000000, 6000000000000000],
                })
                input_spark_df = tecton_pytest_spark_session.createDataFrame(input_pandas_df)

                # Simulate materializing features for May 1st.
                output = user_credit_card_issuer.run(
                    spark=tecton_pytest_spark_session,
                    start_time=datetime(2022, 5, 1),
                    end_time=datetime(2022, 5, 2),
                    fraud_users_batch=input_spark_df)

                actual = output.toPandas()

                expected = pandas.DataFrame({
                    "user_id": ["user_1", "user_2", "user_3", "user_4"],
                    "signup_timestamp":  [datetime(2022, 5, 1)] * 4,
                    "credit_card_issuer": ["other", "Visa", "MasterCard", "Discover"],
                })

                pandas.testing.assert_frame_equal(actual, expected)


        :return: A :class:`tecton.DataFrame` object.
        """
        return declarative_run(self._args, spark, start_time, end_time, aggregation_level, mock_sources)


@typechecked
def stream_feature_view(
    *,
    mode: str,
    source: Union[StreamSource, FilteredSource],
    entities: List[BaseEntity],
    aggregation_interval: Optional[datetime.timedelta] = None,
    aggregation_mode: Optional[AggregationMode] = None,
    aggregations: List[Aggregation] = [],
    online: Optional[bool] = False,
    offline: Optional[bool] = False,
    ttl: Optional[datetime.timedelta] = None,
    feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]] = None,
    batch_trigger: BatchTriggerType = BatchTriggerType.SCHEDULED,
    batch_schedule: Optional[datetime.timedelta] = None,
    online_serving_index: Optional[List[str]] = None,
    batch_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    stream_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    offline_store: Optional[Union[ParquetConfig, DeltaConfig]] = ParquetConfig(),
    online_store: Optional[Union[DynamoConfig, RedisConfig]] = None,
    monitor_freshness: bool = False,
    expected_feature_freshness: Optional[datetime.timedelta] = None,
    alert_email: Optional[str] = None,
    description: Optional[str] = None,
    owner: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    timestamp_field: Optional[str] = None,
    name: Optional[str] = None,
    max_batch_aggregation_interval: Optional[datetime.timedelta] = None,
    output_stream: Optional[OutputStream] = None,
):
    """
    Declare a Stream Feature View.

    :param mode: Whether the annotated function is a pipeline function ("pipeline" mode) or a transformation function ("spark_sql" or "pyspark" mode).
        For the non-pipeline mode, an inferred transformation will also be registered.
    :param source: The data source input to the feature view.
    :param entities: The entities this feature view is associated with.
    :param aggregation_interval: How frequently the feature value is updated (for example, `"1h"` or `"6h"`)
    :param aggregation_mode: Whether aggregations should be "batched" in time intervals or be updated continuously.
        Continuously aggregated features are fresher but more expensive. One of `AggregationMode.TIME_INTERVAL` or
        `AggregationMode.CONTINUOUS`. Defaults to `AggregationMode.TIME_INTERVAL`.
    :param aggregations: A list of :class:`Aggregation` structs
    :param online: Whether the feature view should be materialized to the online feature store. (Default: False)
    :param offline: Whether the feature view should be materialized to the offline feature store. (Default: False)
    :param ttl: The TTL (or "look back window") for features defined by this feature view. This parameter determines how long features will live in the online store and how far to  "look back" relative to a training example's timestamp when generating offline training sets. Shorter TTLs improve performance and reduce costs.
    :param feature_start_time: When materialization for this feature view should start from. (Required if offline=true)
    :param batch_trigger: manual vs scheduled batch materialization trigger
    :param batch_schedule: The interval at which batch materialization should be scheduled.
    :param online_serving_index: (Advanced) Defines the set of join keys that will be indexed and queryable during online serving.
    :param batch_compute: Batch materialization cluster configuration.
    :param stream_compute: Streaming materialization cluster configuration.
    :param offline_store: Configuration for how data is written to the offline feature store.
    :param online_store: Configuration for how data is written to the online feature store.
    :param monitor_freshness: If true, enables monitoring when feature data is materialized to the online feature store.
    :param expected_feature_freshness: Threshold used to determine if recently materialized feature data is stale. Data is stale if ``now - most_recent_feature_value_timestamp > expected_feature_freshness``. For feature views using Tecton aggregations, data is stale if ``now - round_up_to_aggregation_interval(most_recent_feature_value_timestamp) > expected_feature_freshness``. Where ``round_up_to_aggregation_interval()`` rounds up the feature timestamp to the end of the ``aggregation_interval``. Value must be at least 2 times ``aggregation_interval``. If not specified, a value determined by the Tecton backend is used.
    :param alert_email: Email that alerts for this FeatureView will be sent to.
    :param description: A human readable description.
    :param owner: Owner name (typically the email of the primary maintainer).
    :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
    :param timestamp_field: The column name that refers to the timestamp for records that are produced by the feature view. (Default: will infer if one column is a Timestamp type.)
    :param name: Unique, human friendly name that identifies the FeatureView. Defaults to the function name.
    :param max_batch_aggregation_interval: (Advanced) makes batch job scheduler group jobs together for efficiency.
    :return: An object of type :class:`tecton.declarative.feature_view.MaterializedFeatureView`.

    Example `StreamFeatureView` declaration:

    .. code-block:: python

        from datetime import datetime, timedelta
        from entities import user
        from transactions_stream import transactions_stream
        from tecton import Aggregation, FilteredSource, stream_feature_view

        @stream_feature_view(
            source=FilteredSource(transactions_stream),
            entities=[user],
            mode="spark_sql",
            ttl=timedelta(days=30),
            online=True,
            offline=True,
            batch_schedule=timedelta(days=1),
            feature_start_time=datetime(2020, 10, 10),
            tags={"release": "production"},
            owner="kevin@tecton.ai",
            description="Features about the users most recent transaction in the past 60 days. Updated continuously.",
        )
        def user_last_transaction_features(transactions_stream):
            return f'''
                SELECT
                    USER_ID,
                    TIMESTAMP,
                    AMOUNT as LAST_TRANSACTION_AMOUNT,
                    CATEGORY as LAST_TRANSACTION_CATEGORY
                FROM
                    {transactions_stream}
                '''

    Example `StreamFeatureView` declaration using aggregates:

    .. code-block:: python

        from datetime import datetime, timedelta
        from entities import user
        from transactions_stream import transactions_stream
        from tecton import Aggregation, FilteredSource, stream_feature_view

        @stream_feature_view(
            source=FilteredSource(transactions_stream),
            entities=[user],
            mode="spark_sql",
            aggregation_interval=timedelta(minutes=10),
            aggregations=[
                Aggregation(column="AMOUNT", function="mean", time_window=timedelta(hours=1)),
                Aggregation(column="AMOUNT", function="mean", time_window=timedelta(hours=24)),
                Aggregation(column="AMOUNT", function="mean", time_window=timedelta(hours=72)),
                Aggregation(column="AMOUNT", function="sum", time_window=timedelta(hours=1)),
                Aggregation(column="AMOUNT", function="sum", time_window=timedelta(hours=24)),
                Aggregation(column="AMOUNT", function="sum", time_window=timedelta(hours=72)),
            ],
            online=True,
            feature_start_time=datetime(2020, 10, 10),
            tags={"release": "production"},
            owner="kevin@tecton.ai",
            description="Transaction amount statistics and total over a series of time windows, updated every ten minutes.",
        )
        def user_recent_transaction_aggregate_features(transactions_stream):
            return f'''
                SELECT
                    USER_ID,
                    AMOUNT,
                    TIMESTAMP
                FROM
                    {transactions_stream}
                '''
    """

    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            inferred_transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            # We infer owner/family/tags but not a description.
            inferred_transform = transformation(mode, name, description, owner, tags=tags)(user_function)

            def pipeline_function(**kwargs):
                return inferred_transform(**kwargs)

        _aggregation_mode = aggregation_mode or AggregationMode.TIME_INTERVAL if aggregations else None

        featureView = MaterializedFeatureView(
            feature_view_type=FeatureViewType.FEATURE_VIEW_TYPE_FWV5_FEATURE_VIEW,
            name=name or user_function.__name__,
            pipeline_function=pipeline_function,
            inferred_transform=inferred_transform,
            sources=[source],
            entities=entities,
            online=online,
            offline=offline,
            offline_store=offline_store,
            online_store=online_store,
            aggregation_interval=aggregation_interval,
            aggregation_mode=_aggregation_mode,
            aggregations=aggregations,
            ttl=ttl,
            feature_start_time=feature_start_time,
            batch_trigger=batch_trigger,
            batch_schedule=batch_schedule,
            online_serving_index=online_serving_index,
            batch_compute=batch_compute,
            stream_compute=stream_compute,
            monitor_freshness=monitor_freshness,
            expected_feature_freshness=expected_feature_freshness,
            alert_email=alert_email,
            description=description,
            owner=owner,
            tags=tags,
            timestamp_field=timestamp_field,
            data_source_type=DataSourceType.STREAM_WITH_BATCH,
            user_function=user_function,
            max_batch_aggregation_interval=max_batch_aggregation_interval,
            output_stream=output_stream,
            incremental_backfills=False,
        )
        functools.update_wrapper(featureView, user_function)

        return featureView

    return decorator


@typechecked
def batch_feature_view(
    *,
    mode: str,
    sources: Sequence[Union[BatchSource, FilteredSource]],
    entities: List[BaseEntity],
    aggregation_interval: Optional[datetime.timedelta] = None,
    aggregations: List[Aggregation] = [],
    online: Optional[bool] = False,
    offline: Optional[bool] = False,
    ttl: Optional[datetime.timedelta] = None,
    feature_start_time: Optional[Union[pendulum.DateTime, datetime.datetime]] = None,
    batch_trigger: BatchTriggerType = BatchTriggerType.SCHEDULED,
    batch_schedule: Optional[datetime.timedelta] = None,
    online_serving_index: Optional[List[str]] = None,
    batch_compute: Optional[Union[ExistingClusterConfig, DatabricksClusterConfig, EMRClusterConfig]] = None,
    offline_store: Optional[Union[ParquetConfig, DeltaConfig]] = ParquetConfig(),
    online_store: Optional[Union[DynamoConfig, RedisConfig]] = None,
    monitor_freshness: bool = False,
    expected_feature_freshness: Optional[datetime.timedelta] = None,
    alert_email: Optional[str] = None,
    description: Optional[str] = None,
    owner: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    timestamp_field: Optional[str] = None,
    name: Optional[str] = None,
    max_batch_aggregation_interval: Optional[datetime.timedelta] = None,
    incremental_backfills: bool = False,
):
    """
    Declare a Batch Feature View.

    :param mode: Whether the annotated function is a pipeline function ("pipeline" mode) or a transformation function ("spark_sql" or "pyspark" mode).
        For the non-pipeline mode, an inferred transformation will also be registered.
    :param sources: The data source inputs to the feature view.
    :param entities: The entities this feature view is associated with.
    :param aggregation_interval: How frequently the feature value is updated (for example, `"1h"` or `"6h"`)
    :param aggregations: A list of :class:`Aggregation` structs.
    :param online: Whether the feature view should be materialized to the online feature store. (Default: False)
    :param offline: Whether the feature view should be materialized to the offline feature store. (Default: False)
    :param ttl: The TTL (or "look back window") for features defined by this feature view. This parameter determines how long features will live in the online store and how far to  "look back" relative to a training example's timestamp when generating offline training sets. Shorter TTLs improve performance and reduce costs.
    :param feature_start_time: When materialization for this feature view should start from. (Required if offline=true)
    :param batch_schedule: The interval at which batch materialization should be scheduled.
    :param online_serving_index: (Advanced) Defines the set of join keys that will be indexed and queryable during online serving.
    :param batch_trigger: manual vs scheduled batch materialization trigger
    :param batch_compute: Batch materialization cluster configuration.
    :param offline_store: Configuration for how data is written to the offline feature store.
    :param online_store: Configuration for how data is written to the online feature store.
    :param monitor_freshness: If true, enables monitoring when feature data is materialized to the online feature store.
    :param expected_feature_freshness: Threshold used to determine if recently materialized feature data is stale. Data is stale if ``now - most_recent_feature_value_timestamp > expected_feature_freshness``. For feature views using Tecton aggregations, data is stale if ``now - round_up_to_aggregation_interval(most_recent_feature_value_timestamp) > expected_feature_freshness``. Where ``round_up_to_aggregation_interval()`` rounds up the feature timestamp to the end of the ``aggregation_interval``. Value must be at least 2 times ``aggregation_interval``. If not specified, a value determined by the Tecton backend is used.
    :param alert_email: Email that alerts for this FeatureView will be sent to.
    :param description: A human readable description.
    :param owner: Owner name (typically the email of the primary maintainer).
    :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
    :param timestamp_field: The column name that refers to the timestamp for records that are produced by the feature view. (Default: will infer if one column is a Timestamp type.)
    :param name: Unique, human friendly name that identifies the FeatureView. Defaults to the function name.
    :param max_batch_aggregation_interval: (Advanced) makes batch job scheduler group jobs together for efficiency.
    :param incremental_backfills: If set to `True`, the feature view will be backfilled one interval at a time as
        if it had been updated "incrementally" since its feature_start_time. For example, if `batch_interval` is 1 day
        and `feature_start_time` is 1 year prior to the current time, then the backfill will run 365 separate
        materialization jobs to fill the historical feature data.
    :return: An object of type :class:`tecton.declarative.feature_view.MaterializedFeatureView`.

    Example BatchFeatureView declaration:

    .. code-block:: python

        from datetime import datetime
        from datetime import timedelta

        from fraud.entities import user
        from fraud.data_sources.credit_scores_batch import credit_scores_batch

        from tecton import batch_feature_view, Aggregation, FilteredSource

        @batch_feature_view(
            sources=[FilteredSource(credit_scores_batch)],
            entities=[user],
            mode='spark_sql',
            online=True,
            offline=True,
            feature_start_time=datetime(2020, 10, 10),
            batch_schedule=timedelta(days=1),
            ttl=timedelta(days=60),
            description="Features about the users most recent transaction in the past 60 days. Updated daily.",
            )

        def user_last_transaction_features(credit_scores_batch):
            return f'''
                SELECT
                    USER_ID,
                    TIMESTAMP,
                    AMOUNT as LAST_TRANSACTION_AMOUNT,
                    CATEGORY as LAST_TRANSACTION_CATEGORY
                FROM
                    {credit_scores_batch}
            '''

    Example BatchFeatureView declaration using aggregates:

    .. code-block:: python

        from datetime import datetime
        from datetime import timedelta

        from fraud.entities import user
        from fraud.data_sources.credit_scores_batch import credit_scores_batch

        from tecton import batch_feature_view, Aggregation, FilteredSource

        @batch_feature_view(
            sources=[FilteredSource(credit_scores_batch)],
            entities=[user],
            mode='spark_sql',
            online=True,
            offline=True,
            feature_start_time=datetime(2020, 10, 10),
            aggregations=[
                Aggregation(column="amount", function="mean", time_window=timedelta(days=1)),
                Aggregation(column="amount", function="mean", time_window=timedelta(days=30)),
            ],
            aggregation_interval=timedelta(days=1),
            description="Transaction amount statistics and total over a series of time windows, updated daily.",
            )

        def user_recent_transaction_aggregate_features(credit_scores_batch):
            return f'''
                SELECT
                    USER_ID,
                    AMOUNT,
                    TIMESTAMP
                FROM
                    {credit_scores_batch}
            '''
    """

    def decorator(user_function):
        if mode == PIPELINE_MODE:
            pipeline_function = user_function
            inferred_transform = None
        else:
            # Separate out the Transformation and manually construct a simple pipeline function.
            # We infer owner/family/tags but not a description.
            inferred_transform = transformation(mode, name, description, owner, tags=tags)(user_function)

            def pipeline_function(**kwargs):
                return inferred_transform(**kwargs)

        aggregation_mode = AggregationMode.TIME_INTERVAL if aggregations else None

        featureView = MaterializedFeatureView(
            feature_view_type=FeatureViewType.FEATURE_VIEW_TYPE_FWV5_FEATURE_VIEW,
            name=name or user_function.__name__,
            pipeline_function=pipeline_function,
            inferred_transform=inferred_transform,
            sources=sources,
            entities=entities,
            online=online,
            offline=offline,
            offline_store=offline_store,
            online_store=online_store,
            aggregation_interval=aggregation_interval,
            aggregation_mode=aggregation_mode,
            aggregations=aggregations,
            ttl=ttl,
            feature_start_time=feature_start_time,
            batch_trigger=batch_trigger,
            batch_schedule=batch_schedule,
            online_serving_index=online_serving_index,
            batch_compute=batch_compute,
            stream_compute=None,
            monitor_freshness=monitor_freshness,
            expected_feature_freshness=expected_feature_freshness,
            alert_email=alert_email,
            description=description,
            owner=owner,
            tags=tags,
            timestamp_field=timestamp_field,
            data_source_type=DataSourceType.BATCH,
            user_function=user_function,
            max_batch_aggregation_interval=max_batch_aggregation_interval,
            output_stream=None,
            incremental_backfills=incremental_backfills,
        )
        functools.update_wrapper(featureView, user_function)

        return featureView

    return decorator
