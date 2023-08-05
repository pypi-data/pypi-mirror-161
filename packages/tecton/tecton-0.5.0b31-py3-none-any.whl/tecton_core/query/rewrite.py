from abc import ABC
from abc import abstractmethod

from tecton_core import conf
from tecton_core.query.node_interface import NodeRef


class Rewrite(ABC):
    @abstractmethod
    def rewrite(self, node: NodeRef) -> NodeRef:
        raise NotImplementedError


# Mutates the input
def rewrite_tree(tree: NodeRef):
    if not conf.get_bool("QUERY_REWRITE_ENABLED"):
        return
    rewrites = []
    for rewrite in rewrites:
        rewrite.rewrite(tree)
