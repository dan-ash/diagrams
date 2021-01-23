from graphviz import Digraph, lang
from abc import ABC, abstractmethod

class Context(ABC):
    __directions = ("TB", "BT", "LR", "RL")
    __bgcolors = ("#E5F5FD", "#EBF3E7", "#ECE8F6", "#FDF7E3")
    __depth = 0

    @property
    def bgcolors(self):
        return self.__bgcolors

    @property
    def depth(self):
        return self.__depth

    @depth.setter
    def depth(self, value):
        self.__depth = value

    def __init__(self, name, **kwargs):
        self.name = name
        self.dot = Digraph(self.name, **kwargs)

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def _validate_direction(self, direction: str) -> bool:
        direction = direction.upper()
        for v in self.__directions:
            if v == direction:
                return True
        return False

    def node(self, node: "Node") -> None:
        """Create a new node."""
        self.dot.node(node.nodeid, label=node.label, **node._attrs)

    def remove_node(self, node: "Node") -> None:
        """Create a new node."""
        self.dot.body.remove('\t' + f"{lang.quote(node.nodeid)}{lang.attr_list(node.label,node._attrs)}")

    @abstractmethod
    def subgraph(self, dot: Digraph):
        pass
