from pathlib import Path

from rettij.common.file_permissions import FilePermissions
from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.hooks.abstract_post_deploy_hook import AbstractPostDeployHook
from rettij.topology.network_components.node import Node
from rettij.topology.node_container import NodeContainer


class PostDeployHook(AbstractPostDeployHook):
    """
    This class defines the 'post-deploy' hook for the 'simple-router' component.

    It reads and applies any configuration placed in the Node's 'config_dir'.
    """

    def execute(self, node: Node, nodes: NodeContainer) -> None:
        """
        Read and apply any configuration placed in the Node's 'config_dir'.

        :param node: Node to execute the hook for.
        :param nodes: NodeContainer object with all simulation Nodes
        """
        if node.executor_config.config_dir:
            config_dir: Path = node.executor_config.config_dir

            # Write initial FRR running config to /etc/frr/frr.conf
            node.executor.execute_command(["bash", "-c", "{ echo write integrated; } | vtysh"], log_error_only=True)
            # Iterate over all files in the node's config directory
            for path in config_dir.glob("*"):
                if path.is_file():
                    # Define file permissions for the custom config file
                    fps: FilePermissions = FilePermissions("640", "frr", "frr")
                    # Put the custom configuration file in the container
                    path_in_container = node.executor.copy_file_to_node(ValidatedFilePath(path), "/etc/frr/config", fps)
                    # Append the custom config file to the central FRR config file
                    node.executor.execute_command(
                        ["bash", "-c", f"cat {path_in_container.as_posix()} >> /etc/frr/frr.conf"], log_error_only=True
                    )

            # Reload the FRR configuration from the central config file
            # --bindir is the directory containing the `vtysh` binary
            # --overwrite means that this newly applied config will be written back to the config file
            # --reload means that changes are actually applied (--test only shows whatif)
            node.executor.execute_command(
                [
                    "python3",
                    "/usr/lib/frr/frr-reload.py",
                    "--overwrite",
                    "--reload",
                    "/etc/frr/frr.conf",
                ],
                log_error_only=True,
            )
