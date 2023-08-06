import unittest
from unittest.mock import MagicMock

from rettij.topology.node_container import NodeContainer


class TestNodeContainer(unittest.TestCase):
    """
    This TestCase contains tests regarding the NodeContainer class.
    """

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        self.n0 = MagicMock()
        self.n1 = MagicMock()
        self.nodes = {"n0": self.n0, "n1": self.n1}
        self.node_container = NodeContainer(self.nodes)  # type: ignore  # expects Nodes in Dict, but gets MagicMock

    def test_attr(self) -> None:
        """
        Verify that Nodes can be accessed through the NodeContainer.
        """
        # the attributes node_container.n0 and node_container.n1 are added at runtime, so we need to tell PyCharm/mypy to ignore unresolved references
        # noinspection PyUnresolvedReferences
        self.assertEqual(self.n0, self.node_container.n0)  # type: ignore
        # noinspection PyUnresolvedReferences
        self.assertEqual(self.n1, self.node_container.n1)  # type: ignore

    def test_str(self) -> None:
        """
        Verify that the NodeContainer has the expected string representation.
        """
        expected_str = "Available node names: [n0, n1]"
        self.assertIn(expected_str, str(self.node_container))

    def test_repr(self) -> None:
        """
        Verify that the NodeContainer has the expected __repr__ representation.
        """
        self.assertEqual(str(self.node_container), repr(self.node_container))
