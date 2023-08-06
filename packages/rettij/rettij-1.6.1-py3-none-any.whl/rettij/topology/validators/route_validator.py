import ipaddress
from typing import List, Dict

from rettij.topology.validators.abstract_validator import AbstractValidator


class RouteValidator(AbstractValidator):
    """
    Validator class for the routes in the topology.
    """

    def __init__(self, topology: Dict, topology_file_path: str) -> None:
        """
        Initialize a RouteValidator object for the supplied topology.

        :param topology: The topology to validate.
        :param topology_file_path: Path to the topology file.
        """
        super().__init__(topology, topology_file_path)

        self.ip_addresses: List[str] = []
        self.iface_nws: List[ipaddress.IPv4Network] = []

    def validate(self) -> None:
        """
        Validate the routes in the topology.

        Checks for:
        - Gateway IPs actually existing

        :raises: TopologyException
        """
        self._check_default_gateway_ip()

    def _check_default_gateway_ip(self) -> None:
        """
        Check if the default gateway ip actually exists.
        """
        # Catalog all networks in this topology
        for node in self.topology.get("nodes", []):
            for interface in node.get("interfaces", []):
                if "ip" in interface:
                    iface_network = ipaddress.IPv4Network(interface.get("ip"), False)
                    self.iface_nws.append(iface_network)

        # Find this node's default gateway
        for node in self.topology.get("nodes", []):
            for route in node.get("routes", []):
                if route.get("network") == "0.0.0.0/0":

                    # Check if the gateway shares the simulation or host network
                    found: bool = False
                    for nw in self.iface_nws:
                        gw_nw_addr = ipaddress.IPv4Interface(
                            f"{route.get('gateway')}/{nw.prefixlen}"
                        ).network.network_address
                        if gw_nw_addr == nw.network_address:
                            found = True
                            break

                    # Log warning that gateway is outside simulation and host network
                    if not found:
                        self.logger.warning(
                            f"Default gateway {route['gateway']} of Node {node['id']} in {self.topology_file_path} lies outside the simulation or host network.",
                        )
