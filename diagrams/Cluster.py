from graphviz import Digraph
from .Context import Context
from .utils import setcluster, getcluster, getdiagram

class Cluster(Context):
    # fmt: off
    _default_graph_attrs = {
        "shape": "box",
        "style": "rounded",
        "labeljust": "l",
        "pencolor": "#AEB6BE",
        "fontname": "Sans-Serif",
        "fontsize": "12",
    }

    # fmt: on

    # FIXME:
    #  Cluster direction does not work now. Graphviz couldn't render
    #  correctly for a subgraph that has a different rank direction.
    def __init__(
        self,
        label: str = "cluster",
        direction: str = "LR",
        graph_attr: dict = {},
    ):
        """Cluster represents a cluster context.

        :param label: Cluster label.
        :param direction: Data flow direction. Default is 'left to right'.
        :param graph_attr: Provide graph_attr dot config attributes.
        """
        self.nodes = {}
        self.subgraphs = []
        self.label = label
        super().__init__("cluster_" + self.label)

        # Set attributes.
        for k, v in self._default_graph_attrs.items():
            self.dot.graph_attr[k] = v
        self.dot.graph_attr["label"] = self.label

        if not self._validate_direction(direction):
            raise ValueError(f'"{direction}" is not a valid direction')
        self.dot.graph_attr["rankdir"] = direction

        # Node must be belong to a diagrams.
        try:
            self._parent = getcluster() or getdiagram()
        except EnvironmentError:
            self._parent = None

        # Set cluster depth for distinguishing the background color
        self.depth = self._parent.depth + 1 if self._parent else 0
        coloridx = self.depth % len(self.bgcolors)
        self.dot.graph_attr["bgcolor"] = self.bgcolors[coloridx]

        # Merge passed in attributes
        self.dot.graph_attr.update(graph_attr)

    def __enter__(self):
        self._before_enter()
        setcluster(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._parent:
            self._parent.subgraph(self.dot)

        if len(self.nodes.values()) > 0:
            for node in self.nodes.values():
                self.dot.node(node.nodeid, label=node.label, **node._attrs)

        if len(self.subgraphs) > 0:
            for subgraph in self.subgraphs:
                self.dot.subgraph(subgraph)

        setcluster(self._parent)


    def node(self, node: "Node") -> None:
        """Create a new node."""
        self.nodes[node.nodeid] = node
        self.dot.node(node.nodeid, label=node.label, **node._attrs)

    def remove_node(self, node: "Node") -> None:
        del self.nodes[node.nodeid]
        super().remove_node(node)

    def subgraph(self, subgraph: "Cluster") -> None:
        """Create a subgraph for clustering"""
        self.subgraphs.append(subgraph)
        self.dot.subgraph(subgraph)

    def _before_enter(self):
        pass

    @property
    def nodes_iter(self):
        if self.nodes:
            yield from self.nodes.values()
        if self.subgraphs:
            for subgraph in self.subgraphs:
                yield from subgraph.nodes_iter
