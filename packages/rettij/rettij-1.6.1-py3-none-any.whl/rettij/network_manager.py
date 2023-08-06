import subprocess
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path
from typing import Dict, List, Optional

from rettij.common.constants import RESOURCES_DIR
from rettij.common.data_rate import DataRate
from rettij.common.is_suited_host_system import is_suited_host_system
from rettij.common.logging_utilities import LoggingSetup
from rettij.common.validated_path import ValidatedFilePath
from rettij.exceptions.task_exception import TaskException
from rettij.topology.exec_result import ExecResult
from rettij.topology.network_components.channel import Channel
from rettij.topology.network_components.interface import Interface, ExternalSettingsStore
from rettij.topology.network_components.node import Node
from rettij.topology.node_container import NodeContainer
from rettij.topology.node_executors.node_executor import NodeExecutor


def _select_data_rate(iface: Interface) -> Optional[DataRate]:
    """
    Select the lower data rate between that of the channel and that of the connected interfaces.

    :param iface: Interface
    :return: Selected data rate. May return None if no data rate is set.
    """
    channel: Channel = iface.channel
    connected_node_names_and_data_rates: Dict[str, DataRate] = channel.connected_node_names_and_data_rates

    min_data_rate: Optional[DataRate] = channel.data_rate

    for node_name, node_data_rate in connected_node_names_and_data_rates.items():
        if node_data_rate:  # Skip if the node has no data rate
            if min_data_rate and node_data_rate < min_data_rate:  # Check if the node's data rate is the lowest
                min_data_rate = node_data_rate
            if not min_data_rate:  # If current lowest data rate is "None", use node's data rate as lowest
                min_data_rate = node_data_rate

    return min_data_rate


def _set_connection_parameters(iface: Interface, executor: Optional[NodeExecutor] = None) -> List[str]:
    """
    Set the connection parameters (if present).

    :param iface: VXLAN interface to set the connection parameters for.
    :param executor: (Optional) NodeExecutor the interface is on.
    :return: The setup command.
    """
    parameters_to_set: int = 0

    command: List[str] = ["tc", "qdisc", "replace", "dev", iface.name, "root", "netem"]

    if _select_data_rate(iface):
        command += ["rate", str(_select_data_rate(iface))]
        parameters_to_set += 1

    if iface.channel.delay:
        command += ["delay", iface.channel.delay]
        parameters_to_set += 1

    # tc qdisc replace dev "$iface_id" root netem rate "$data_rate" delay "$delay";
    if parameters_to_set > 0:
        if not executor:
            return command
        else:
            result: ExecResult = executor.execute_command(command, log_error_only=True)

            exit_code: int = int(result.exit_code)
            if exit_code != 0:
                raise TaskException(
                    task=f"VXLAN interface setup for interface {iface} of node {executor.name}",
                    msg=f"Failed to set connection parameters: {result.std_out} | {result.std_out} | {result.api_response}",
                )

    return []


class NetworkManager:
    """
    This class manages all rettij-specific network configuration.
    """

    def __init__(self) -> None:
        """
        Initialize a NetworkManager object.
        """
        self.__logger = LoggingSetup.submodule_logging(self.__class__.__name__)

    def __setup_regular_interface_vxlan(
        self,
        executor: NodeExecutor,
        iface: Interface,
        remote_ext_ip: IPv4Address,
    ) -> bool:
        """
        Set up a VXLAN interface on a node of type 'container' or 'router'.

        :param executor: NodeExecutor to setup the interface on.
        :param iface: VXLAN interface to create.
        :param remote_ext_ip: IP of peer node (e.g. switch) in the Kubernetes overlay network
        """
        self.__logger.debug("########## Setting up regular interface VXLAN tunnel... ##########")

        remote_ext_ip_str: str = remote_ext_ip.compressed  # e.g. 10.0.1.1
        tun_ip_cidr_str: str = iface.ip_address_cidr.compressed  # e.g. 192.168.0.1/24
        vni_str: str = str(iface.channel.vni)
        parent_iface: str = "eth0"  # The Kubernetes network interface is usually eth0

        self.__logger.debug(f"Container: {executor.name}")
        self.__logger.debug(
            f"Interface: {iface.name} | Remote-IP: {remote_ext_ip_str} | Internal-IP: {tun_ip_cidr_str} | MAC: {iface.mac} | VNI: {vni_str}"
        )

        # Usage: setup_vxlan_interface.sh <iface_name> <iface_mac> <remote_ext_ip> <tun_ip_cidr> <vni> <parent_iface>
        result: ExecResult = executor.execute_command(
            [
                "/setup_vxlan_interface.sh",
                iface.name,
                iface.mac,
                remote_ext_ip_str,
                tun_ip_cidr_str,
                vni_str,
                parent_iface,
            ],
            log_error_only=True,
        )

        exit_code: int = int(result.exit_code)
        if exit_code != 0:
            cause_dict = {
                0: "Command execution was successful",
                11: "Wrong number of arguments",
                12: "Validation of MAC address failed",
                13: "Validation of remote IP failed",
                14: "Validation of tunnel interface IP configuration failed",
                15: "Validation of VNI failed",
                16: "Failed to add tunnel adapter",
                17: "Failed to set IP for tunnel adapter",
                18: "Failed to activate tunnel adapter",
            }

            raise TaskException(
                task=f"VXLAN interface setup for interface {iface} of node {executor.name}: ",
                msg=f"{cause_dict.get(exit_code, exit_code)}: {result}",
            )

        _set_connection_parameters(iface, executor)

        self.__logger.debug("########## Finished regular interface VXLAN tunnel setup ##########\n")
        return True

    def __setup_vxlan_bridge_interface(
        self,
        executor: NodeExecutor,
        iface: Interface,
        remote_ext_ip: IPv4Address,
        hub: bool = False,
    ) -> bool:
        """
        Set up a VXLAN interface on a node of type 'switch'.

        :param executor: NodeExecutor to setup the interface on.  Corresponding RemoteContainer of the switch node
        :param iface: VXLAN interface
        :param remote_ext_ip: IP of peer node in the Kubernetes overlay network
        :param hub: If False (standard), this bridge behaves like a switch; otherwise it acts as a hub
        """
        bridge_name = "vxlan-bridge"
        vni_str: str = str(iface.channel.vni)
        parent_iface: str = "eth0"  # The Kubernetes network interface is usually eth0

        self.__logger.debug("########## Setting up simple-switch VXLAN tunnel... ##########")
        self.__logger.debug(f"Container: {executor.name}")
        self.__logger.debug(f"Interface: {iface.name} | MAC: {iface.mac} | VNI: {vni_str} | Bridge: {bridge_name}")

        if hub:
            ageing_time = "0"  # this makes a linux bridge behave like a hub
        else:
            ageing_time = ""  # empty string if we don't want to set this parameter for the following shell script

        # Usage: setup_vxlan_brigde_interface.sh <bridge_name> <iface_name> <remote_ext_ip> <vni> <parent_iface> [<ageing_time>]
        result: ExecResult = executor.execute_command(
            [
                "/setup_vxlan_bridge_interface.sh",
                bridge_name,
                iface.name,
                remote_ext_ip.compressed,
                vni_str,
                parent_iface,
                ageing_time,
            ],
            log_error_only=True,
        )

        exit_code: int = int(result.exit_code)

        if exit_code != 0:
            cause_dict = {
                0: "Command execution was successful",
                11: "Wrong number of arguments",
                12: "Validation of remote IP failed",
                13: "Validation of VNI failed",
                14: "Creation of new bridge failed",
                15: "Failed to activate bridge",
                16: "Failed to add tunnel adapter",
                17: "Failed to add tunnel adapter to bridge",
                18: "Failed to activate tunnel adapter",
            }

            raise TaskException(
                task=f"VXLAN bridge interface setup for interface {iface} of node {executor.name}",
                msg=f"{cause_dict.get(exit_code, exit_code)}: {result}",
            )

        _set_connection_parameters(iface, executor)

        self.__logger.debug("########## Finished simple-switch VXLAN tunnel setup ##########\n")
        return True

    def __remove_interface(self, node: Node, iface: Interface) -> bool:
        result = node.executor.execute_command(["ip", "link", "delete", iface.name], log_error_only=True)

        if result.exit_code == 0:
            self.__logger.debug(f"Interface {iface} successfully removed from node {node.name}.")
            return True
        else:
            raise TaskException(
                task=f"Interface removal for interface {iface} of node {node.name}",
                msg=f"{result.exit_code}: {result.std_out} | {result.std_out} | {result.api_response}",
            )

    def __setup_host_interface_vxlan(
        self,
        iface: Interface,
        remote_ext_ip: IPv4Address,
    ) -> bool:
        """
        Set up an ethernet connection from the host to the simulation network via a VXLAN interface.

        Works by creating a VXLAN interface connected to a peer Node in Kubernetes.
        Setup and teardown are automated if the host system is compatible.
        Otherwise, it will only print the commands.

        :param iface: Name for the simulation VXLAN interface
        :param remote_ext_ip: IP of peer node in the Kubernetes overlay network
        """
        remote_ext_ip_str: str = remote_ext_ip.compressed  # e.g. 10.0.1.1
        tun_ip_cidr_str: str = iface.ip_address_cidr.compressed  # e.g. 192.168.0.1/24
        vni_str: str = str(iface.channel.vni)
        parent_iface: str = "cni0"  # The Kubernetes host network interface is usually cni0

        setup_commands: List[List] = [
            [
                "sudo",
                ValidatedFilePath(Path(RESOURCES_DIR) / "scripts" / "setup_vxlan_interface.sh"),
                iface.name,
                iface.mac,
                remote_ext_ip_str,
                tun_ip_cidr_str,
                vni_str,
                parent_iface,
            ],
        ]

        # _set_connection_parameters may return empty list, which lead to errors in subprocess
        connection_parameter_command: List[str] = _set_connection_parameters(iface)
        if connection_parameter_command:
            setup_commands.append(connection_parameter_command)

        remove_command: List[str] = [
            "sudo",
            ValidatedFilePath(Path(RESOURCES_DIR) / "scripts" / "remove_host_vxlan_interface.sh"),
            iface.name,
        ]

        # Store the removal command in the interface, so it can be called later during teardown
        iface.remove_commands = [remove_command]

        if is_suited_host_system():
            for command in setup_commands:
                setup_result: subprocess.CompletedProcess = subprocess.run(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                self.__logger.debug(setup_result)
                if setup_result.returncode != 0:
                    raise RuntimeError(str(setup_result))

        else:
            print("Run the commands below to SETUP up the VXLAN interface:")
            for command in setup_commands:
                print(" ".join(command))
            print("Run the script below to REMOVE up the VXLAN interface:")
            print(" ".join(remove_command))

        return True

    def __setup_host_vxlan_bridge_interface(
        self, iface: Interface, remote_ext_ip: IPv4Address, channel: Channel, node: Node
    ) -> None:
        """
        Set up an ethernet bridge between the simulation VXLAN interface, and a (physical) host NIC.

        Works by creating a VXLAN interface connected to a peer Node in Kubernetes, an ethernet bridge between the VXLAN interface and a host NIC, and corresponding iptables forwarding rules.
        Setup and teardown are automated if the host system is compatible.
        Otherwise, it will only print the commands.

        :param iface: Name for the simulation VXLAN interface
        :param remote_ext_ip: IP of peer node in the Kubernetes overlay network
        :param channel: Channel between the simulation VXLAN interface, and the peer node interface
        :param node: Host simulation Node
        """
        bridge_name: str = f"vxlan-bridge-{channel.name}"
        vni_str: str = str(iface.channel.vni)
        parent_iface: str = "cni0"  # The Kubernetes host network interface is usually cni0
        ageing_time: str = "0"  # always act like a hub, since we only want a transparent bridge, not a switch

        remote_ext_ip_str: str = remote_ext_ip.compressed  # e.g. 10.0.1.1

        node_is_suited_host_system: bool = is_suited_host_system()

        setup_commands: List[List[str]] = []
        remove_commands: List[List[str]] = []

        if not isinstance(iface.external, ExternalSettingsStore):
            raise AttributeError("ExternalSettingsStore required.")

        bridge_setup_command: List[str] = [
            "sudo",
            ValidatedFilePath(Path(RESOURCES_DIR) / "scripts" / "setup_vxlan_bridge_interface.sh"),
            bridge_name,
            iface.name,
            remote_ext_ip_str,
            vni_str,
            parent_iface,
            ageing_time,
        ]

        setup_commands.append(bridge_setup_command)
        setup_commands.append(["sudo", "ip", "link", "set", "dev", iface.external.interface, "master", bridge_name])

        # _set_connection_parameters may return empty list, which lead to errors in subprocess
        connection_parameter_command: List[str] = _set_connection_parameters(iface)
        if connection_parameter_command:
            setup_commands.append(connection_parameter_command)

        for network in iface.external.networks:
            setup_commands.append(
                [
                    "sudo",
                    "iptables",
                    "-A",
                    "FORWARD",
                    "-s",
                    network.compressed,
                    "-d",
                    network.compressed,
                    "-j",
                    "ACCEPT",
                    "-m",
                    "comment",
                    "--comment",
                    '"rettij host bridge"',
                ]
            )

        remove_commands.append(["sudo", "ip", "link", "del", iface.name])
        remove_commands.append(["sudo", "ip", "link", "set", "dev", iface.external.interface, "nomaster"])
        remove_commands.append(["sudo", "ip", "link", "del", bridge_name])
        for network in iface.external.networks:
            remove_commands.append(
                [
                    "sudo",
                    "iptables",
                    "-D",
                    "FORWARD",
                    "-s",
                    network.compressed,
                    "-d",
                    network.compressed,
                    "-j",
                    "ACCEPT",
                    "-m",
                    "comment",
                    "--comment",
                    '"rettij host bridge"',
                ]
            )

        # Add some additional setup and teardown commands that require reading information from the host system.
        # Only works if the host system is suited for the automated setup.
        if node_is_suited_host_system:
            # Get NIC information
            ip_cmd_result: subprocess.CompletedProcess = subprocess.run(
                ["ip", "address", "show", iface.external.interface],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if ip_cmd_result.returncode != 0:
                raise RuntimeError(str(ip_cmd_result))

            # Split the output into a list of strings at each whitespace
            ip_cmd_stdout_split: List[str] = ip_cmd_result.stdout.decode().split()

            # Get the index of the string 'mtu' and retrieve the value at the next index to use in the commands
            mtu: str = ip_cmd_stdout_split[ip_cmd_stdout_split.index("mtu") + 1]

            # Set the MTU to 1400 to work with rettij's VXLAN tunnels
            setup_commands.append(["sudo", "ip", "link", "set", "dev", iface.external.interface, "mtu", "1400"])

            # Reset the MTU after the simulation has finished
            remove_commands.append(["sudo", "ip", "link", "set", "dev", iface.external.interface, "mtu", mtu])

            # Get the indices of the every 'inet' or 'inet6' string and retrieve the value at the next index to use in the commands
            ip_list: List[str] = []
            for i in range(0, len(ip_cmd_stdout_split)):
                if ip_cmd_stdout_split[i] == "inet" or ip_cmd_stdout_split[i] == "inet6":
                    ip_list.append(ip_cmd_stdout_split[i + 1])

            # Remove all ips from the interface
            setup_commands.append(["sudo", "ip", "address", "flush", "dev", iface.external.interface])

            # Re-add the ips after the simulation has finished
            for ip in ip_list:
                remove_commands.append(["sudo", "ip", "address", "add", ip, "dev", iface.external.interface])

        # Store the removal command in the interface, so it can be called later during teardown
        iface.remove_commands = remove_commands

        if node_is_suited_host_system:
            for command in setup_commands:
                setup_result: subprocess.CompletedProcess = subprocess.run(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                self.__logger.debug(setup_result)
                if setup_result.returncode != 0:
                    raise RuntimeError(str(setup_result))
        else:
            print("Run the following commands to setup the rettij bridge configuration:")
            for command in setup_commands:
                print(" ".join(command))

            print("Run the following commands to remove the rettij bridge configuration:")
            for command in remove_commands:
                print(" ".join(command))

    def connect_node_neighbours(self, node: Node, nodes: NodeContainer, rebuild_tunnel: bool = False) -> None:
        """
        Create one-way VXLAN tunnels to all neighbours of a node.

        :param node: Node to create VXLAN tunnels for.
        :param nodes: NodeContainer object with all simulation Nodes.
        :param rebuild_tunnel: Set True to also rebuild the one-way tunnels from the neighbouring nodes. Required if the node was restarted during the simulation run.
        :return bool: True if successful.
        """
        # region Validate inputs
        if not isinstance(node, Node):
            raise ValueError("Parameter 'node' must be of type 'Node'!")

        if not isinstance(nodes, NodeContainer):
            raise ValueError("Parameter 'nodes' must be of type 'NodeContainer'!")

        # endregion

        # region Copy interface setup script to the container
        if node.node_type in ["container", "router"]:
            node.executor.copy_file_to_node(
                ValidatedFilePath.join_paths(RESOURCES_DIR, "scripts", "setup_vxlan_interface.sh")
            )
        if node.node_type in ["switch", "hub", "router"]:
            node.executor.copy_file_to_node(
                ValidatedFilePath.join_paths(RESOURCES_DIR, "scripts", "setup_vxlan_bridge_interface.sh")
            )
        # endregion

        # region Create VXLAN tunnel for each interface
        for iface_id, iface in node.ifaces.items():

            # `iface.channel.connected_node_names` always contains two node names, as channels are strictly point-to-point connections.
            # Therefore, if we remove our own name from that list, we are left with the name of the neighbouring node.
            channel_nodes = list(iface.channel.connected_node_names_and_data_rates.keys()).copy()
            channel_nodes.remove(node.name)
            neighbour: Node = nodes[channel_nodes[0]]
            neighbour_ip: IPv4Address = neighbour.executor.ip

            self.__vxlan_setup(node, iface, neighbour_ip)

            # Also rebuild the tunnel from the neighboring node
            if rebuild_tunnel:
                for neighbour_iface_id, neighbour_iface in neighbour.ifaces.items():
                    if neighbour_iface.channel == iface.channel:
                        self.__remove_interface(neighbour, neighbour_iface)
                        self.__vxlan_setup(neighbour, neighbour_iface, node.executor.ip)
                        break

        # endregion

        if node.routes:
            for route in node.routes:
                if route.network == IPv4Network("0.0.0.0/0"):
                    # Add the gateway's ip-address for this container's default route
                    node.executor.execute_command(["ip", "route", "del", "default"], log_error_only=True)
                    node.executor.execute_command(
                        ["ip", "route", "add", "default", "via", route.gateway.compressed], log_error_only=True
                    )
                elif route.metric:
                    node.executor.execute_command(
                        [
                            "ip",
                            "route",
                            "add",
                            route.network.compressed,
                            "via",
                            route.gateway.compressed,
                            "metric",
                            str(route.metric),
                        ],
                        log_error_only=True,
                    )
                else:
                    node.executor.execute_command(
                        ["ip", "route", "add", route.network.compressed, "via", route.gateway.compressed],
                        log_error_only=True,
                    )
                self.__logger.debug("Gateway of container " + node.name + " set to " + route.gateway.compressed)

    def __vxlan_setup(self, node: Node, iface: Interface, neighbour_ip: IPv4Address) -> None:
        if node.node_type in ["container", "router"]:
            self.__setup_regular_interface_vxlan(node.executor, iface, neighbour_ip)
        elif node.node_type == "switch":
            self.__setup_vxlan_bridge_interface(node.executor, iface, neighbour_ip)
        elif node.node_type == "hub":
            self.__setup_vxlan_bridge_interface(node.executor, iface, neighbour_ip, hub=True)
        elif node.node_type == "host":
            if iface.external:
                self.__setup_host_vxlan_bridge_interface(iface, neighbour_ip, iface.channel, node)
            else:
                self.__setup_host_interface_vxlan(iface, neighbour_ip)
        else:
            raise NotImplementedError(
                "Node types other than 'container', 'router', 'switch', 'hub' and 'host' are not yet implemented!."
            )
