import pendulum

from tecton._internals.data_frame_helper import _get_time_limits_of_dataframe
from tecton._internals.feature_views import aggregations
from tecton_core import conf
from tecton_core.pipeline_common import get_time_window_from_data_source_node
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.nodes import FeatureTimeFilterNode
from tecton_core.query.nodes import FeatureViewPipelineNode
from tecton_core.query.nodes import FullAggNode
from tecton_core.query.nodes import OfflineStoreScanNode
from tecton_core.query.nodes import PartialAggNode
from tecton_core.query.nodes import RenameColsNode
from tecton_core.query.nodes import RespectFSTNode
from tecton_core.query.nodes import SetAnchorTimeNode
from tecton_core.query.rewrite import Rewrite


# TODO: genericize this so it can be applied to non-spark. Right now we depend on directly being able to read dataframe from spark to get time limits.


class AggSpineTimePushdown(Rewrite):
    def rewrite(self, tree: NodeRef):
        if isinstance(tree.node, FullAggNode):
            self.rewrite_agg(tree)
        else:
            for i in tree.inputs:
                self.rewrite(i)

    # Compute the time limits from the node, and push down the time limits to its input
    def rewrite_agg(self, tree: "NodeRef[FullAggNode]"):
        node = tree.node
        spine = node.spine

        spine_time_limits = _get_time_limits_of_dataframe(spine, node.spine_time_field)
        self.pushdown_time_range(node.input_node, spine_time_limits)

    # Push down and convert spine time filter to either raw data or feature time filter at the DataSourceScanNode or OfflineStoreScanNode.
    # Nodes that do not affect the correlation with the spine time range are enumerated in the can_be_pushed_down list.
    def pushdown_time_range(self, tree: NodeRef, spine_time_limits: pendulum.Period):
        node = tree.node
        can_be_pushed_down = (RespectFSTNode, RenameColsNode, PartialAggNode, FeatureTimeFilterNode, SetAnchorTimeNode)
        if isinstance(node, can_be_pushed_down):
            self.pushdown_time_range(node.input_node, spine_time_limits)
        elif isinstance(node, OfflineStoreScanNode) or isinstance(node, FeatureViewPipelineNode):
            # NB: don't use aggregations._get_feature_time_limits; it does not account for aggregation windows.
            feature_time_limits = aggregations._get_time_limits(
                fd=node.feature_definition_wrapper, spine_df=None, spine_time_limits=spine_time_limits
            )
            if isinstance(node, FeatureViewPipelineNode):
                for n in node.inputs:
                    if isinstance(n.node, DataSourceScanNode):
                        # this method will convert aligned_feature_time_limits to raw data time limits by accounting for FilteredSource offsets etc.
                        data_time_filter = get_time_window_from_data_source_node(
                            feature_time_limits,
                            node.feature_definition_wrapper.batch_materialization_schedule,
                            n.node.ds_node,
                        )
                        if data_time_filter is not None:
                            n.node = n.node.with_raw_data_time_filter(
                                data_time_filter,
                            )
            elif isinstance(node, OfflineStoreScanNode):
                tree.node = node.with_time_filter(feature_time_limits)


# Mutates the input
def rewrite_tree_for_spine(tree: NodeRef):
    if not conf.get_bool("QUERY_REWRITE_ENABLED"):
        return
    rewrites = [AggSpineTimePushdown()]
    for rewrite in rewrites:
        rewrite.rewrite(tree)
