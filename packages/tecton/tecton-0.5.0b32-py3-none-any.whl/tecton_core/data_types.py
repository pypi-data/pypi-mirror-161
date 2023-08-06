from typing import List

from tecton_proto.common import data_type_pb2


class DataType:
    """
    Base DataType class. A python utility for working with `tecton_proto.common.DataType` protos.
    """

    @property
    def proto(self) -> data_type_pb2.DataType:
        # Return a copy of the underlying proto.
        proto = data_type_pb2.DataType()
        proto.CopyFrom(self._proto)
        return proto

    def __hash__(self):
        return hash(self._proto.SerializeToString(deterministic=True))

    def __eq__(self, other):
        return self._proto == other._proto

    def __str__(self):
        # Require __str__ implementation. Used in error messages.
        raise NotImplementedError


class Int32Type(DataType):
    def __init__(self):
        self._proto = data_type_pb2.DataType()
        self._proto.type = data_type_pb2.DATA_TYPE_INT32

    def __str__(self):
        return "Int32"


class Int64Type(DataType):
    def __init__(self):
        self._proto = data_type_pb2.DataType()
        self._proto.type = data_type_pb2.DATA_TYPE_INT64

    def __str__(self):
        return "Int64"


class Float32Type(DataType):
    def __init__(self):
        self._proto = data_type_pb2.DataType()
        self._proto.type = data_type_pb2.DATA_TYPE_FLOAT32

    def __str__(self):
        return "Float32"


class Float64Type(DataType):
    def __init__(self):
        self._proto = data_type_pb2.DataType()
        self._proto.type = data_type_pb2.DATA_TYPE_FLOAT64

    def __str__(self):
        return "Float64"


class StringType(DataType):
    def __init__(self):
        self._proto = data_type_pb2.DataType()
        self._proto.type = data_type_pb2.DATA_TYPE_STRING

    def __str__(self):
        return "String"


class BoolType(DataType):
    def __init__(self):
        self._proto = data_type_pb2.DataType()
        self._proto.type = data_type_pb2.DATA_TYPE_BOOL

    def __str__(self):
        return "Bool"


class TimestampType(DataType):
    def __init__(self):
        self._proto = data_type_pb2.DataType()
        self._proto.type = data_type_pb2.DATA_TYPE_TIMESTAMP

    def __str__(self):
        return "Timestamp"


class ArrayType(DataType):
    _element_type: DataType

    def __init__(self, element_type: DataType):
        self._proto = data_type_pb2.DataType()
        self._proto.type = data_type_pb2.DATA_TYPE_ARRAY
        self._proto.array_element_type.CopyFrom(element_type._proto)
        self._element_type = element_type

    @property
    def element_type(self) -> DataType:
        return self._element_type

    def __str__(self):
        return f"Array({self._element_type})"


# Note StructField does not inherit from DataType. This is because it is not directly convertable to a data type proto.
class StructField:
    def __init__(self, name: str, data_type: DataType):
        self._name = name
        self._data_type = data_type
        self._proto = data_type_pb2.StructField()
        self._proto.data_type.CopyFrom(data_type._proto)
        self._proto.name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def data_type(self) -> DataType:
        return self._data_type

    def __hash__(self):
        return hash(self._proto.SerializeToString(deterministic=True))

    def __eq__(self, other):
        return self._proto == other._proto

    def __str__(self):
        return f"Field({self._name}, {self._data_type})"


class StructType(DataType):
    def __init__(self, fields: List[StructField]):
        self._fields = fields
        self._proto = data_type_pb2.DataType()
        self._proto.type = data_type_pb2.DATA_TYPE_STRUCT
        self._proto.struct_fields.extend([field._proto for field in fields])

    @property
    def fields(self) -> List[StructField]:
        return self._fields

    def __str__(self):
        fields_string = ", ".join(str(field) for field in self._fields)
        return f"Struct({fields_string})"


def data_type_from_proto(proto: data_type_pb2.DataType) -> DataType:
    """
    Factory method to creata a DataType python class from a `tecton_proto.common.DataType` proto.
    """
    assert proto
    assert proto.type

    if proto.type == data_type_pb2.DATA_TYPE_INT32:
        return Int32Type()
    elif proto.type == data_type_pb2.DATA_TYPE_INT64:
        return Int64Type()
    elif proto.type == data_type_pb2.DATA_TYPE_FLOAT32:
        return Float32Type()
    elif proto.type == data_type_pb2.DATA_TYPE_FLOAT64:
        return Float64Type()
    elif proto.type == data_type_pb2.DATA_TYPE_STRING:
        return StringType()
    elif proto.type == data_type_pb2.DATA_TYPE_BOOL:
        return BoolType()
    elif proto.type == data_type_pb2.DATA_TYPE_TIMESTAMP:
        return TimestampType()
    elif proto.type == data_type_pb2.DATA_TYPE_ARRAY:
        assert proto.array_element_type
        element_type = data_type_from_proto(proto.array_element_type)
        return ArrayType(element_type)
    elif proto.type == data_type_pb2.DATA_TYPE_STRUCT:
        fields = [StructField(field.name, data_type_from_proto(field.data_type)) for field in proto.struct_fields]
        return StructType(fields)
    else:
        raise ValueError(f"Unexpected data type {proto}")
