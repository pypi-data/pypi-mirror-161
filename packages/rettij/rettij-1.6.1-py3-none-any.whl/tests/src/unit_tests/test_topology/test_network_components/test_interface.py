import unittest
from unittest.mock import Mock

from rettij.topology.network_components.interface import Interface


class TestInterface(unittest.TestCase):
    """
    This TestCase contains tests regarding the Interface class.
    """

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        self.executor = Mock()
        self.name = "i0"
        self.channel = Mock()
        self.mac = "aa:bb:cc:dd:ee"
        self.ip_str = "10.1.1.1"
        self.ip_mock = Mock(ip=self.ip_str)
        self.gateway = Mock()
        self.data_rate = "1000.0mbps"

        self.iface = Interface(self.executor, self.name, self.channel, self.mac, self.ip_mock, self.data_rate)

    def test_name(self) -> None:
        """
        Verify that the Interface name can be set, and that too long names raise a ValueError.
        """
        name_new = "i1"
        name_too_long = "i234567891234567"  # 16 chars long (max length: 15 chars)
        self.assertEqual(self.name, self.iface.name)
        self.iface.name = name_new
        self.assertEqual(name_new, self.iface.name)
        with self.assertRaises(ValueError):
            self.iface.name = name_too_long

    def test_channel(self) -> None:
        """
        Verify that the Channel can be set.
        """
        self.assertEqual(self.channel, self.iface.channel)
        new_channel = Mock()
        self.iface.channel = new_channel
        self.assertEqual(new_channel, self.iface.channel)

    def test_data_rate(self) -> None:
        """
        Verify that the data rate can be set.
        """
        self.assertEqual(self.data_rate, str(self.iface.data_rate))
        new_data_rate = Mock()
        self.iface.data_rate = new_data_rate
        self.assertEqual(new_data_rate, self.iface.data_rate)

    def test_ip(self) -> None:
        """
        Verify that the IP address can be set.
        """
        self.assertEqual(self.ip_str, self.iface.ip)
        # TODO the following block still needs to be implemented in the Interface class
        # new_ip = Mock()
        # self.iface.ip = new_ip
        # self.assertEqual(new_ip, self.iface.ip)

    def test_mac(self) -> None:
        """
        Verify that the MAC address can be set.
        """
        self.assertEqual(self.mac, self.iface.mac)
        new_mac = "bb:bb:cc:dd:ee"
        self.iface.mac = new_mac
        self.assertEqual(new_mac, self.iface.mac)

    def test_executor(self) -> None:
        """
        Verify that the NodeExecutor can be set.
        """
        self.assertEqual(self.executor, self.iface.executor)

    def test_str(self) -> None:
        """
        Verify that the Interface has the expected string representation.
        """
        iface_str: str = r"""
                          Interface: i0
                          ------------------------------
                          IP: 10\.1\.1\.1
                          Attributes:
                            channel: .*
                            data_rate: 1000\.0mbps
                            executor: .*
                            ip: 10\.1\.1\.1
                            ip_address_cidr: .*
                            mac: aa:bb:cc:dd:ee
                            name: i0
                          Methods: down\(\), up\(\), utilization\(\)
                          """.replace(
            "                          ", ""
        )  # Remove leading spaces

        self.assertRegex(str(self.iface), iface_str)

    def test_repr(self) -> None:
        """
        Verify that the Interface has the expected __repr__ representation.
        """
        self.assertEqual(str(self.iface), repr(self.iface))
