from __future__ import annotations

from ipaddress import IPv4Address, IPv4Interface, IPv4Network
from typing import Dict, Optional, List, Final

from rettij.common.constants import RESOURCES_DIR
from rettij.common.data_rate import DataRate
from rettij.common.logging_utilities import LoggingSetup
from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.exec_result import ExecResult
from rettij.topology.network_components.channel import Channel
from rettij.topology.node_executors.node_executor import NodeExecutor


class ExternalSettingsStore:
    """
    This class stores setting regarding the host bridge.
    """

    def __init__(self, interface: str, networks: List[str]):
        """
        Initialize an ExternalSettingsStore object.

        :param interface: Name of the host network interface to bridge to.
        :param networks: IP ranges of allowed networks. Use 0.0.0.0/0 to allow all (SECURITY RISK!).
        """
        self.interface: str = interface

        self.networks: List[IPv4Network] = []
        for i, network_str in enumerate(networks):
            self.networks.insert(i, IPv4Network(network_str))


class Interface:
    """
    This class represents a network interface attached to the simulation network.
    """

    # otherwise network interface names get too long; see https://stackoverflow.com/a/53478768
    __MAX_ID_LENGTH = 15

    def __init__(
        self,
        executor: NodeExecutor,
        name: str,
        channel: Channel,
        mac: str,
        iface_address: IPv4Interface = IPv4Interface("0.0.0.0/0"),
        data_rate: Optional[str] = None,
        external: Optional[ExternalSettingsStore] = None,
    ):
        """
        Initialize an Interface object.

        :param executor: NodeExecutor object of the parent Node.
        :param name: Name for the interface.
        :param channel: Channel which the interface is connected to.
        :param mac: MAC address for the interface.
        :param iface_address: IP address (CIDR) for the interface.
        :param data_rate: Data rate for the interface.
        """
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)

        self.name: str = name
        self.channel: Channel = channel
        self.ip_address_cidr = iface_address
        self.mac = mac

        self.data_rate: Optional[DataRate] = DataRate(data_rate) if data_rate else None  # type: ignore

        self.external: Optional[ExternalSettingsStore] = external

        # Set the NodeExecutor, used for executing commands on the Node.
        # A private attribute without a setter, since it would not be changed after initialization.
        self.__executor: Final[NodeExecutor] = executor

        self.remove_commands: List[List[str]] = []

        # Reference: https://www.askpython.com/python/examples/find-all-methods-of-class
        public_attributes_list = [
            attribute
            for attribute in dir(self.__class__)
            if not (attribute.startswith("__") or attribute.startswith("_"))
        ]
        self.public_property_list = [
            attribute for attribute in public_attributes_list if not callable(getattr(self.__class__, attribute))
        ]
        self.public_method_list = [
            attribute for attribute in public_attributes_list if callable(getattr(self.__class__, attribute))
        ]

    @property
    def name(self) -> str:
        """
        Retrieve the Interface name.

        :return: Interface name.
        """
        return self.__iface_name

    @name.setter
    def name(self, name: str) -> None:
        """
        Set the Interface name.

        Verifies that the Interface name length does not exceed the maximum length.
        Only meant for internal use, as the IfaceContainer will not be updated.

        :param name: New name for the Interface.
        """
        if len(name) > Interface.__MAX_ID_LENGTH:
            raise ValueError(f"Length of interface id {name} too long (max. {Interface.__MAX_ID_LENGTH})")
        self.__iface_name = name

    @property
    def channel(self) -> Channel:
        """
        Retrieve the Channel which the Interface is connected to.

        :return: Connected Channel object.
        """
        return self.__channel

    @channel.setter
    def channel(self, channel: Channel) -> None:
        """
        Set the connected Channel.

        Only meant for internal use, as the connected Channel is only used during Node deployment.
        TODO: Allow change in live system after deployment.

        :param channel: New Channel to connect to.
        """
        self.__channel: Channel = channel

    @property
    def data_rate(self) -> DataRate:
        """
        Retrieve the Interface data rate.

        :return: DataRate object.
        """
        return self.__data_rate

    @data_rate.setter
    def data_rate(self, data_rate: DataRate) -> None:
        """
        Set the Interface data rate.

        Only meant for internal use, as the data rate is only used during Node deployment.
        TODO: Allow change in live system after deployment.

        :param data_rate: New DataRate object.
        """
        self.__data_rate: DataRate = data_rate

    @property
    def ip_address_cidr(self) -> IPv4Interface:
        """
        Retrieve the Interface IP address with netmask (CIDR).

        :return: Interface IP address with netmask (CIDR).
        """
        return self.__ip_address_cidr

    @ip_address_cidr.setter
    def ip_address_cidr(self, ip_address_cidr: IPv4Interface) -> None:
        """
        Set the Interface IP address with netmask (CIDR).

        Only meant for internal use, as the IP address is only used during Node deployment.
        TODO: Allow change in live system after deployment.

        :param ip_address_cidr: IPv4Interface object.
        """
        self.__ip_address_cidr = ip_address_cidr

    @property
    def ip(self) -> IPv4Address:
        """
        Retrieve the Interface IP address.

        :return: Interface IP address.
        """
        return self.ip_address_cidr.ip

    @property
    def mac(self) -> str:
        """
        Retrieve the Interface MAC address.

        :return: MAC address string.
        """
        return self.__mac

    @mac.setter
    def mac(self, mac: str) -> None:
        """
        Set the Interface MAC address.

        Only meant for internal use, as the MAC address is only used during Node deployment.
        TODO: Allow change in live system after deployment.

        :param mac: MAC address string.
        """
        self.__mac = mac

    @property
    def executor(self) -> NodeExecutor:
        """
        Retrieve the NodeExecutor object of the parent Node.

        :return:  NodeExecutor object of the parent Node
        """
        # TODO: Currently this getter is still used from the outside. This should be removed in the future as all
        #       "control operations" should be implemented in the Node / Interface class at some point. Currently,
        #       this is not the case for everything, though.
        return self.__executor

    def down(self) -> None:
        """
        Disable the Interface.
        """
        self.__executor.execute_command(f"ip link set dev {self.name} down")

    def up(self) -> None:
        """
        Enable the Interface.
        """
        self.__executor.execute_command(f"ip link set dev {self.name} up")

    def utilization(self) -> Dict[str, int]:
        """
        Retrieve the utilization of the interface over one second (kB/s).

        :return: Dictionary of utilization
            - 'rx' (int): Received bytes
            - 'tx' (int): Transmitted bytes
            - 'total' (int): Total bytes
        """
        # Check if the utilization script is present on the node, copy it if not
        check_script_result: ExecResult = self.__executor.execute_command(
            ["/usr/bin/which", "/get_interface_utilization.sh"], log_error_only=True
        )
        if check_script_result.exit_code == 1:
            self.__executor.copy_file_to_node(
                ValidatedFilePath.join_paths(RESOURCES_DIR, "scripts", "get_interface_utilization.sh")
            )
        elif check_script_result.exit_code != 0:
            raise RuntimeError(f"{check_script_result}")

        # Retrieve interface utilization
        get_utilization_result: ExecResult = self.__executor.execute_command(
            ["/get_interface_utilization.sh", str(self.name)], log_error_only=True
        )
        if get_utilization_result.exit_code != 0:
            raise RuntimeError(f"{get_utilization_result}")
        utilization = get_utilization_result.std_out.split(",")
        return {
            "rx": int(utilization[0]),
            "tx": int(utilization[1]),
            "total": int(utilization[2]),
        }

    def __str__(self) -> str:
        """
        Return a string representation.

        Looks like this::

            Interface: i0
            ------------------------------
            IP: 10.1.1.1
            Attributes:
              channel: Channel: c0
              data_rate: None
              executor: <rettij.topology.node_executors.kubernetes_pod_executor.KubernetesPodExecutor object at 0x7f57409543d0>
              ip: 10.1.1.1
              ip_address_cidr: 10.1.1.1/24
              mac: 1A:2B:3C:4D:5E:01
              name: i0
            Methods: down(), up(), utilization()

        :return: String representation.
        """
        attributes_str = "\n".join([f"  {prop}: {self.__getattribute__(prop)}" for prop in self.public_property_list])

        return f"""
            Interface: {self.name}
            ------------------------------
            IP: {self.ip}
            Attributes:\n{attributes_str}
            Methods: {'(), '.join(self.public_method_list)}()
            """.replace(
            "\n            ", "\n"
        )  # Remove the 12 leading spaces caused by the text block

    def __repr__(self) -> str:
        return self.__str__()
