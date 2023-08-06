import filecmp
import os
import tempfile
import unittest
from pathlib import Path

from rettij.common.constants import TESTS_DIR
from rettij.common.validated_path import ValidatedDirPath, ValidatedFilePath
from rettij.topology.topology_exporter_mermaid import TopologyExporterMermaid
from rettij.topology.topology_reader import TopologyReader


class TestTopologyExporterMermaid(unittest.TestCase):
    """
    This TestCase contains tests regarding TopologyExporterMermaid class.
    """

    test_base_path: str
    test_resources_path: ValidatedDirPath
    topo_path: ValidatedFilePath
    expected_out_file: ValidatedFilePath

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the TestCase class variables.
        """
        cls.test_base_path = os.path.dirname(os.path.realpath(__file__))
        cls.test_resources_path = ValidatedDirPath.join_paths(cls.test_base_path, "resources")

        cls.topo_path = ValidatedFilePath.join_paths(TESTS_DIR, "shared_resources", "topologies", "topology.yml")
        cls.expected_out_file = ValidatedFilePath.join_paths(cls.test_resources_path, "expected_mermaid_topology.txt")

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        self.tmp_output_dir = tempfile.TemporaryDirectory()
        self.tmp_output_file = Path(self.tmp_output_dir.name) / "tmp_out_mermaid_topology.txt"
        topo_reader: TopologyReader = TopologyReader()
        nodes, channels = topo_reader.read(self.topo_path)
        self.topo_exporter_mermaid: TopologyExporterMermaid = TopologyExporterMermaid(nodes, channels)

    def tearDown(self) -> None:
        """
        Clean up before TestCase instance is discarded.
        """
        self.tmp_output_dir.cleanup()

    def test_export(self) -> None:
        """
        Verify that the Topology can be parsed into a Mermaid diagram.
        """
        self.topo_exporter_mermaid.export(self.tmp_output_file)
        self.assertTrue(
            filecmp.cmp(self.expected_out_file, self.tmp_output_file, shallow=False),
            "Output mermaid topology file doesn't match expected file.",
        )
