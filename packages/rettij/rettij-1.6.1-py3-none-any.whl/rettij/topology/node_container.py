from unittest.mock import MagicMock

from rettij.topology.network_components.node import Node


class NodeContainer(dict):
    """
    Provide a simple container for Nodes.

    Enable a way that single items can be accessed as attributes, e.g. node.n1.
    Supports dict-based access by inheriting from the built-in `dict` class.
    """

    def __setitem__(self, node_name: str, node: Node) -> None:
        if not isinstance(node_name, str):
            raise TypeError(f"'node_name' must be of type 'str', not '{type(node_name)}'!")
        if not (isinstance(node, Node) or isinstance(node, MagicMock)):  # fixes for error in unit test using MagicMock
            raise TypeError(f"'node' must be of type 'Node', not '{type(node)}'!")
        super(NodeContainer, self).__setitem__(node_name, node)

    def __getitem__(self, node_name: str) -> Node:
        try:
            node = super(NodeContainer, self).__getitem__(node_name)
            if isinstance(node, Node) or isinstance(node, MagicMock):  # fixes for error in unit test using MagicMock
                return node
            else:
                raise AttributeError(f"Node {node_name} does not exist!")
        except KeyError as e:
            raise AttributeError(f"Node {e} does not exist!")

    def __setattr__(self, node_name: str, node: Node) -> None:
        self.__setitem__(node_name, node)

    def __delattr__(self, node_name: str) -> None:
        self.__delitem__(node_name)

    def __getattr__(self, node_name: str) -> Node:
        return self.__getitem__(node_name)

    def __str__(self) -> str:
        node_list: str = ", ".join(self.keys())
        return f"Available node names: [{node_list}]\nUse 'nodes.<name>' to access the node.\nExample: 'nodes.{list(self.keys())[0]}'\n"

    def __repr__(self) -> str:
        # give the user a nicely formatted string when he simply types "node" in the CLI
        return self.__str__()
