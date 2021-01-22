from graphviz import Digraph
from abc import ABC, abstractmethod

class Context(ABC):
    __directions = ("TB", "BT", "LR", "RL")

    def __init__(self, name):
        self.name = name
        self.dot = Digraph(self.name)

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

    def node(self, nodeid: str, label: str, **attrs) -> None:
        """Create a new node."""
        self.dot.node(nodeid, label=label, **attrs)


    def subgraph(self, dot: Digraph):
        """Create a subgraph for clustering"""
        self.dot.subgraph(dot)
