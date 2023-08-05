from collections import namedtuple
from enum import Enum
from typing import List
from typing import Union

from pyspark.sql import types as spark_types
from typeguard import typechecked

from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper


class DataType(namedtuple("DataType", ["name", "spark_type"]), Enum):
    Int64 = "int64", spark_types.LongType()
    Float32 = "float32", spark_types.FloatType()
    Float64 = "float64", spark_types.DoubleType()
    String = "string", spark_types.StringType()
    Bool = "bool", spark_types.BooleanType()
    Timestamp = "timestamp", spark_types.TimestampType()


class Array:
    def __init__(self, element_type: Union[DataType, "Array", "Struct"]):
        self.element_type = element_type

    @property
    def spark_type(self) -> spark_types.ArrayType:
        return spark_types.ArrayType(self.element_type.spark_type)


Int64 = DataType.Int64
Float32 = DataType.Float32
Float64 = DataType.Float64
String = DataType.String
Bool = DataType.Bool
Timestamp = DataType.Timestamp


@typechecked
class Field:
    def __init__(
        self,
        name: str,
        dtype: Union[DataType, Array, "Struct"],
    ):
        self.name = name
        self.dtype = dtype

    def spark_type(self) -> spark_types.StructField:
        return spark_types.StructField(self.name, self.dtype.spark_type)


@typechecked
class Struct:
    def __init__(self, fields: List[Field]):
        self.fields = fields

    @property
    def spark_type(self) -> spark_types.StructType:
        spark_fields = [field.spark_type() for field in self.fields]
        return spark_types.StructType(spark_fields)


def to_spark_schema_wrapper(field_list: List[Field]) -> SparkSchemaWrapper:
    s = spark_types.StructType([field.spark_type() for field in field_list])
    return SparkSchemaWrapper(s)
