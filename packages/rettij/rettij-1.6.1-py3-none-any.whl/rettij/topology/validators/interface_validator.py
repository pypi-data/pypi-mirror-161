from typing import List, Dict

from rettij.topology.validators.abstract_validator import AbstractValidator
from rettij.topology.mac_address_pool import MacAddressPool


class InterfaceValidator(AbstractValidator):
    """
    Validator class for the interfaces in the topology.
    """

    def __init__(self, topology: Dict, topology_file_path: str) -> None:
        """
        Initialize a InterfaceValidator object for the supplied topology.

        :param topology: The topology to validate.
        :param topology_file_path: Path to the topology file.
        """
        super().__init__(topology, topology_file_path)

        # Maps IP / MAC to the lines that they occur in, e.g.: {"192.168.0.10": [5,18]}
        self.ips_in_use: Dict[str, List[int]] = {}
        self.macs_in_use: Dict[str, List[int]] = {}

    def validate(self) -> None:
        """
        Validate the interfaces in the topology.

        Checks for:
        - Duplicate IP addresses
        - Duplicate and non-standard (e.g. multicast) MAC addresses

        :raises: TopologyException
        """
        self._check_for_duplicate_ips()
        self._check_mac_addresses()

    def _check_for_duplicate_ips(self) -> None:
        """
        Check if there are duplicate IP addresses.

        The correct format is already checked by the schema validator.
        """
        for node in self.topology["nodes"]:
            for interface in node.get("interfaces", []):
                # check ip duplicates
                if "ip" in interface:
                    ip: str = interface["ip"]
                    line: int = interface["__line__"]
                    if ip not in self.ips_in_use:
                        self.ips_in_use[ip] = [line]
                    else:
                        self.ips_in_use[ip].append(line)

        for ip, lines in self.ips_in_use.items():
            if len(lines) > 1:
                self.logger.warning(
                    f"IP {ip} is assigned to multiple interfaces. See lines {str(lines)} in '{self.topology_file_path}'."
                )

    def _check_mac_addresses(self) -> None:
        """
        Check if there are duplicate or non-standard (e.g. multicast) mac addresses.

        The correct format is already checked by the schema validator.
        """
        for node in self.topology["nodes"]:
            for interface in node.get("interfaces", []):
                if "mac" in interface:
                    mac: str = interface["mac"]
                    line: int = interface["__line__"]
                    # Check if MAC is a multicast address:
                    # If the least-significant bit of the first octet is a 1, it is a multicast address
                    # mac.split(":")[0] -> First octet of the MAC address
                    # int("A6", 16) -> Create int from hex-string (base 16)
                    if int(mac.split(":")[0], 16) % 2 != 0:
                        self.logger.warning(
                            f"MAC {mac} is a multicast address and not a standard mac. \
                            See line {str(line)} in '{self.topology_file_path}'."
                        )
                    # check for mac duplicates
                    if mac not in self.macs_in_use:
                        MacAddressPool.add_used_mac(mac)  # add to pool to prevent generating a duplicate mac later on
                        self.macs_in_use[mac] = [line]
                    else:
                        self.macs_in_use[mac].append(line)

        for mac, lines in self.macs_in_use.items():
            if len(lines) > 1:
                self.logger.warning(
                    f"MAC {mac} is assigned to multiple interfaces. See lines {str(lines)} in '{self.topology_file_path}'."
                )
