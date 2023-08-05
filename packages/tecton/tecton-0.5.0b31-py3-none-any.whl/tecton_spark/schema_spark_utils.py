import pyspark.sql.types as spark_types

from tecton_core.data_types import ArrayType
from tecton_core.data_types import BoolType
from tecton_core.data_types import DataType
from tecton_core.data_types import Float32Type
from tecton_core.data_types import Float64Type
from tecton_core.data_types import Int32Type
from tecton_core.data_types import Int64Type
from tecton_core.data_types import StringType
from tecton_core.data_types import StructType
from tecton_core.data_types import TimestampType
from tecton_core.schema import Schema
from tecton_proto.common import column_type_pb2
from tecton_proto.common import schema_pb2
from tecton_proto.common.schema_pb2 import Schema as SchemaProto


def _column_proto(
    raw_spark_type: str,
    feature_server_type: column_type_pb2.ColumnType,
    offline_data_type: DataType,
    feature_server_data_type: DataType,
) -> schema_pb2.Column:
    column = schema_pb2.Column()
    column.raw_spark_type = raw_spark_type
    column.offline_data_type.CopyFrom(offline_data_type.proto)
    if feature_server_type:
        column.feature_server_type = feature_server_type
    column.feature_server_data_type.CopyFrom(feature_server_data_type.proto)

    return column


# Keep in sync with DataTypeUtils.kt. Use "simple strings" as the keys so that fields like "nullable" are ignored.
SPARK_TYPE_SIMPLE_STRING_TO_COLUMN = {
    spark_types.StringType().simpleString(): _column_proto(
        raw_spark_type="string",
        feature_server_type=column_type_pb2.COLUMN_TYPE_STRING,
        offline_data_type=StringType(),
        feature_server_data_type=StringType(),
    ),
    spark_types.LongType().simpleString(): _column_proto(
        raw_spark_type="long",
        feature_server_type=column_type_pb2.COLUMN_TYPE_INT64,
        offline_data_type=Int64Type(),
        feature_server_data_type=Int64Type(),
    ),
    spark_types.DoubleType().simpleString(): _column_proto(
        raw_spark_type="double",
        feature_server_type=column_type_pb2.COLUMN_TYPE_DOUBLE,
        offline_data_type=Float64Type(),
        feature_server_data_type=Float64Type(),
    ),
    spark_types.BooleanType().simpleString(): _column_proto(
        raw_spark_type="boolean",
        feature_server_type=column_type_pb2.COLUMN_TYPE_BOOL,
        offline_data_type=BoolType(),
        feature_server_data_type=BoolType(),
    ),
    # Int32 has a different offline and feature server data type.
    spark_types.IntegerType().simpleString(): _column_proto(
        raw_spark_type="integer",
        feature_server_type=column_type_pb2.COLUMN_TYPE_INT64,
        offline_data_type=Int32Type(),
        feature_server_data_type=Int64Type(),
    ),
    # Timestamp type is special since it does not have a ColumnType.
    spark_types.TimestampType().simpleString(): _column_proto(
        raw_spark_type="timestamp",
        feature_server_type=column_type_pb2.COLUMN_TYPE_DERIVE_FROM_DATA_TYPE,
        offline_data_type=TimestampType(),
        feature_server_data_type=TimestampType(),
    ),
    # Array types.
    spark_types.ArrayType(spark_types.LongType()).simpleString(): _column_proto(
        raw_spark_type="long_array",
        feature_server_type=column_type_pb2.COLUMN_TYPE_INT64_ARRAY,
        offline_data_type=ArrayType(Int64Type()),
        feature_server_data_type=ArrayType(Int64Type()),
    ),
    spark_types.ArrayType(spark_types.FloatType()).simpleString(): _column_proto(
        raw_spark_type="float_array",
        feature_server_type=column_type_pb2.COLUMN_TYPE_FLOAT_ARRAY,
        offline_data_type=ArrayType(Float32Type()),
        feature_server_data_type=ArrayType(Float32Type()),
    ),
    spark_types.ArrayType(spark_types.DoubleType()).simpleString(): _column_proto(
        raw_spark_type="double_array",
        feature_server_type=column_type_pb2.COLUMN_TYPE_DOUBLE_ARRAY,
        offline_data_type=ArrayType(Float64Type()),
        feature_server_data_type=ArrayType(Float64Type()),
    ),
    spark_types.ArrayType(spark_types.StringType()).simpleString(): _column_proto(
        raw_spark_type="string_array",
        feature_server_type=column_type_pb2.COLUMN_TYPE_STRING_ARRAY,
        offline_data_type=ArrayType(StringType()),
        feature_server_data_type=ArrayType(StringType()),
    ),
}

# Map from simple (i.e non-complex) Tecton data types to Spark Types.
SIMPLE_TECTON_DATA_TYPE_TO_SPARK_DATA_TYPE = {
    Int32Type(): spark_types.IntegerType(),
    Int64Type(): spark_types.LongType(),
    Float32Type(): spark_types.FloatType(),
    Float64Type(): spark_types.DoubleType(),
    StringType(): spark_types.StringType(),
    BoolType(): spark_types.BooleanType(),
    TimestampType(): spark_types.TimestampType(),
}


def schema_from_spark(spark_schema: spark_types.StructType) -> Schema:
    proto = SchemaProto()
    for field in spark_schema:
        column = proto.columns.add()

        if field.dataType.simpleString() not in SPARK_TYPE_SIMPLE_STRING_TO_COLUMN:
            raise ValueError(
                f"Field {field.name} is of type {field.dataType.simpleString()}, which is not a supported type for features. "
                + f"Please change {field.name} to be one of our supported types: https://docs.tecton.ai/latest/faq/creating_and_managing_features.html"
            )
        column.CopyFrom(SPARK_TYPE_SIMPLE_STRING_TO_COLUMN[field.dataType.simpleString()])
        column.name = field.name

    return Schema(proto)


def _spark_data_type_from_tecton_data_type(tecton_data_type: DataType) -> spark_types.DataType:
    if tecton_data_type in SIMPLE_TECTON_DATA_TYPE_TO_SPARK_DATA_TYPE:
        return SIMPLE_TECTON_DATA_TYPE_TO_SPARK_DATA_TYPE[tecton_data_type]
    elif isinstance(tecton_data_type, ArrayType):
        element_type = _spark_data_type_from_tecton_data_type(tecton_data_type.element_type)
        return spark_types.ArrayType(element_type)
    elif isinstance(tecton_data_type, StructType):
        spark_struct = spark_types.StructType()
        for field in tecton_data_type.fields:
            spark_struct.add(field.name, _spark_data_type_from_tecton_data_type(field.data_type))
        return spark_struct
    else:
        assert False, f"Unsupported type: {tecton_data_type}"


def schema_to_spark(schema: Schema) -> spark_types.StructType:
    ret = spark_types.StructType()
    for col_name, col_spark_data_type in column_name_spark_data_types(schema):
        ret.add(col_name, col_spark_data_type)
    return ret


def column_name_spark_data_types(schema: Schema):
    return [(c[0], _spark_data_type_from_tecton_data_type(c[1])) for c in schema.column_name_and_data_types()]
