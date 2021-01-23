import os, sys, uuid, html
from pathlib import Path
from typing import List, Union, Dict
from .Edge import Edge
from .Cluster import Cluster
from .utils import setcluster, getcluster, getdiagram, new_init

class Node(Cluster):
    """Node represents a node for a specific backend service."""

    _provider = None
    _type = None

    _icon_dir = None
    _icon = None
    _icon_size = 30
    _loaded_icon = None
    _direction = "TB"

    _height = 1.9

    def __init__(self,
                 label: str = "",
                 icon_size: int = None,
                 **attrs: Dict):
        """Node represents a system component.

        :param label: Node label.
        :param icon_size: The icon size when used as a Cluster. Default is 30.
        """
        # Generates an ID for identifying a node.
        self._id = self._rand_id()
        self.label = label

        super().__init__(self.label)

        if icon_size:
            self._icon_size = icon_size

        # fmt: off
        # If a node has an icon, increase the height slightly to avoid
        # that label being spanned between icon image and white space.
        # Increase the height by the number of new lines included in the label.
        padding = 0.4 * (label.count('\n'))
        self._loaded_icon = self._load_icon()

        
        self._attrs = {
            "shape": "none",
            "height": str(self._height + padding),
            "image": self._loaded_icon,
        } if self._loaded_icon else {}

        # fmt: on
        self._attrs.update(attrs)

        # If a node is in the cluster context, add it to cluster.
        if self._parent is not None:
            # Adding node to diagram / cluster
            self._parent.node(self)
        else:
            raise EnvironmentError("Node must be belong to a diagram or cluster")

    def _before_enter(self):
        # If Node is used as context remove the node from the graph
        if self._parent is not None and getattr(self._parent, "remove_node", False):
            self._parent.remove_node(self)
        self._attrs = {}

    def __enter__(self):
        super().__enter__()

        # Set attributes.
        for k, v in self._default_graph_attrs.items():
            self.dot.graph_attr[k] = v

        icon = self._load_icon()
        if icon:
            lines = iter(html.escape(self.label).split("\n"))
            self.dot.graph_attr["label"] = '<<TABLE border="0"><TR>' +\
                f'<TD fixedsize="true" width="{self._icon_size}" height="{self._icon_size}"><IMG SRC="{icon}"></IMG></TD>' +\
                f'<TD align="left">{next(lines)}</TD></TR>' +\
                ''.join(f'<TR><TD colspan="2" align="left">{line}</TD></TR>' for line in lines) +\
                '</TABLE>>'

        if not self._validate_direction(self._direction):
            raise ValueError(f'"{self._direction}" is not a valid direction')
        self.dot.graph_attr["rankdir"] = self._direction

        # Set cluster depth for distinguishing the background color
        self.depth = self._parent.depth + 1
        coloridx = self.depth % len(self.bgcolors)
        self.dot.graph_attr["bgcolor"] = self.bgcolors[coloridx]

        return self

    def __exit__(self, *args):
        super().__exit__(*args)
        self._id = "cluster_" + self.nodeid
        self.dot.name = self.nodeid

    def __repr__(self):
        _name = self.__class__.__name__
        return f"<{self._provider}.{self._type}.{_name}>"

    def __sub__(self, other: Union["Node", List["Node"], "Edge"]):
        """Implement Self - Node, Self - [Nodes] and Self - Edge."""
        if isinstance(other, list):
            for node in other:
                self.connect(node, Edge(self))
            return other
        elif isinstance(other, Node):
            return self.connect(other, Edge(self))
        else:
            other.node = self
            return other

    def __rsub__(self, other: Union[List["Node"], List["Edge"]]):
        """ Called for [Nodes] and [Edges] - Self because list don't have __sub__ operators. """
        for o in other:
            if isinstance(o, Edge):
                o.connect(self)
            else:
                o.connect(self, Edge(self))
        return self

    def __rshift__(self, other: Union["Node", List["Node"], "Edge"]):
        """Implements Self >> Node, Self >> [Nodes] and Self Edge."""
        if isinstance(other, list):
            for node in other:
                self.connect(node, Edge(self, forward=True))
            return other
        elif isinstance(other, Node):
            return self.connect(other, Edge(self, forward=True))
        else:
            other.forward = True
            other.node = self
            return other

    def __lshift__(self, other: Union["Node", List["Node"], "Edge"]):
        """Implements Self << Node, Self << [Nodes] and Self << Edge."""
        if isinstance(other, list):
            for node in other:
                self.connect(node, Edge(self, reverse=True))
            return other
        elif isinstance(other, Node):
            return self.connect(other, Edge(self, reverse=True))
        else:
            other.reverse = True
            return other.connect(self)

    def __rrshift__(self, other: Union[List["Node"], List["Edge"]]):
        """Called for [Nodes] and [Edges] >> Self because list don't have __rshift__ operators."""
        for o in other:
            if isinstance(o, Edge):
                o.forward = True
                o.connect(self)
            else:
                o.connect(self, Edge(self, forward=True))
        return self

    def __rlshift__(self, other: Union[List["Node"], List["Edge"]]):
        """Called for [Nodes] << Self because list of Nodes don't have __lshift__ operators."""
        for o in other:
            if isinstance(o, Edge):
                o.reverse = True
                o.connect(self)
            else:
                o.connect(self, Edge(self, reverse=True))
        return self

    @property
    def nodeid(self):
        return self._id

    # TODO: option for adding flow description to the connection edge
    def connect(self, node: "Node", edge: "Edge"):
        """Connect to other node.

        :param node: Other node instance.
        :param edge: Type of the edge.
        :return: Connected node.
        """
        if not isinstance(node, Node):
            ValueError(f"{node} is not a valid Node")
        if not isinstance(node, Edge):
            ValueError(f"{node} is not a valid Edge")
        # An edge must be added on the global diagrams, not a cluster.
        getdiagram().connect(self, node, edge)
        return node

    @staticmethod
    def _rand_id():
        return uuid.uuid4().hex

    def _load_icon(self):
        if self._icon and self._icon_dir:
            basedir = Path(os.path.abspath(os.path.dirname(__file__)))
            return os.path.join(basedir.parent, self._icon_dir, self._icon)
        return None
