from pathlib import Path
from typing import Dict, List, Union, Set

from rettij.common.logging_utilities import LoggingSetup
from rettij.topology.network_components.channel import Channel
from rettij.topology.network_components.node import Node
from rettij.topology.node_container import NodeContainer


class TopologyExporterMermaid:
    """
    Class to export mermaid-js compatible topologies / graphs (https://mermaid-js.github.io).
    """

    def __init__(self, nodes: NodeContainer, channels: Dict[str, Channel]) -> None:
        """
        Initialize topology-exporter.

        :param nodes: Dict with all nodes that should be included. Format: {"n0": node}
        :param channels: Dict with all channels that should be included. Format: {"c0": channel}
        """
        self._logger = LoggingSetup.submodule_logging(self.__class__.__name__)
        self._nodes: NodeContainer = nodes
        self._channels: Dict[str, Channel] = channels

    def export(self, export_file_path: Path) -> None:
        """
        Export the topology to a given file path.

        :param export_file_path: Path to the exported file.
        """
        node_connections: List[NodeConnection] = []
        node_names_found: Set[str] = set()
        for c_id, channel in self._channels.items():
            connected_node_names: List[str] = list(channel.connected_node_names_and_data_rates.keys())

            if len(connected_node_names) > 2:
                self._logger.warning(
                    f"Channel {c_id} is connected to more than 2 nodes which isn't supported by the "
                    f"mermaid exporter, thus the connection of nodes {connected_node_names}"
                    f" will be ignored."
                )
                continue

            if len(connected_node_names) < 2:
                self._logger.warning(
                    f"Channel {c_id} is connected to less than 2 nodes which isn't supported by the "
                    f"mermaid exporter, thus the connection will be ignored."
                )
                continue

            n0_name = connected_node_names[0]
            n0 = self._nodes[n0_name]
            node_names_found.add(n0_name)
            if len(connected_node_names) == 2:
                n1_name = connected_node_names[1]
                n1 = self._nodes[n1_name]
                node_connections.append(NodeConnection(n0, n1))
                node_names_found.add(n1_name)
            elif len(connected_node_names) == 1:
                node_connections.append(NodeConnection(n0))

        for node_name in self._nodes.keys():
            if node_name not in node_names_found:
                node_connections.append(NodeConnection(self._nodes[node_name]))  # create single-node node connection
                node_names_found.add(node_name)  # make sure not to add a node twice

        mermaid_graph_orientation = "BT"  # bottom -> top (possible different configs e.g.: TD, BT, LR, ...)
        mermaid_link_style = "linkStyle default interpolate basis"
        output_str_list: List[str] = [
            f"graph {mermaid_graph_orientation}\n",  # graph = Flowchart style
            f"{mermaid_link_style}\n",
        ]

        for n_con in node_connections:
            output_str_list.append(f"{n_con}\n")

        self._logger.info(f"Writing Mermaid-compatible output file to '{export_file_path}'.")
        with open(export_file_path, "w", newline="\n") as f:
            f.writelines(output_str_list)


class NodeConnection:
    """
    Represent the 1:1 connection between a pair of two nodes (and possible a single node without a connection).
    """

    def __init__(self, node_0: Node, node_1: Union[Node, None] = None) -> None:
        """
        Initialize NodeConnection object.

        :param node_0: First node of the node connection pair.
        :param node_1: (Optional) Second node of the node connection pair.
        """
        self._nodes: Dict[str, Node] = {"n0": node_0, "n1": node_1} if node_1 else {"n0": node_0}

    def __str__(self) -> str:
        """
        Create a mermaid-compatible output format.

        :return: Mermaid-compatible formatted string.
        """
        mermaid_line: Dict[str, str] = {}
        for n in self._nodes.keys():
            n_name = self._nodes[n].name
            n_desc = f"{n_name}"
            mermaid_line[n] = f"{n_name.upper()}({n_desc})"

        try:
            n0, n1 = self._nodes
            mermaid_str = f"{mermaid_line[n0]} --- {mermaid_line[n1]};"
        except ValueError:  # if only 1 unconnected node
            (n0,) = self._nodes
            mermaid_str = f"{mermaid_line[n0]}"
        return mermaid_str
