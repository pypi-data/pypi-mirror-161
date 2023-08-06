from tecton_core.id_helper import IdHelper
from tecton_proto.common.id_pb2 import Id

_ALL_FCOS = {}

# An internal superclass of declarative Tecton Objects
class Fco:
    @classmethod
    def _register(cls, fco):
        id = fco._id
        assert id.most_significant_bits > 0 and id.least_significant_bits > 0, f"Object {fco} has no `id` set."
        _ALL_FCOS[IdHelper.to_string(id)] = fco

    @property
    def _id(self) -> Id:
        """
        The id of this Tecton Object.
        """
        raise NotImplementedError()
