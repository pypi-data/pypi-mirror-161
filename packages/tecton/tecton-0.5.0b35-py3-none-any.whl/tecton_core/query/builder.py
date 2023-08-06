from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pendulum

from tecton_core import errors
from tecton_core import time_utils
from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper
from tecton_core.feature_definition_wrapper import pipeline_to_ds_inputs
from tecton_core.feature_set_config import FeatureDefinitionAndJoinConfig
from tecton_core.feature_set_config import FeatureSetConfig
from tecton_core.id_helper import IdHelper
from tecton_core.pipeline_common import find_dependent_feature_set_items
from tecton_core.pipeline_common import get_time_window_from_data_source_node
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.nodes import AsofJoinNode
from tecton_core.query.nodes import DataNode
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.nodes import FeatureTimeFilterNode
from tecton_core.query.nodes import FeatureViewPipelineNode
from tecton_core.query.nodes import FullAggNode
from tecton_core.query.nodes import JoinNode
from tecton_core.query.nodes import OdfvPipelineNode
from tecton_core.query.nodes import OfflineStoreScanNode
from tecton_core.query.nodes import PartialAggNode
from tecton_core.query.nodes import RenameColsNode
from tecton_core.query.nodes import RespectFSTNode
from tecton_core.query.nodes import RespectTTLNode
from tecton_core.query.nodes import SetAnchorTimeNode

ANCHOR_TIME = "_anchor_time"


def build_datasource_input_querynodes(
    fdw: FeatureDefinitionWrapper, for_stream: bool, feature_data_time_limits: Optional[pendulum.Period] = None
) -> Dict[str, NodeRef]:
    """
    Starting in FWV5, data sources of FVs with incremental backfills may contain transformations that are only
    correct if the data has been filtered to a specific range.
    """
    schedule_interval = fdw.get_tile_interval if fdw.is_temporal else None
    ds_inputs = pipeline_to_ds_inputs(fdw.pipeline)
    return {
        input_name: DataSourceScanNode.ref(
            fdw.fco_container.get_by_id(IdHelper.to_string(node.virtual_data_source_id)),
            node,
            for_stream,
            get_time_window_from_data_source_node(feature_data_time_limits, schedule_interval, node),
        )
        for input_name, node in ds_inputs.items()
    }


# build QueryTree that executes all transformations
def build_pipeline_querytree(
    fdw: FeatureDefinitionWrapper, for_stream: bool, feature_data_time_limits: Optional[pendulum.Period] = None
) -> NodeRef:
    inputs_map = build_datasource_input_querynodes(fdw, for_stream, feature_data_time_limits)
    return FeatureViewPipelineNode.ref(
        inputs_map=inputs_map,
        feature_definition_wrapper=fdw,
        feature_time_limits=feature_data_time_limits,
    )


# builds a QueryTree for just whatever we would materialize
# ie partial aggregates for WAFVs.
def build_run_querytree(
    fdw: FeatureDefinitionWrapper, for_stream: bool, feature_data_time_limits: Optional[pendulum.Period] = None
) -> NodeRef:
    assert not for_stream or feature_data_time_limits is None, "Cannot run with time limits on a stream source"
    base = build_pipeline_querytree(fdw, for_stream, feature_data_time_limits)
    tree = FeatureTimeFilterNode.ref(
        base,
        feature_data_time_limits=feature_data_time_limits,
        policy=fdw.time_range_policy,
        timestamp_field=fdw.timestamp_key,
    )
    if fdw.is_temporal:
        tree = SetAnchorTimeNode.ref(
            tree,
            offline=True,
            feature_store_format_version=fdw.get_feature_store_format_version,
            batch_schedule_in_feature_store_specific_version_units=time_utils.convert_proto_duration_for_version(
                fdw.fv.materialization_params.schedule_interval, fdw.get_feature_store_format_version
            ),
            timestamp_field=fdw.timestamp_key,
            retrieval=False,
        )
    elif fdw.is_temporal_aggregate:

        tree = PartialAggNode.ref(tree, fdw)
    else:
        raise Exception("unexpected FV type")
    return tree


# QueryTree for getting data from offline store
def build_offline_store_scan_querytree(fdw: FeatureDefinitionWrapper) -> NodeRef:
    return OfflineStoreScanNode.ref(feature_definition_wrapper=fdw)


def build_get_features(fdw: FeatureDefinitionWrapper, from_source: bool):
    if not from_source:
        if not fdw.writes_to_offline_store:
            raise errors.FV_NEEDS_TO_BE_MATERIALIZED(fdw.name)
        return build_offline_store_scan_querytree(fdw)
    else:
        if fdw.is_incremental_backfill:
            raise errors.FV_BFC_SINGLE_FROM_SOURCE
        return build_run_querytree(fdw, for_stream=False, feature_data_time_limits=None)


def build_get_features_from_spine_agg(
    fdw: FeatureDefinitionWrapper,
    spine: Any,
    spine_time_field: str,
    spine_join_keys: List[Tuple[str]],
    from_source: bool,
):
    base = build_get_features(fdw, from_source)
    return FullAggNode.ref(base, fdw, spine, spine_time_field, spine_join_keys)


def build_spine_join_querytree(
    dac: FeatureDefinitionAndJoinConfig, spine: Any, spine_time_field: str, from_source: bool
) -> NodeRef:
    fdw = dac.feature_definition
    spine_node = DataNode.ref(spine)
    if spine_time_field != fdw.timestamp_key:
        spine_node = RenameColsNode.ref(spine_node, {spine_time_field: fdw.timestamp_key})
    if any([jk[0] != jk[1] for jk in dac.join_keys]):
        spine_node = RenameColsNode.ref(spine_node, {jk[0]: jk[1] for jk in dac.join_keys if jk[0] != jk[1]})
    if fdw.is_temporal or fdw.is_feature_table:
        base = build_get_features(fdw, from_source=from_source)
        rightside_join_prefix = "_tecton_right"
        join_prefixed_feature_names = [f"{rightside_join_prefix}_{f}" for f in fdw.features]
        # we can't just ask for the correct right_prefix to begin with because the asofJoin always sticks an extra underscore in between
        rename_map = {
            f"{rightside_join_prefix}_{f}": f"{dac.namespace}{fdw.namespace_separator}{f}"
            for f in fdw.features
            if f in dac.features
        }
        for f in fdw.features:
            if f not in dac.features:
                rename_map[f"{rightside_join_prefix}_{f}"] = None
            else:
                rename_map[f"{rightside_join_prefix}_{f}"] = f"{dac.namespace}{fdw.namespace_separator}{f}"

        rename_map[f"{rightside_join_prefix}_{fdw.timestamp_key}"] = None
        rename_map[f"{rightside_join_prefix}_{ANCHOR_TIME}"] = None

        if fdw.feature_start_timestamp is not None:
            base = RespectFSTNode.ref(base, fdw.timestamp_key, fdw.feature_start_timestamp, fdw.features)
        join = AsofJoinNode.ref(
            spine_node,
            base,
            join_cols=fdw.join_keys,
            timestamp_field=fdw.timestamp_key,
            right_prefix=rightside_join_prefix,
        )
        ttl_node = RespectTTLNode.ref(
            join,
            fdw.timestamp_key,
            f"{rightside_join_prefix}_{fdw.timestamp_key}",
            fdw.serving_ttl,
            join_prefixed_feature_names,
        )
        # remove anchor cols/dupe timestamp cols
        ret = RenameColsNode.ref(ttl_node, rename_map)
    elif fdw.is_temporal_aggregate:
        base = build_get_features_from_spine_agg(
            fdw, spine=spine, spine_time_field=spine_time_field, spine_join_keys=dac.join_keys, from_source=from_source
        )
        augmented_spine = SetAnchorTimeNode.ref(
            spine_node,
            offline=True,
            feature_store_format_version=fdw.get_feature_store_format_version,
            batch_schedule_in_feature_store_specific_version_units=fdw.get_tile_interval_for_version,
            timestamp_field=fdw.timestamp_key,
            retrieval=True,
        )
        rename_map = {}
        for f in fdw.features:
            if f not in dac.features:
                rename_map[f] = None
            else:
                rename_map[f] = f"{dac.namespace}{fdw.namespace_separator}{f}"
        right = RenameColsNode.ref(base, rename_map)
        join_keys = fdw.join_keys + [ANCHOR_TIME]
        # TODO: can consider having "inner" be an enum. right now join type as string can be passed directly to spark/snowflake
        join = JoinNode.ref(augmented_spine, right, how="inner", join_cols=join_keys)
        # Drop anchor time col
        ret = RenameColsNode.ref(join, {ANCHOR_TIME: None})
    elif fdw.is_on_demand:
        inputs = find_dependent_feature_set_items(
            fdw.fco_container,
            fdw.pipeline.root,
            visited_inputs={},
            fv_id=fdw.id,
            workspace_name=fdw.workspace,
        )
        dac = FeatureDefinitionAndJoinConfig.from_feature_definition(fdw)
        fsc = FeatureSetConfig(inputs + [dac])
        ret = build_feature_set_config_querytree(fsc, spine, spine_time_field, from_source)
    else:
        raise NotImplementedError
    if spine_time_field != fdw.timestamp_key:
        ret = RenameColsNode.ref(ret, {fdw.timestamp_key: spine_time_field})
    if any([jk[0] != jk[1] for jk in dac.join_keys]):
        ret = RenameColsNode.ref(ret, {jk[1]: jk[0] for jk in dac.join_keys if jk[0] != jk[1]})
    return ret


# Construct each materialized fvtree by joining against distinct set of join keys.
# Then, join the full spine against each of those.
# Finally, compute odfvs via udf on top of the result (not using joins)
def build_feature_set_config_querytree(
    fsc: FeatureSetConfig, spine: Any, spine_time_field: str, from_source: bool
) -> NodeRef:
    spine_node = DataNode.ref(spine)
    spine_join_keys = fsc.join_keys
    newtree = spine_node
    odfv_dacs = [dac for dac in fsc._definitions_and_configs if dac.feature_definition.is_on_demand]
    other_dacs = [dac for dac in fsc._definitions_and_configs if not dac.feature_definition.is_on_demand]
    internal_cols = set()
    # do all non on-demand first
    for dac in other_dacs:
        fdw = dac.feature_definition
        subspine_join_keys = [jk[0] for jk in dac.join_keys]
        if dac.namespace.startswith("_udf_internal"):
            for feature in fdw.features:
                internal_cols.add(dac.namespace + fdw.namespace_separator + feature)
        for feature in dac.features:
            if "_udf_internal" in feature:
                internal_cols.add(feature)
        subspine = spine.select([jk[0] for jk in dac.join_keys] + [spine_time_field]).distinct()
        fvtree = build_spine_join_querytree(dac, subspine, spine_time_field, from_source)
        if len(dac.features) < len(fdw.features):
            fvtree = RenameColsNode.ref(
                fvtree, {f"{fdw.name}{fdw.namespace_separator}{f}": None for f in fdw.features if f not in dac.features}
            )
        newtree = JoinNode.ref(newtree, fvtree, how="inner", join_cols=subspine_join_keys + [spine_time_field])
    # do all on-demand next
    for dac in odfv_dacs:
        fdw = dac.feature_definition
        newtree = OdfvPipelineNode.ref(newtree, fdw, dac.namespace)
        if len(dac.features) < len(fdw.features):
            drop_map = {
                f"{dac.namespace}{fdw.namespace_separator}{f}": None for f in fdw.features if f not in dac.features
            }
            newtree = RenameColsNode.ref(newtree, drop_map)
    # drop all internal cols
    if len(internal_cols) > 0:
        newtree = RenameColsNode.ref(newtree, {col: None for col in internal_cols})

    return newtree
