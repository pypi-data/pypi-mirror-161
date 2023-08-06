from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Tuple

global_id = 1
global_map = {}


def get_new_id():
    global global_id
    global_id += 1
    return global_id


@dataclass
class NodeRef:
    """
    Used so we can more easily modify the QueryTree by inserting and removing nodes, e.g.
    def subtree_rewrite(subtree_node_ref):
        subtree_node_ref.node = NewNode(subtree_node_ref.node)
    """

    node: "QueryNode"

    @property
    def inputs(self):
        return self.node.inputs

    def as_str(self, verbose: bool = False) -> str:
        return self.node.as_str(verbose)

    def pretty_print(self, verbose: bool = False, indents=0, show_ids=True):
        return self.node.pretty_print(verbose, indents, show_ids)


class QueryNode(ABC):
    @classmethod
    def ref(cls, *args, **kwargs):
        return NodeRef(cls(*args, **kwargs))

    # used for recursing through the tree for tree rewrites
    @property
    @abstractmethod
    def inputs(self) -> Tuple[NodeRef]:
        pass

    @abstractmethod
    def as_str(self, verbose: bool) -> str:
        """
        Prints contents of this node and calls recursively on its inputs.
        Used by tecton.DataFrame.explain
        """
        pass

    # TODO: update this placeholder printing logic with something that looks beautiful
    def pretty_print(self, verbose: bool = False, indents=0, show_ids=True) -> str:
        if show_ids:
            new_id = get_new_id()
            global_map[new_id] = self
            s = f"<{new_id}>"
        else:
            s = ""
        lines = self.as_str(verbose=verbose).rstrip()
        for line in lines.split("\n"):
            s += "  " * indents + line + "\n"
        if len(self.inputs) == 1:
            s += self.inputs[0].pretty_print(verbose, indents + 1, show_ids)
        else:
            for i in self.inputs:
                s += i.pretty_print(verbose, indents + 1, show_ids)
        return s
