import unittest
from pathlib import Path
from unittest.mock import MagicMock

from rettij import Rettij
from rettij.common.constants import SRC_DIR, TESTS_DIR
from rettij.common.logging_utilities import Loglevel
from rettij.cosim.rettij_mosaik import RettijMosaik
from rettij.rettij import RettijPhase
from rettij.topology.node_container import NodeContainer


class TestRettijMosaik(unittest.TestCase):
    """
    This TestCase contains unit tests regarding the RettijMosaik class.
    """

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        self.rettij_mosaik: RettijMosaik = RettijMosaik()

    def test_init(self) -> None:
        """
        Verify that RettijMosaik.init() raises an exception when invalid parameters are passed and works with valid parameters.
        """
        # Contains a non-existent parameter
        faulty_rettij_params_01 = {"step_size": 1, "non_existent_parameter": ""}
        with self.assertRaises(TypeError):
            # This will trigger MyPy for some reason, as the signature contains actual parameters rather than **kwargs.
            RettijMosaik().init("", **faulty_rettij_params_01)  # type: ignore

        # Lacks the required topology_path parameter
        faulty_rettij_params_02 = {"step_size": 1}
        with self.assertRaises(TypeError):
            # This will trigger MyPy for some reason, as the signature contains actual parameters rather than **kwargs
            RettijMosaik().init("", **faulty_rettij_params_02)  # type: ignore

        valid_rettij_params = {
            "step_size": 1,
            "file_loglevel": Loglevel.DEBUG,
            "console_loglevel": Loglevel.INFO,
            "topology_path": Path(SRC_DIR) / "examples" / "topologies" / "simple-switch_topology.yml",
            "sequence_path": "",
            "components_dir_path": Path(TESTS_DIR) / "shared_resources" / "custom_components",
            "kubeconfig_path": "",
            "monitoring_config_path": "",
        }
        # This will trigger MyPy for some reason, as the signature contains actual parameters rather than **kwargs
        self.rettij_mosaik.init("", **valid_rettij_params)  # type: ignore

        self.assertIsInstance(self.rettij_mosaik.rettij, Rettij)
        assert isinstance(self.rettij_mosaik.rettij, Rettij)
        self.assertGreater(len(self.rettij_mosaik.rettij.nodes), 0)

    def test_create(self) -> None:
        """
        Verify that `RettijMosaik.create_children()` returns the expected data.

        Implicitly tests `RettijMosaik.create_entity()` as well, as it is called by `RettijMosaik.create_children()`.
        """
        n0 = MagicMock()
        n1 = MagicMock()
        n0.mosaik_model = "Test"
        n1.mosaik_model = "Test1"
        nodes = {"n0": n0, "n1": n1}
        node_container = NodeContainer(nodes)
        self.rettij_mosaik.rettij = MagicMock()
        self.rettij_mosaik.rettij.phase = RettijPhase.CREATED
        self.rettij_mosaik.rettij.nodes = node_container
        entities = self.rettij_mosaik.create(1, "Rettij")

        # Using output from `self.rettij_mosaik.create_children()` to ensure future consistency of data
        self.assertEqual(
            entities,
            [
                {
                    "children": [
                        {"children": [], "eid": "n0", "rel": [], "type": "Test"},
                        {"children": [], "eid": "n1", "rel": [], "type": "Test1"},
                    ],
                    "eid": "Rettij-0",
                    "type": "Rettij",
                }
            ],
        )

    # RettijMosaik.connect() requires a live system and is not unit testable with any meaningful result
    # RettijMosaik.step() requires a live system and is not unit testable with any meaningful result
    # RettijMosaik.get_data() requires a live system and is not unit testable with any meaningful result
    # RettijMosaik.finalize() requires a live system and is not unit testable with any meaningful result
