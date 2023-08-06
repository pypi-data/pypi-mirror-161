from __future__ import annotations

import re
from enum import Enum
from ipaddress import IPv4Address
from pathlib import Path
from typing import Dict, Any, Type, List, Optional, Union

from rettij.commands.command import Command
from rettij.commands.open_shell_command import OpenShellCommand
from rettij.commands.ping_command import PingCommand
from rettij.commands.put_file_command import PutFileCommand
from rettij.commands.retrieve_file_command import RetrieveFileCommand
from rettij.commands.run_command import RunCommand
from rettij.commands.stop_command import StopCommand
from rettij.common.file_permissions import FilePermissions
from rettij.common.logging import monitoring_logging
from rettij.common.logging_utilities import LoggingSetup
from rettij.common.validated_path import ValidatedFilePath, ValidatedDirPath
from rettij.topology.iface_container import IfaceContainer
from rettij.topology.network_components.channel import Channel
from rettij.topology.network_components.interface import Interface
from rettij.topology.network_components.route import Route
from rettij.topology.node_configurations.kubernetes_pod_config import KubernetesPodConfig
from rettij.topology.node_configurations.node_config import NodeConfig
from rettij.topology.node_executors.node_executor import NodeExecutor


class NodeStatus(Enum):
    """
    This class contains an enumeration for the different Node states.

    Available states:
    - DOWN
    - UP
    - STARTING
    - STOPPING
    """

    DOWN = 0
    UP = 1
    STARTING = 2
    STOPPING = 3


class Node:
    """
    This class represents a simulation node.
    """

    __VALID_NODE_TYPES = ("container", "vm", "host", "router", "switch", "hub")

    # rfc1035/rfc1123 subdomain (DNS_SUBDOMAIN)
    # For an explanation, see https://gitlab.com/frihsb/rettij/-/issues/91#note_603046450
    _NAME_PATTERN: re.Pattern = re.compile(
        r"^(([a-z0-9]|[a-z0-9][a-z0-9\-]{0,61}[a-z0-9])\.){0,3}([a-z0-9]|[a-z0-9][a-z0-9\-]{0,61}[a-z0-9])$"
    )

    def __init__(
        self,
        executor_type: Type[NodeExecutor],
        name: str,
        node_type: str,
        executor_config: NodeConfig,
        custom_config: dict = None,
        mosaik_configuration: Dict[str, Any] = None,
    ):
        """
        Initialize a Node object.

        :param executor_type: Class of the NodeExecutor. Available executor classes: KubernetesPodExecutor, HostExecutor, DummyExecutor.
        :param name: Name of the Node.
        :param node_type: Type of the Node. Available types: "container", "vm", "host", "router", "switch", "hub".
        :param executor_config: Executor-specific configuration object.
        :param custom_config: Custom configuration object. May contain any user-defined information for later use in scenarios.
        :param mosaik_configuration: Initial co-simulation data.
        """
        self.__logger = LoggingSetup.submodule_logging(self.__class__.__name__)
        self.__name: str = name
        self.__ifaces = IfaceContainer()
        self._routes: List[Route] = []
        self.node_type: str = node_type
        self.executor_config: NodeConfig = executor_config
        self.custom_config: Dict = custom_config if custom_config else {}
        if mosaik_configuration is None:
            mosaik_configuration = {}
        self.mosaik_data: Dict[str, Any] = mosaik_configuration.get("mosaik_data", {})
        self.mosaik_model: Dict[str, Any] = mosaik_configuration.get("mosaik_model", "")
        self.status: Enum = NodeStatus.DOWN
        self.executor: NodeExecutor = executor_type(name)

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

    def run(self, shell_cmd: Union[str, List[str]], detached: bool = False, exec_now: bool = True) -> Command:
        """
        Execute a shell command in the Node.

        :param shell_cmd: Command in string or exec form (e.g. ["ip", "-a"])
        :param detached: If 'True', run the command asynchronously / in the background, meaning execution will not wait for the command to finish. Otherwise, the execution will be blocked until the command execution is finished. Default: 'False'.
        :param exec_now: Execute the command immediately if 'True'. Else, return the Command object without executing it. Default: 'True'.
        :return: ExecuteScriptCommand object.
        """
        cmd = RunCommand(self.executor, shell_cmd, detached=detached)
        if exec_now:
            cmd.execute(0, {})
        return cmd

    def shell(self, exec_now: bool = True) -> Command:
        """
        Open an interactive shell to the Node.

        If a shell cannot be opened, this will log a warning, but return the Command with exit code 0 as to not crash the simulation!

        :param exec_now: Execute the command immediately if 'True'. Else, return the Command object without executing it. Default: 'True'.
        :return: OpenShellCommand object.
        """
        cmd = OpenShellCommand(self.executor, self.name)
        if exec_now:
            cmd.execute(0, {})
        return cmd

    def ping(self, target: str, detached: bool = False, exec_now: bool = True, **kwargs: Any) -> Command:
        """
        Run a ping from the Node to the target.

        :param target: Target ip address or hostname
        :param detached: If 'True', run the command asynchronously / in the background, meaning execution will not wait for the command to finish. Otherwise, the execution will be blocked until the command execution is finished. Default: 'False'.
        :param exec_now: Execute the command immediately if 'True'. Else, return the Command object without executing it. Default: 'True'.
        :param kwargs: Optional parameters for the linux 'ping' command:
          - 'a' - use audible ping
          - 'A' - use adaptive ping
          - 'B' - sticky source address
          - 'c' - stop after <count> replies
          - 'D' - print timestamps
          - 'd' - use SO_DEBUG socket option
          - 'f' - flood ping
          - 'h' - print help and exit
          - 'I' - either interface name or address
          - 'i' - seconds between sending each packet
          - 'L' - suppress loopback of multicast packets
          - 'l' - send <preload> number of packages while waiting replies
          - 'm' - tag the packets going out
          - 'M' - define mtu discovery, can be one of <do|dont|want>
          - 'n' - no dns name resolution
          - 'O' - report outstanding replies
          - 'p' - contents of padding byte
          - 'q' - quiet output
          - 'Q' - use quality of service <tclass> bits
          - 's' - use <size> as number of data bytes to be sent
          - 'S' - use <size> as SO_SNDBUF socket option value
          - 't' - define time to live
          - 'U' - print user-to-user latency
          - 'v' - verbose output
          - 'V' - print version and exit
          - 'w' - reply wait <deadline> in seconds
          - 'W' - time to wait for response in seconds

        :return: PingCommand object.
        """
        cmd = PingCommand(self.executor, IPv4Address(target), detached=detached, **kwargs)
        if exec_now:
            cmd.execute(0, {})
        return cmd

    def copy_file_from_node(
        self, src_file_path: str, dst_dir: Union[str, ValidatedDirPath, Path] = "", exec_now: bool = True
    ) -> Command:
        """
        Copy a file from the Node to the local machine.

        :param src_file_path: Source path on the Node.
        :param dst_dir: Destination directory path on the local machine.
        :param exec_now: Execute the command immediately if 'True'. Else, return the Command object without executing it. Default: 'True'.
        :return: RetrieveFileCommand object.
        """
        cmd = RetrieveFileCommand(self.executor, src_file_path, str(dst_dir))
        if exec_now:
            cmd.execute(0, {})
        return cmd

    def copy_file_to_node(
        self,
        src_file_path: Union[str, ValidatedFilePath, Path],
        dst_dir: str = "/",
        file_permissions: FilePermissions = None,
        exec_now: bool = True,
    ) -> Command:
        """
        Copy a file from the local machine to the Node.

        :param src_file_path: Source path on the local machine.
        :param dst_dir: Destination directory path on the Node.
        :param file_permissions: Target file permissions representation.
        :param exec_now: Execute the command immediately if 'True'. Else, return the Command object without executing it. Default: 'True'.
        :return: PutFileCommand object.
        """
        src_file_path = ValidatedFilePath(src_file_path)
        cmd = PutFileCommand(self.executor, src_file_path, dst_dir, file_permissions)
        if exec_now:
            cmd.execute(0, {})
        return cmd

    def shutdown(self) -> None:
        """
        Shut down the Node.

        DOES NOT HAVE PERSISTENCE. ALL DATA ON THE NODE WILL BE LOST.
        """
        print(f"Shutting down node {self.name}... (not actually, this is only mocked for now!)")

    def reboot(self) -> None:
        """
        Reboot the Node.

        DOES NOT HAVE PERSISTENCE. ALL DATA ON THE NODE WILL BE LOST.
        """
        print(f"Rebooting node {self.name}... (not actually, this is only mocked for now!)")

    def stop_detached(self, command: Command, exec_now: bool = True) -> Command:
        """
        Stop an asynchronously started (detached) process on the Node that was started with 'detached = True'.

        :param command: Command object received from the command starting the detached process.
        :param exec_now: Execute the command immediately if 'True'. Else, return the Command object without executing it. Default: 'True'.
        :return: StopCommand object.
        """
        cmd = StopCommand(self.executor, self.executor.stop_detached, command)
        if exec_now:
            cmd.execute(0, {})
        return cmd

    @property
    def name(self) -> str:
        """
        Retrieve the Node name.

        :return: Node name.
        """
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        """
        Set the Node name.

        Verifies that the Node name length does not exceed the maximum length.
        Only meant for internal use, as the NodeContainer will not be updated.

        :param name: New name for the Node.
        """
        if not re.match(pattern=self._NAME_PATTERN, string=name):
            raise ValueError(
                f"Invalid name for Node {name}. Node names must be 'rfc1035/rfc1123 subdomain (DNS_SUBDOMAIN)' compliant (refer to https://github.com/kubernetes/community/blob/master/contributors/design-proposals/architecture/identifiers.md#definitions)."
            )
        self.__name = name

    def get_data(self, keys: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Read attributes from the Node.

        Attributes are read from the Node's executor (live system) and  written to the Node.data variable.

        :param keys: (Optional) Attribute identifiers. If not set, all attributes are returned.
        :return: Key-value pairs stored in `Node.data`. Structure:

            .. code-block:: python

                "<attribute name>": {
                    "<mosaik source entity>": "<attribute value>",  # can also be a list, dict etc.
                },

        """
        self.mosaik_data.update(self.executor.read_values(keys))
        return self.mosaik_data

    def set_data(self, inputs: Dict[str, Dict[str, Any]]) -> None:
        """
        Write attributes to the Node.

        Attributes are written to the Node's executor (live system) and the Node.data variable.

        :param inputs: Key-value pairs to be written. Structure:

            .. code-block:: python

                "<attribute name>": {
                    "<mosaik source entity>": "<attribute value>",  # can also be a list, dict etc.
                },

        """
        self.executor.write_values(inputs)
        # self.data.update(inputs)

    def initiate_executor(self, **kwargs: Any) -> None:
        """
        Create the Executor for the Node.

        :param kwargs: Executor-specific arguments.
        """
        kwargs["node"] = self
        executor_config: Any = self.executor.generate_config(**kwargs)
        self.executor.initialize(**executor_config)

    @property
    def node_type(self) -> str:
        """
        Retrieve the Node type.

        :return: Node type string.
        """
        return self.__node_type

    @node_type.setter
    def node_type(self, node_type: str) -> None:
        """
        Set the Node type.

        Verifies that the Node type is valid.
        Only meant for internal use, as the type is only used during Node deployment.

        :param node_type: New type for the Node.
        """
        if node_type not in Node.__VALID_NODE_TYPES:
            raise ValueError(
                "Invalid node type set: '{}'. Possible values: {}".format(node_type, ", ".join(Node.__VALID_NODE_TYPES))
            )
        self.__node_type: str = node_type

    @property
    def executor_config(self) -> NodeConfig:
        """
        Retrieve the executor-specific Node configuration object.

        :return: Node configuration object.
        """
        return self.__config

    @executor_config.setter
    def executor_config(self, config: KubernetesPodConfig) -> None:
        """
        Set the executor-specific Node configuration object.

        Only meant for internal use, as the Node configuration is only used during Node deployment.

        :return: New Node configuration object.
        """
        self.__config: KubernetesPodConfig = config

    @property
    def ifaces(self) -> IfaceContainer:
        """
        Retrieve the container with the Node's network interfaces.

        :return: Container with the Node's interfaces.
        """
        return self.__ifaces

    @property
    def iface(self) -> IfaceContainer:
        """
        Retrieve the container with the Node's network interfaces.

        Alternative signature to 'Node.ifaces'.

        :return: Container with the Node's interfaces.
        """
        return self.ifaces

    @property
    def routes(self) -> List[Route]:
        """
        Retrieve a list of the Node's network routes.

        :return: List of the Node's network routes.
        """
        return self._routes

    @routes.setter
    def routes(self, routes: List[Route]) -> None:
        """
        Set the Node's network routes.

        Only meant for internal use, as the list of routes is only used during Node deployment.

        :param routes: List of new routes.
        """
        self._routes = routes

    @property
    def executor(self) -> NodeExecutor:
        """
        Retrieve the Node's executor object.

        :return: Node's executor object.
        """
        return self.__executor

    @executor.setter
    def executor(self, executor: NodeExecutor) -> None:
        """
        Set the Node's executor.

        Only meant for internal use, as the executor cannot be changed during simulation.

        :param executor: NodeExecutor object.
        """
        self.__executor: NodeExecutor = executor

    # TODO add remove_interface-method
    def add_interface(self, channel: Channel, iface: Interface) -> None:
        """
        Add an Interface to the Node.

        This currently has no effect if run in the rettij CLI (at least until the node is rebooted) and thus should only
        be used internally by rettij for now, until adding interfaces to the live system is implemented.

        TODO: This should be extended to do so.

        :param channel: Channel to connect the Interface to.
        :param iface: Interface to add to the Node.
        """
        channel.on_node_connect(self.name, iface.data_rate)
        self.__ifaces[iface.name] = iface

    @property
    def status(self) -> NodeStatus:
        """
        Retrieve the Node status.

        :return: Node status enumeration.
        """
        return self.__status

    @status.setter
    def status(self, status: NodeStatus) -> None:
        """
        Set the Node status.

        Will register an event in the monitoring logging.

        :param status: New Node status.
        """
        self.__status = status
        monitoring_logging.log(
            measurement="NodeEvent", entity_name=self.name, attr_name="status", attr_value=status.value
        )

    def __str__(self) -> str:
        """
        Return a string representation.

        Looks like this::

            Node: client0
            ------------------------------
            Interfaces: i0
            Attributes:
              config: <rettij.topology.node_configurations.kubernetes_pod_config.KubernetesPodConfig object at 0x7f48085b3fa0>
              executor: <rettij.topology.node_executors.kubernetes_pod_executor.KubernetesPodExecutor object at 0x7f48085b3c10>
              iface: Available interface names: i0
              ifaces: Available interface names: i0
              name: client0
              node_type: container
              routes: []
              status: NodeStatus.UP
            Methods: add_interface(), copy_file_from_node(), copy_file_to_node(), get_data(), initiate_executor(), ping(), reboot(), run(), set_data(), shell(), shutdown(), stop_detached()


        :return: String representation.
        """
        iface_names = ", ".join(self.ifaces.keys())
        attributes_str = "\n".join([f"  {prop}: {self.__getattribute__(prop)}" for prop in self.public_property_list])

        return f"""
            Node: {self.name}
            ------------------------------
            Interfaces: {iface_names}
            Attributes:\n{attributes_str}
            Methods: {'(), '.join(self.public_method_list)}()
            """.replace(
            "\n            ", "\n"
        )  # Remove the 12 leading spaces caused by the text block

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Node):
            return repr(self) == repr(other)
        return False
