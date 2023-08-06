from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pendulum

from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper
from tecton_core.query.node_interface import get_new_id
from tecton_core.query.node_interface import global_map
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.node_interface import QueryNode
from tecton_proto.args.pipeline_pb2 import DataSourceNode
from tecton_proto.data.feature_view_pb2 import MaterializationTimeRangePolicy
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource


class OdfvPipelineNode(QueryNode):
    """
    Evaluates an odfv pipeline on top of an input containing columns prefixed '_udf_internal' to be used as dependent feature view inputs. The _udf_internal contract is
    documented in pipeline_helper.py
    The input may also have other feature values. This ensures we can match multiple odfv features to the right rows based on request context without joining them.
    In order to make this possible, a namespace is also passed through at this point to ensure the odfv features do not conflict with other features.
    """

    def __init__(self, input_node: NodeRef, feature_definition_wrapper: FeatureDefinitionWrapper, namespace: str):
        self.feature_definition_wrapper = feature_definition_wrapper
        self.input_node = input_node
        self.namespace = namespace

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return (self.input_node,)

    def as_str(self, verbose: bool):
        return f"Evaluate OnDemand Pipeline: {self.feature_definition_wrapper.name}\n"


class FeatureViewPipelineNode(QueryNode):
    def __init__(
        self,
        inputs_map: Dict[str, NodeRef],
        feature_definition_wrapper: FeatureDefinitionWrapper,
        feature_time_limits: Optional[pendulum.Period],
    ):
        self.feature_definition_wrapper = feature_definition_wrapper
        self.inputs_map = inputs_map
        # Needed for correct behavior by tecton_sliding_window udf if it exists in the pipeline
        self.feature_time_limits = feature_time_limits
        # Note: elsewhere we set this to pendulum.Duration(seconds=fv_proto.materialization_params.schedule_interval.ToSeconds())
        # but that seemed wrong for bwafv
        self.schedule_interval = feature_definition_wrapper.batch_materialization_schedule

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return tuple(self.inputs_map.values())

    def as_str(self, verbose: bool):
        return f"Evaluate Pipeline: {self.feature_definition_wrapper.name}\n"

    # overwrite pretty_print because we have named inputs
    def pretty_print(self, verbose: bool = False, indents=0, show_ids=True) -> str:
        # TODO: remove this copypasta
        if show_ids:
            new_id = get_new_id()
            global_map[new_id] = self
            s = f"<{new_id}>"
        else:
            s = ""
        s += "  " * indents + self.as_str(verbose)
        for k in self.inputs_map:
            s += "  " * (indents) + f"- PipelineInput: {k}\n"
            s += self.inputs_map[k].pretty_print(verbose, indents + 1, show_ids)
        return s


class DataSourceScanNode(QueryNode):
    """
    DataSource + Filter
    We don't have a separate filter node to hide away the filter/partition interaction with raw_batch_translator
    """

    def __init__(
        self,
        ds: VirtualDataSource,
        ds_node: DataSourceNode,
        is_stream: bool,
        raw_data_time_filter: Optional[pendulum.Period] = None,
    ):
        self.ds = ds
        self.ds_node = ds_node
        self.time_filter = raw_data_time_filter
        self.is_stream = is_stream

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return tuple()

    def with_raw_data_time_filter(self, raw_data_time_filter: pendulum.Period) -> QueryNode:
        """Returns a new node with the raw data time filter applied."""
        assert not self.is_stream, "Raw data filtering cannot be run on a stream source"
        return DataSourceScanNode(self.ds, self.ds_node, self.is_stream, raw_data_time_filter)

    def as_str(self, verbose: bool):
        s = ""
        if self.time_filter is not None:
            s += f"TimeFilter: {self.time_filter}\n"
        verb = "Read Stream" if self.is_stream else "Scan DataSource"
        s += f"{verb}: {self.ds.fco_metadata.name}\n"
        return s


class OfflineStoreScanNode(QueryNode):
    """
    Fetch values from offline store
    """

    def __init__(
        self,
        feature_definition_wrapper: FeatureDefinitionWrapper,
        feature_time_filter: Optional[pendulum.Period] = None,
    ):
        self.feature_definition_wrapper = feature_definition_wrapper
        self.time_filter = feature_time_filter

    def as_str(self, verbose: bool):
        s = ""
        if self.time_filter is not None:
            s += f"TimeFilter: {self.time_filter}\n"
        s += f"Scan OfflineStore: {self.feature_definition_wrapper.name}"
        return s

    def with_time_filter(self, feature_time_filter: pendulum.Period):
        return OfflineStoreScanNode(self.feature_definition_wrapper, feature_time_filter)

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return tuple()


class JoinNode(QueryNode):
    """
    A basic left join on 2 inputs
    """

    def __init__(self, left: NodeRef, right: NodeRef, join_cols: List[str], how: str):
        self.left = left
        self.right = right
        self.join_cols = join_cols
        self.how = how

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return (self.left, self.right)

    def as_str(self, verbose: bool):
        # TODO: this is gonna look ugly
        return f"{self.how} Join" + (f" on {self.join_cols}:" if verbose else ":")


class AsofJoinNode(QueryNode):
    """
    A "basic" asof join on 2 inputs
    """

    def __init__(self, left: NodeRef, right: NodeRef, join_cols: List[str], timestamp_field: str, right_prefix: str):
        self.left = left
        self.right = right
        self.join_cols = join_cols
        self.timestamp_field = timestamp_field
        self.right_prefix = right_prefix

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return (self.left, self.right)

    def as_str(self, verbose: bool):
        # TODO: this is gonna look ugly
        return "Asof Join:"


class FullAggNode(QueryNode):
    """
    Performs full aggregations for each of the aggregates in fdw.trailing_time_window_aggregation.
    The full aggregations are applied for all the join keys in spine; otherwise new aggregations changed via
    expiring windows will not be generated.

    The resulting dataframe with contain all join keys in the spine.
    """

    def __init__(
        self,
        input_node: NodeRef,
        fdw: FeatureDefinitionWrapper,
        spine: Optional[Any],
        spine_time_field: Optional[str],
        spine_join_keys: List[Tuple[str]],
    ):
        assert fdw.is_temporal_aggregate
        self.input_node = input_node
        self.fdw = fdw
        self.spine = spine
        self.spine_time_field = spine_time_field
        self.spine_join_keys = spine_join_keys

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return (self.input_node,)

    def as_str(self, verbose: bool):
        if verbose:
            return (
                "FullAggNode: Set any feature values for rows with time < feature_start_time to null\n"
                + "Use window function to perform full aggregations; window range = agg.time_range range preceding -> current row\n"
                + "right-join against spine, with _anchor_time = aligned_spine_timestamp - 1 window, because raw data in a given time will only be accessible for retrieval by the end of the window. We also do some stuff to account for upstream_lateness, but we don't do anything to account for differences in slide_window and batch_schedule. And also this kind of assumes materialization happens instantaneously."
                if self.spine
                else ""
            )
        else:
            return "Perform Full Aggregates"


class PartialAggNode(QueryNode):
    """
    Performs partial aggregations for each of the aggregates in fdw.trailing_time_window_aggregation
    """

    def __init__(self, input_node: NodeRef, fdw: FeatureDefinitionWrapper):
        self.input_node = input_node
        self.fdw = fdw

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return (self.input_node,)

    def as_str(self, verbose: bool):
        if verbose:
            return (
                'Add column "_anchor_time" as the start of aggregation window\n'
                + "Perform partial-aggregate group by aggregation window\n"
                + "Align timestamp_key to aggregation_slide_period to create aggregation window"
            )
        else:
            return "Perform Partial Aggregates"


class SetAnchorTimeNode(QueryNode):
    """
    Augment a dataframe with an anchor time based on batch schedule (BFV) or slide window (WAFV)
    """

    def __init__(
        self,
        input_node: NodeRef,
        offline: bool,
        feature_store_format_version: int,
        batch_schedule_in_feature_store_specific_version_units: int,
        timestamp_field: str,
        retrieval: bool,
    ):
        self.input_node = input_node
        self.offline = offline
        self.feature_store_format_version = feature_store_format_version
        self.batch_schedule_in_feature_store_specific_version_units = (
            batch_schedule_in_feature_store_specific_version_units
        )
        self.timestamp_field = timestamp_field
        self.for_retrieval = retrieval

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return (self.input_node,)

    def as_str(self, verbose: bool):
        if not verbose:
            return ""
        if self.for_retrieval:
            return "Add anchor time column _anchor_time: timestamp_col-timestamp_col%batch_schedule - batch_schedule, because if you're querying at t, you would only see the data for the previous window"
        elif self.offline:
            return "Add anchor time column _anchor_time: timestamp_col-timestamp_col%batch_schedule"
        else:
            return "Add raw data end time column _materialized_raw_data_end_time: timestamp_col-timestamp_col%batch_schedule + batch_schedule. We assume feature_end_time==raw_data_end_time"


class RenameColsNode(QueryNode):
    """
    Rename some columns. Maybe you want to join on the columns.
    """

    def __init__(self, input_node: NodeRef, mapping: Dict[str, str]):
        self.input_node = input_node
        self.mapping = mapping

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return (self.input_node,)

    def as_str(self, verbose: bool):
        return f"Rename {self.mapping}"


class DataNode(QueryNode):
    """
    Currently used for testing, but could be used for run_api(mock_inputs). The executor node will need to typecheck and know how to handle the type of mock data.
    """

    data: Any

    def __init__(self, data: Any):
        self.data = data

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return tuple()

    def as_str(self, verbose: bool):
        if verbose:
            return f"User-provided Data: type:{self.data.__class__}"
        else:
            return "User-provided Data"


class RespectFSTNode(QueryNode):
    """
    Null out all features outside of feature start time
    """

    def __init__(
        self,
        input_node: NodeRef,
        retrieval_time_col: str,
        feature_start_time: pendulum.datetime,
        features: List[str],
    ):
        self.input_node = input_node
        self.retrieval_time_col = retrieval_time_col
        self.feature_start_time = feature_start_time
        self.features = features

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return (self.input_node,)

    def as_str(self, verbose: bool):
        return f"Null out any values based on a FeatureStartTime of {self.feature_start_time}"


class RespectTTLNode(QueryNode):
    """
    Null out all features outside of ttl
    """

    def __init__(
        self,
        input_node: NodeRef,
        retrieval_time_col: str,
        source_time_col: str,
        ttl: pendulum.Period,
        features: List[str],
    ):
        self.input_node = input_node
        self.retrieval_time_col = retrieval_time_col
        self.source_time_col = source_time_col
        self.ttl = ttl
        self.features = features

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return (self.input_node,)

    def as_str(self, verbose: bool):
        return f"Null out any values based on a TTL of {self.ttl}"


class CustomFilterNode(QueryNode):
    def __init__(self, input_node: NodeRef, filter_str: str):
        self.input_node = input_node
        self.filter_str = filter_str

    def as_str(self, verbose: bool):
        return f"Apply filter: ({self.filter_str})"

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return (self.input_node,)


class FeatureTimeFilterNode(QueryNode):
    """
    Ensure the data being written by a materialization job to offline/online store only contains
    feature timestamps in the feature_data_time_limits range.
    """

    def __init__(
        self,
        input_node: NodeRef,
        feature_data_time_limits: pendulum.Period,
        policy: MaterializationTimeRangePolicy,
        timestamp_field: str,
    ):
        self.input_node = input_node
        self.time_filter = feature_data_time_limits
        self.policy = policy
        self.timestamp_field = timestamp_field

    @property
    def inputs(self) -> Tuple[NodeRef]:
        return (self.input_node,)

    def as_str(self, verbose: bool):
        if self.policy == MaterializationTimeRangePolicy.MATERIALIZATION_TIME_RANGE_POLICY_FAIL_IF_OUT_OF_RANGE:
            policy_str = "Assert time in range:"
        else:
            policy_str = "Apply:"
        return f"{policy_str} TimeFilter: {self.time_filter}"
