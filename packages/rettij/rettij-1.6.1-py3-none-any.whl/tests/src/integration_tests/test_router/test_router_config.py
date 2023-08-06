import os
import shutil
import unittest
from pathlib import Path
from typing import Dict

from rettij import Rettij
from rettij.commands.command_result import CommandResult
from rettij.commands.execute_router_config_command import ExecuteRouterConfigCommand
from rettij.commands.update_router_config_file_command import UpdateRouterConfigFileCommand
from rettij.common.constants import USER_DIR
from rettij.common.logging_utilities import Loglevel
from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.network_components.node import Node
from tests.src.utils.load_k8s_config import load_k8s_config


@unittest.skipIf(
    not load_k8s_config(),
    "No Kubernetes configuration found, skipping test.",
)
class TestRouterConfig(unittest.TestCase):
    """
    This TestCase contains tests regarding the simple-router component.
    """

    rettij: Rettij
    test_base_path: Path
    test_resources_path: Path

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the TestCase class variables.
        """
        cls.test_base_path = Path(__file__).parent.absolute()
        cls.test_resources_path = cls.test_base_path.joinpath("resources")

        cls.rettij = Rettij(file_loglevel=Loglevel.DEBUG, console_loglevel=Loglevel.DEBUG)

        topology_path: ValidatedFilePath = ValidatedFilePath(
            os.path.join(cls.test_resources_path, "single_router_with_config_topology.yml")
        )

        shutil.rmtree(str(Path(USER_DIR) / "config/frr/test_router1"), ignore_errors=True)
        shutil.copytree(
            (Path(cls.test_resources_path) / "config/frr/test_router1").as_posix(),
            (Path(USER_DIR) / r"config/frr/test_router1").as_posix(),
        )

        cls.rettij.init(topology_path)
        cls.rettij.create()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Clean up before TestCase class is discarded.
        """
        if cls.rettij:
            cls.rettij.finalize()
        shutil.rmtree(str(Path(USER_DIR) / "config/frr/test_router1"), ignore_errors=True)

    def test_router_config_01_startup(self) -> None:
        """
        Verify that the pre-supplied router config is applied at startup.
        """
        nodes: Dict[str, Node] = self.rettij.nodes

        shutil.rmtree((Path(USER_DIR) / r"config/frr/test_router1").as_posix())

        execute_router_config_result = ExecuteRouterConfigCommand(nodes["router1"].executor, ["do show run"]).execute(0)

        self.assertEqual(0, execute_router_config_result.exit_code)
        self.assertIn("ip route 10.1.20.0/24 192.168.0.2", execute_router_config_result.std_out)

    def test_router_config_02_update_file(self) -> None:
        """
        Verify that a new file-based router config can be applied.
        """
        nodes: Dict[str, Node] = self.rettij.nodes

        update_router_config_result: CommandResult = UpdateRouterConfigFileCommand(
            nodes["router1"].executor, ValidatedFilePath(self.test_resources_path / "user_running.conf")
        ).execute(0)

        self.assertEqual(0, update_router_config_result.exit_code)

        execute_router_config_result: CommandResult = ExecuteRouterConfigCommand(
            nodes["router1"].executor, ["do show run"]
        ).execute(0)

        self.assertEqual(0, execute_router_config_result.exit_code)
        self.assertNotIn("ip route 10.1.20.0/24 192.168.0.2", execute_router_config_result.std_out)

    def test_router_config_03_update_cmd(self) -> None:
        """
        Verify that a router config can be applied via console commands.
        """
        nodes: Dict[str, Node] = self.rettij.nodes

        execute_router_config_result: CommandResult = ExecuteRouterConfigCommand(
            nodes["router1"].executor, ["do show run"]
        ).execute(0)

        self.assertEqual(0, execute_router_config_result.exit_code)
        self.assertIn("Current configuration:", execute_router_config_result.std_out)
