from typing import Dict, List

from rettij.common.logging_utilities import LoggingSetup
from rettij.topology.validators.abstract_validator import AbstractValidator
from rettij.exceptions.topology_exception import TopologyException


class ChannelValidator(AbstractValidator):
    """
    Validator class for the channels in the topology.
    """

    def __init__(self, topology: Dict, topology_file_path: str) -> None:
        """
        Initialize a ChannelValidator object for the supplied topology.

        :param topology: The topology to validate.
        :param topology_file_path: Path to the topology file.
        """
        super().__init__(topology, topology_file_path)
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)

        # Maps channels to the lines that they are declared in, e.g.: {"c0": [10,13]}
        self.declared_channels: Dict[str, List[int]] = self._store_declared_channels()

        # Maps channels to the lines that they are used in, e.g.: {"c0": [5,8]}
        self.referenced_channels: Dict[str, List[int]] = self._store_referenced_channels()

    def validate(self) -> None:
        """
        Validate the channels in the topology.

        Checks for:
        - Duplicate channels
        - Correct channel references

        :raises: TopologyException
        """
        self._check_for_duplicate_channels()
        self._check_channel_references()

    def _store_declared_channels(self) -> Dict[str, List[int]]:
        """
        Store the declared channels, and the lines they are declared in, in a dictionary.

        :return: Dictionary of channels and lines they are declared in. Dictionary looks like this: {"c0": [41]}
        """
        declared_channels: Dict[str, List[int]] = {}
        for channel in self.topology.get("channels", []):
            channel_id: str = channel.get("id", "")
            line: int = channel.get("__line__", 0)
            if channel_id not in declared_channels:
                declared_channels[channel_id] = [line]
            else:
                declared_channels[channel_id].append(line)

        return declared_channels

    def _store_referenced_channels(self) -> Dict[str, List[int]]:
        """
        Store the referenced channels, and the lines they are referenced in, in a dictionary.

        :return: Dictionary of channels and lines they are referenced in. Dictionary looks like this: {"c0": [8, 20]}
        """
        referenced_channels: Dict[str, List[int]] = {}
        for node in self.topology.get("nodes", []):
            if node.get("interfaces"):
                for interface in node.get("interfaces"):
                    if "channel" in interface:
                        channel_id = interface.get("channel")
                        line = interface.get("__line__")
                        if channel_id not in referenced_channels:
                            referenced_channels[channel_id] = [line]
                        else:
                            referenced_channels[channel_id].append(line)

        return referenced_channels

    def _check_for_duplicate_channels(self) -> None:
        """
        Check if declared channels are unique and raise an error if not.

        :raises: TopologyException
        """
        for channel_id, lines in self.declared_channels.items():
            if len(lines) > 1:
                raise TopologyException(
                    TopologyException.CHANNEL_VALIDATION_FAILED,
                    self.topology_file_path,
                    message=f"Explicitly declared channel {channel_id} is declared twice. See lines {lines}.",
                ) from None

    def _check_channel_references(self) -> None:
        """
        Check if every channel has exactly two connections and if referenced channels actually exist, log a warning if not.
        """
        # check if all declared channels are actually used
        unused_channel_ids = self.declared_channels.keys() - self.referenced_channels.keys()
        for unused_channel_id in unused_channel_ids:
            self.logger.warning(
                f"Channel {unused_channel_id} was declared but never used. See line {str(self.declared_channels[unused_channel_id])} in {self.topology_file_path}."
            )

        # check if used channels are used exactly twice
        for channel_id, lines in self.referenced_channels.items():
            if len(lines) != 2:
                self.logger.warning(
                    f"Channel {channel_id} has {len(lines)} connection(s) instead of 2. It is used in lines {str(lines)} in {self.topology_file_path}."
                )
