import unittest

from unittest.mock import Mock

from rettij.topology.network_components.channel import Channel


class TestChannel(unittest.TestCase):
    """
    This TestCase contains tests regarding the Channel class.
    """

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        self.name: str = "c0"
        self.vni: int = 1
        self.data_rate: str = "1000mbps"
        self.delay: str = "10ms"
        self.channel: Channel = Channel(self.name, self.vni, self.data_rate, self.delay)

    def test_node_connection(self) -> None:
        """
        Verify that two Nodes can be connected by a channel.

        Tests:
         - Return values from Channel.connected_node_names_and_data_rates()
         - Error-free execution of Channel.on_node_connect()
        """
        node_name0, node_name1, node_name2 = "n0", "n1", "n2"
        node_data_rate_mock0, node_data_rate_mock1 = Mock(), Mock()
        # connect 1st node to channel
        self.channel.on_node_connect(node_name0, node_data_rate_mock0)
        ret_val = self.channel.connected_node_names_and_data_rates
        # make sure connection worked
        self.assertEqual({node_name0: node_data_rate_mock0}, ret_val)
        # connect 2nd node to channel
        self.channel.on_node_connect(node_name1, node_data_rate_mock1)
        ret_val = self.channel.connected_node_names_and_data_rates
        # make sure connection worked
        self.assertEqual({node_name0: node_data_rate_mock0, node_name1: node_data_rate_mock1}, ret_val)
        # make sure that exception is raised when trying to connect 3rd node to a single channel
        with self.assertRaises(ValueError):
            self.channel.on_node_connect(node_name2, node_data_rate_mock0)

    def test_channel_id(self) -> None:
        """
        Verify that the Channel ID can be read and set.
        """
        self.assertEqual(self.name, self.channel.name)
        new_name: str = "i1"
        self.channel.name = new_name
        self.assertEqual(new_name, self.channel.name)

    def test_channel_vni(self) -> None:
        """
        Verify that the channel VNI can be set, and that faulty VNIs raise ValueErrors.

        Tested:
        - Valid VNI
        - VNI of wrong data type
        - VNI with too high number
        - VNI with negative number
        """
        new_vni_valid = 2
        new_vni_wrong_datatype = "5"
        new_vni_too_big = 16777215 + 1  # max vni + 1
        new_vni_negative = -1

        self.assertEqual(self.vni, self.channel.vni)
        self.channel.vni = new_vni_valid
        self.assertEqual(new_vni_valid, self.channel.vni)
        with self.assertRaises(ValueError):
            # tell mypy to not type check this test as it is intentionally wrong
            self.channel.vni = new_vni_wrong_datatype  # type: ignore
        with self.assertRaises(ValueError):
            self.channel.vni = new_vni_too_big
        with self.assertRaises(ValueError):
            self.channel.vni = new_vni_negative

    def test_delay(self) -> None:
        """
        Verify that the Channel delay can be read and set.
        """
        self.assertEqual(self.delay, self.channel.delay)
        new_delay: str = "20ms"
        self.channel.delay = new_delay
        self.assertEqual(new_delay, self.channel.delay)

    def test_str(self) -> None:
        """
        Verify that the Channel has the expected string representation.
        """
        self.assertEqual(f"Channel: {self.name}", str(self.channel))
