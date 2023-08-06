import os
import unittest
from unittest.mock import Mock, patch
from pathlib import Path
from rettij import Rettij

from rettij.common.constants import TESTS_DIR
from rettij.common.validated_path import ValidatedFilePath


class TestRettij(unittest.TestCase):
    """
    This TestCase contains tests for the "main" class Rettij.
    """

    topo_path: ValidatedFilePath = ValidatedFilePath.join_paths(
        TESTS_DIR, "shared_resources", "topologies", "topology.yml"
    )
    non_existant_path: str = str(Path.home() / "some" / "nonexistant" / "file.txt")

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        self.rettij: Rettij = Rettij()
        # create empty "kubeconfig" to make sure it exists and the tests don't already fail at ValidatedFilePath check
        kube_dir = Path.home() / ".kube"
        default_kubeconfig_path = kube_dir / "config"
        if not os.path.exists(default_kubeconfig_path):
            kube_dir.mkdir(parents=True, exist_ok=True)
            open(default_kubeconfig_path, "w").close()

    @patch("rettij.Rettij.finalize")  # prevent calling finalize which won't work because it didn't really initialize
    def test_load_kubeconfig_from_param_validated_file_path(self, _: Mock) -> None:
        """
        Verify that rettij handles kubeconfig_path parameter with given path correctly.
        """
        with patch("rettij.rettij.kubernetes.config") as config_mock:
            # Test case: Existing path (ValidatedFilePath)
            path_in_validated: ValidatedFilePath = self.topo_path  # just use some existing file path
            path_in_str: str = str(self.topo_path)  # just use some existing file path
            path_out_expected = path_in_str
            self.rettij.load_kubeconfig(path_in_validated)
            config_mock.load_kube_config.assert_called_once_with(path_out_expected)

    @patch("rettij.Rettij.finalize")  # prevent calling finalize which won't work because it didn't really initialize
    def test_load_kubeconfig_path_param_str(self, _: Mock) -> None:
        """
        Verify that rettij handles kubeconfig_path parameter with given path correctly.
        """
        with patch("rettij.rettij.kubernetes.config") as config_mock:
            # Test case: Existing path (str)
            path_in_str: str = str(self.topo_path)  # just use some existing file path
            path_out_expected = path_in_str
            self.rettij.load_kubeconfig(kubeconfig_path=path_in_str)
            config_mock.load_kube_config.assert_called_once_with(path_out_expected)

    @patch("rettij.Rettij.finalize")  # prevent calling finalize which won't work because it didn't really initialize
    def test_load_kubeconfig_from_param_path(self, _: Mock) -> None:
        """
        Verify that rettij handles kubeconfig_path parameter with given path correctly.
        """
        with patch("rettij.rettij.kubernetes.config") as config_mock:
            # Test case: Existing path (Path)
            path_in_str: str = str(self.topo_path)  # just use some existing file path
            path_in_path: Path = Path(self.topo_path)  # just use some existing file path
            path_out_expected = path_in_str
            self.rettij.load_kubeconfig(kubeconfig_path=path_in_path)
            config_mock.load_kube_config.assert_called_once_with(path_out_expected)

    @patch("rettij.Rettij.finalize")  # prevent calling finalize which won't work because it didn't really initialize
    def test_load_kubeconfig_from_param_non_existant(self, _: Mock) -> None:
        """
        Verify that rettij handles kubeconfig_path parameter with given path correctly.
        """
        with patch("rettij.rettij.kubernetes.config"):
            # Test case: Non existant path
            path_in_non_existant: str = self.non_existant_path
            with self.assertLogs(level="WARNING", logger="rettij") as log:
                self.rettij.load_kubeconfig(kubeconfig_path=path_in_non_existant)
                self.assertIn("No kubeconfig file found at", log.output[0])

    @patch("rettij.Rettij.finalize")  # prevent calling finalize which won't work because it didn't really initialize
    def test_load_kubeconfig_from_default_path(self, _: Mock) -> None:
        """
        Verify that rettij handles kubeconfig_path parameter as empty string (=should use default path) correctly.
        """
        with patch("rettij.rettij.kubernetes.config") as config_mock:
            # Test case: No kubeconfig path given, i.e. use default path (~/.kube/config)
            path_in = ""
            path_out_expected = str(Path.home() / ".kube" / "config")
            self.rettij.load_kubeconfig(kubeconfig_path=path_in)
            config_mock.load_kube_config.assert_called_once_with(path_out_expected)

    # Mock KUBECONFIG environment variable; use clear=True to clear existing system environment vars
    @patch.dict(os.environ, {"KUBECONFIG": topo_path}, clear=True)  # just use some existing file path
    @patch("rettij.Rettij.finalize")  # prevent calling finalize which won't work because it didn't really initialize
    def test_load_kubeconfig_from_env_valid(self, _: Mock) -> None:
        """
        Verify that rettij handles kubeconfig_path parameter not set (=should use environment var) correctly.
        """
        with patch("rettij.rettij.kubernetes.config") as config_mock:
            path_out_expected = self.topo_path  # just use some existing file path
            self.rettij.load_kubeconfig()
            config_mock.load_kube_config.assert_called_once_with(path_out_expected)

    # Mock KUBECONFIG environment variable; use clear=True to clear existing system environment vars
    @patch.dict(os.environ, {"KUBECONFIG": non_existant_path}, clear=True)
    @patch("rettij.Rettij.finalize")  # prevent calling finalize which won't work because it didn't really initialize
    def test_load_kubeconfig_from_env_invalid(self, _: Mock) -> None:
        """
        Verify handling invalid path in KUBECONFIG environment variable is done correctly.
        """
        with patch("rettij.rettij.kubernetes.config"):
            with self.assertLogs(level="WARNING", logger="rettij") as log:
                self.rettij.load_kubeconfig()
                self.assertIn("No kubeconfig file found at", log.output[0])
