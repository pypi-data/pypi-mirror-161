import os
import unittest
from datetime import datetime

from rettij.common.constants import TESTS_DIR, RESOURCES_DIR
from rettij.common.logging_utilities import LoggingSetup, Loglevel
from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.topology_reader import TopologyReader


class ValidatorTestBase(unittest.TestCase):
    """
    This TestCase contains the setup for testing the validators.

    It is inherited by the classes containing the actual tests.
    """

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        uid: str = str(datetime.now().strftime("%H%M%S"))  # create (almost) unique id from timestamp

        LoggingSetup.initialize_logging(uid, Loglevel.DEBUG, Loglevel.DEBUG)
        self.logger = LoggingSetup.submodule_logging("ValidatorTest")

        self.test_resources_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")

        self.topology_file_path: ValidatedFilePath = ValidatedFilePath(
            os.path.join(TESTS_DIR, "shared_resources", "topologies", "topology.yml")
        )

        self.topology = TopologyReader.load_yaml(self.topology_file_path)

        self.schema_file_path: ValidatedFilePath = ValidatedFilePath(
            os.path.join(
                RESOURCES_DIR,
                "schemas",
                f"{TopologyReader.MAJOR_VERSION}-{TopologyReader.MINOR_VERSION}",
                "topology_schema.json",
            )
        )

        LoggingSetup.initialize_logging(uid, Loglevel.DEBUG, Loglevel.DEBUG)
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)
