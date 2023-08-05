from tecton_core.errors import TectonValidationError
from tecton_proto.args.user_defined_function_pb2 import UserDefinedFunction


def from_proto(serialized_transform: UserDefinedFunction, scope=None):
    """
    deserialize into global scope by default. if a scope if provided, deserialize into provided scope
    """

    if scope is None:
        # PySpark has issues if the UDFs are not in global scope
        scope = __import__("__main__").__dict__

    assert serialized_transform.HasField("body") and serialized_transform.HasField(
        "name"
    ), "Invalid UserDefinedFunction."

    try:
        exec(serialized_transform.body, scope)
    except NameError as e:
        raise TectonValidationError(
            "Failed to serialize function. Please note that all imports must be in the body of the function (not top-level) and type annotations cannot require imports. Additionally, be cautious of variables that shadow other variables. See https://docs.tecton.ai/v2/overviews/framework/transformations.html for more details.",
            e,
        )

    # Return function pointer
    try:
        fn = eval(serialized_transform.name, scope)
        fn._code = serialized_transform.body
        return fn
    except Exception as e:
        raise ValueError("Invalid transform") from e
