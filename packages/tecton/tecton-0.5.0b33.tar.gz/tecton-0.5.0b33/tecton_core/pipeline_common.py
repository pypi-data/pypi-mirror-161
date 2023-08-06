from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
from typing import Union

import pandas
import pendulum

from tecton_core import time_utils
from tecton_core.fco_container import FcoContainer
from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper
from tecton_core.feature_set_config import FeatureDefinitionAndJoinConfig
from tecton_core.id_helper import IdHelper
from tecton_proto.args.new_transformation_pb2 import NewTransformationArgs as TransformationArgs
from tecton_proto.args.pipeline_pb2 import ConstantNode
from tecton_proto.args.pipeline_pb2 import DataSourceNode
from tecton_proto.args.pipeline_pb2 import Input as InputProto
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.data.new_transformation_pb2 import NewTransformation as Transformation

CONSTANT_TYPE = Optional[Union[str, int, float, bool]]


def _make_mode_to_type():
    lookup = {
        "pandas": pandas.DataFrame,
        "python": Dict,
        "pipeline": PipelineNode,
        "spark_sql": str,
        "snowflake_sql": str,
    }
    try:
        import pyspark.sql

        lookup["pyspark"] = pyspark.sql.DataFrame
    except ImportError:
        pass
    try:
        import snowflake.snowpark

        lookup["snowpark"] = snowflake.snowpark.DataFrame
    except ImportError:
        pass
    return lookup


MODE_TO_TYPE_LOOKUP = _make_mode_to_type()


def constant_node_to_value(constant_node: ConstantNode) -> CONSTANT_TYPE:
    if constant_node.HasField("string_const"):
        return constant_node.string_const
    elif constant_node.HasField("int_const"):
        return int(constant_node.int_const)
    elif constant_node.HasField("float_const"):
        return float(constant_node.float_const)
    elif constant_node.HasField("bool_const"):
        return constant_node.bool_constant
    elif constant_node.HasField("null_const"):
        return None
    raise KeyError(f"Unknown ConstantNode type: {constant_node}")


def get_keyword_inputs(transformation_node) -> Dict[str, InputProto]:
    """Returns the keyword inputs of transformation_node in a dict."""
    return {
        node_input.arg_name: node_input for node_input in transformation_node.inputs if node_input.HasField("arg_name")
    }


def positional_inputs(transformation_node) -> List[InputProto]:
    """Returns the positional inputs of transformation_node in order."""
    return [node_input for node_input in transformation_node.inputs if node_input.HasField("arg_index")]


def get_transformation_name(transformation: Union[Transformation, TransformationArgs]) -> str:
    if isinstance(transformation, Transformation):
        return transformation.fco_metadata.name
    elif isinstance(transformation, TransformationArgs):
        return transformation.info.name
    else:
        # should ideally never be thrown
        raise Exception(f"Invalid type (expected Transformation or TransformationArgs): {type(transformation)}")


def transformation_type_checker(object_name, result, mode, supported_modes):
    possible_mode = None
    for candidate_mode, candidate_type in MODE_TO_TYPE_LOOKUP.items():
        if isinstance(result, candidate_type):
            possible_mode = candidate_mode
            break
    expected_type = MODE_TO_TYPE_LOOKUP[mode]
    actual_type = type(result)

    if isinstance(result, expected_type):
        return
    elif possible_mode is not None and possible_mode in supported_modes:
        raise TypeError(
            f"Transformation function {object_name} with mode '{mode}' is expected to return result with type {expected_type}, but returns result with type {actual_type} instead. Did you mean to set mode='{possible_mode}'?"
        )
    else:
        raise TypeError(
            f"Transformation function {object_name} with mode {mode} is expected to return result with type {expected_type}, but returns result with type {actual_type} instead."
        )


def get_time_window_from_data_source_node(
    feature_time_limits: Optional[pendulum.Period],
    schedule_interval: Optional[pendulum.Duration],
    data_source_node: DataSourceNode,
) -> Optional[pendulum.Period]:
    if data_source_node.HasField("window") and feature_time_limits:
        new_start = feature_time_limits.start - time_utils.proto_to_duration(data_source_node.window)
        if schedule_interval:
            new_start = new_start + schedule_interval
        raw_data_limits = pendulum.Period(new_start, feature_time_limits.end)
    elif data_source_node.HasField("window_unbounded_preceding") and feature_time_limits:
        raw_data_limits = pendulum.Period(pendulum.datetime(1970, 1, 1), feature_time_limits.end)
    elif data_source_node.HasField("start_time_offset") and feature_time_limits:
        new_start = feature_time_limits.start + time_utils.proto_to_duration(data_source_node.start_time_offset)
        raw_data_limits = pendulum.Period(new_start, feature_time_limits.end)
    elif data_source_node.HasField("window_unbounded"):
        raw_data_limits = None
    else:
        # no data_source_override has been set
        raw_data_limits = feature_time_limits
    return raw_data_limits


def find_dependent_feature_set_items(
    fco_container: FcoContainer, node: PipelineNode, visited_inputs: Mapping[str, bool], fv_id: str, workspace_name: str
) -> List[FeatureDefinitionAndJoinConfig]:
    if node.HasField("feature_view_node"):
        if node.feature_view_node.input_name in visited_inputs:
            return []
        visited_inputs[node.feature_view_node.input_name] = True

        fv_proto = fco_container.get_by_id(IdHelper.to_string(node.feature_view_node.feature_view_id))
        fd = FeatureDefinitionWrapper(fv_proto, fco_container)

        join_keys = []
        overrides = {
            colpair.feature_column: colpair.spine_column
            for colpair in node.feature_view_node.feature_view.override_join_keys
        }
        for join_key in fv_proto.join_keys:
            potentially_overriden_key = overrides.get(join_key, join_key)
            join_keys.append((potentially_overriden_key, join_key))

        cfg = FeatureDefinitionAndJoinConfig(
            feature_definition=fd,
            name=fd.name,
            join_keys=join_keys,
            namespace=f"_udf_internal_{node.feature_view_node.input_name}_{fv_id}",
            features=node.feature_view_node.feature_view.features or fd.features,
        )

        return [cfg]
    elif node.HasField("transformation_node"):
        ret: List[FeatureDefinitionAndJoinConfig] = []
        for child in node.transformation_node.inputs:
            ret = ret + find_dependent_feature_set_items(
                fco_container, child.node, visited_inputs, fv_id, workspace_name
            )
        return ret
    return []
