from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from tecton._internals import errors
from tecton._internals.fco import Fco
from tecton.declarative.base import BaseEntity
from tecton.declarative.basic_info import prepare_basic_info
from tecton_core import errors
from tecton_core.feature_definition_wrapper import FrameworkVersion
from tecton_core.id_helper import IdHelper
from tecton_core.logger import get_logger
from tecton_proto.args.basic_info_pb2 import BasicInfo
from tecton_proto.args.entity_pb2 import EntityArgs
from tecton_proto.args.repo_metadata_pb2 import SourceInfo
from tecton_proto.common.id_pb2 import Id


logger = get_logger("Entity")


class Entity(BaseEntity):
    """
    Declare an Entity, used to organize and join features.

    An Entity is a class that represents an Entity that is being modeled in Tecton.
    Entities are used to index and organize features - a :class:`FeatureView`
    contains at least one Entity.

    Entities contain metadata about *join keys*, which represent the columns
    that are used to join features together.

    Example of an Entity declaration:

    .. code-block:: python

        from tecton import Entity

        customer = Entity(
            name='churned_customer',
            join_keys=['customer_id'],
            description='A customer subscribing to a Sports TV subscription service',
            owner='matt@tecton.ai',
            tags={'release': 'development'})
    """

    _args: EntityArgs
    _source_info: SourceInfo

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        owner: Optional[str] = None,
        join_keys: Optional[Union[str, List[str]]] = None,
    ):
        """
        Declare a new Entity.

        :param name: Unique name for the new entity.
        :param description: Short description of the new entity.
        :param tags: Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
        :param owner: Owner name (typically the email of the primary maintainer).
        :param join_keys: Names of columns that uniquely identify the entity in FeatureView's SQL statement
            for which features should be aggregated. Defaults to using ``name`` as the entity's join key.

        :raises TectonValidationError: if the input parameters are invalid.
        """
        from tecton.cli.common import get_fco_source_info

        if join_keys is None:
            raise errors.TectonValidationError("You must specify `join_keys` to create an Entity object.")

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, tags=tags, family=None)

        if not join_keys:
            resolved_join_keys = [name]
        elif isinstance(join_keys, str):
            resolved_join_keys = [join_keys]
        else:
            resolved_join_keys = join_keys

        args = prepare_args(join_keys=resolved_join_keys, basic_info=basic_info)

        self._source_info = get_fco_source_info()
        self._args = args

        Fco._register(self)

    @property
    def name(self) -> str:
        """
        Name of the entity.
        """
        return self._args.info.name

    @property
    def join_keys(self) -> List[str]:
        """
        Join keys of the entity.
        """
        return list(self._args.join_keys)

    @property
    def _id(self) -> Id:
        return self._args.entity_id


def prepare_args(*, basic_info: BasicInfo, join_keys: List[str]) -> EntityArgs:
    args = EntityArgs()
    args.entity_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))
    args.version = FrameworkVersion.FWV5.value
    args.info.CopyFrom(basic_info)
    args.join_keys.extend(join_keys)
    return args
