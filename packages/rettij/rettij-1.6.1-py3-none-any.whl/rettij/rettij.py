import importlib
import uuid
import os
import sys
import tempfile
import threading
from datetime import datetime
from enum import Enum
from functools import total_ordering
from pathlib import Path
from typing import Callable, Dict, Any, Optional, List, Union

import kubernetes

from rettij.abstract_scheduled_sequence import AbstractScheduledSequence
from rettij.abstract_script_sequence import AbstractScriptSequence
from rettij.commands.command import Command
from rettij.commands.command_result import CommandResult
from rettij.common.constants import COMPONENTS_DIR
from rettij.common.logging import monitoring_logging
from rettij.common.logging_utilities import LoggingSetup, Loglevel
from rettij.common.validated_path import ValidatedDirPath, ValidatedFilePath
from rettij.exceptions.invalid_path_exception import InvalidPathException
from rettij.simulation_manager import SimulationManager
from rettij.topology.exec_result import ExecResult
from rettij.topology.network_components.channel import Channel
from rettij.topology.network_components.node import Node
from rettij.topology.node_container import NodeContainer
from rettij.topology.node_executors.dummy_executor import DummyExecutor
from rettij.topology.topology_exporter_mermaid import TopologyExporterMermaid
from rettij.topology.topology_reader import TopologyReader


# from https://stackoverflow.com/questions/39268052/how-to-compare-enums-in-python
@total_ordering
class RettijPhase(Enum):
    """
    Enumerator for the rettij execution phase.

    Enumerators:
    1. PREINIT: Instance created
    2. INITIALIZED: Configuration loaded
    3. CREATED: Simulation environment online
    4. FINALIZED: Simulation environment cleaned up

    Completion of a phase may be checked using `>=`.
    """

    PREINIT = 0
    INITIALIZED = 1
    CREATED = 2
    FINALIZED = 3

    def __lt__(self, other: Any) -> Union[bool, Any]:
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __gt__(self, other: Any) -> Union[bool, Any]:
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented


class Rettij:
    """
    Main Rettij class.
    """

    # Event for when there are no more steps to execute
    no_more_steps_event: threading.Event = threading.Event()

    def __init__(
        self,
        file_loglevel: Loglevel = Loglevel.NOTSET,
        console_loglevel: Loglevel = Loglevel.NOTSET,
        fail_on_step_error: bool = True,
        confirm_finalize: bool = False,
        monitoring_config_path: Optional[Union[Path, str]] = None,
    ):
        """
        Create a Rettij object that is used to use Rettij itself.

        :param file_loglevel: (Optional) File loglevel. Set to `Loglevel.NOTSET` if logging configuration is handled
            outside of rettij (e.g. if you integrate rettij as a lib; otherwise it would overwrite global logging
            configs). If you run rettij as a standalone network simulator, set this to a desired log level, so that
            rettij can handle setting up the logger. Attention: If either file_loglevel or console_loglevel is set,
            rettij will need to configure its own logger, thus dismiss global logging configuration.
            Default: `Loglevel.NOTSET`.
        :param console_loglevel: (Optional) Console loglevel. Set to `Loglevel.NOTSET` if logging configuration is
            handled outside of rettij (e.g. if you integrate rettij as a lib; otherwise it would overwrite global
            logging configs). If you run rettij as a standalone network simulator, set this to a desired log level, so
            that rettij can handle setting up the logger. Attention: If either file_loglevel or console_loglevel is set,
            rettij will need to configure its own logger, thus dismiss global logging configuration.
            Default: `Loglevel.NOTSET`.
        :param fail_on_step_error: (Optional) If True, raise exception on step execution failure. If False, continue
            execution. Default: 'True'.
        :param confirm_finalize: (Optional) If True, wait for user input (e.g. pressing Enter on the keyboard) before
            running `finalize()`. If False, run immediately. Allows for manual access to Nodes after the simulation
            ended, thus is helpful for debug purposes. Default: `False`.
        :param monitoring_config_path: (Optional) Path to the InfluxDB monitoring logging config file.
        """
        # generate suffix like "4d24d4ccae604b75a9f282da5245c768" to make uid truly unique
        # (to make sure, multiple rettij instances can be started at the same minute)
        uid_suffix = str(uuid.uuid4()).replace("-", "")
        # create unique id from timestamp (e.g. '20210512-14-57-4d24d4ccae604b75a9f282da5245c768')
        # (namespace will be 'rettij-<uid>' (max k8s namespace length: 63 chars)
        self.uid: str = f"{datetime.now().strftime('%Y%m%d-%H-%M')}-{uid_suffix}"

        self.fail_on_step_error: bool = fail_on_step_error
        self.confirm_finalize = confirm_finalize

        LoggingSetup.initialize_logging(self.uid, file_loglevel, console_loglevel)
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)
        if monitoring_config_path:
            monitoring_logging.get_logger(monitoring_config_path)

        self.sm: SimulationManager = SimulationManager(self.uid)
        self.sequence: Optional[AbstractScheduledSequence] = None

        # Simulation time increment for each step
        self.step_size: int = 1

        self.phase: RettijPhase = RettijPhase.PREINIT

        self.kubeconfig_path: Optional[Union[Path, str]] = None

    def __load_topology(
        self, topology_path: ValidatedFilePath, components_dir_path: ValidatedDirPath = ValidatedDirPath(COMPONENTS_DIR)
    ) -> None:
        """
        Load the simulation topology from a file.

        RETTIJ INTERNAL USE ONLY. rettij does not support loading a new topology after the initial deployment.

        :param topology_path: Validated path to the file containing the topology.
        :param components_dir_path: (Optional) Validated path to the directory containing custom components.
        """
        self.logger.info("Loading simulation topology from {}".format(topology_path))
        topo_reader: TopologyReader = TopologyReader()
        nodes, channels = topo_reader.read(topology_path, components_dir_path)
        self.nodes.update(nodes)
        self.channels.update(channels)

    def load_sequence(self, sequence_path: Union[Path, ValidatedFilePath, str]) -> None:
        """
        Load a simulation sequence from a file.

        A simulation sequence can be loaded at runtime.

        :param sequence_path: Path to the file containing the simulation sequence.
        """
        self.logger.info(f"Loading simulation sequence from {sequence_path}")
        sequence_path = ValidatedFilePath(sequence_path)
        sys.path.append(str(Path(sequence_path).parent))
        module_name = Path(sequence_path).stem
        sequence_module = importlib.import_module(module_name)

        if not sequence_module:
            self.logger.error(f"No module loaded for {sequence_path}")
            return None

        if hasattr(sequence_module, "ScheduledSequence"):
            sequence: sequence_module.ScheduledSequence = sequence_module.ScheduledSequence()  # type: ignore
        elif hasattr(sequence_module, "ScriptSequence"):
            sequence: sequence_module.ScriptSequence = sequence_module.ScriptSequence()  # type: ignore
        else:
            raise AttributeError("module 'sequence' has no attribute 'ScheduleSequence' or 'ScriptSequence'")
        self.sequence = sequence
        if isinstance(self.sequence, AbstractScheduledSequence):
            self.run_sequence()
        elif isinstance(self.sequence, AbstractScriptSequence):
            self.sm.add_step(
                scheduled_time=self.sm.current_time + 1,
                command=self.run_sequence,
            )
        else:
            raise TypeError(
                "Sequence must be of type 'rettij.AbstractScheduledSequence' or 'rettij.AbstractScriptSequence'!"
            )

    class RunSequenceCommand(Command):
        """
        This Command class is used to define (execute) a sequence for rettij.
        """

        def __init__(self, rettij: Any):
            """
            Initialize a RunSequenceCommand object.

            :param rettij: Rettij object (annotated as 'Any' for import order reasons)
            """
            self.rettij = rettij
            super().__init__(DummyExecutor("rettij"), [])

        def execute(self, current_time: int = 0, inputs: Optional[Dict] = None) -> CommandResult:
            """
            Define the sequence for rettij.

            :param current_time: Not used, default '0'.
            :param inputs: Not used, default 'None'.
            :return: CommandResult object.
            """
            self.rettij.sequence.define(
                self.rettij.sm, self.rettij.nodes, self.rettij.nodes, self.rettij.channels, self.rettij.channels
            )
            self.result = CommandResult(ExecResult())
            return self.result

    def run_sequence(self, exec_now: bool = True) -> Command:
        """
        Create (and execute) a RunSequenceCommand.

        :param exec_now: Execute the command immediately if 'True'. Else, return the Command object without executing it. Default: 'True'.
        :return: RunSequenceCommand object.
        """
        cmd = self.RunSequenceCommand(self)
        if exec_now:
            cmd.execute()
        return cmd

    @staticmethod
    def load_kubeconfig(kubeconfig_path: Optional[Union[Path, str]] = None, debug_only: bool = False) -> None:
        """
        Load the kubeconfig used by the Kubernetes API client to connect to the cluster.

        Method is static so it can be used in tests and other modules if required.
        The configuration is loaded in the following order:
        1. File from `kubeconfig_path` parameter.
        2. File from `KUBECONFIG` environment variable.
        3. File at `~/.kube/config`.
        4. Information from `KUBE_TOKEN`, `KUBE_URL` and `KUBE_CA_PEM` environment variables (used in CI pipeline).
        :param kubeconfig_path: (Optional) Path to the file containing the `kubeconfig` file.
        :param debug_only: (Optional) If `True`, log everything with level DEBUG (used for less verbose output during testing and finalization). If `False`, log with levels INFO and WARNING. Default: `False`
        """
        logger = LoggingSetup.submodule_logging(Rettij.__class__.__name__)

        kubeconfig_loaded: bool = False
        kubeconfig_default_path: Path = Path.home() / ".kube" / "config"

        log_info = logger.debug if debug_only else logger.info
        log_warn = logger.debug if debug_only else logger.warning

        # Load kubeconfig from kubeconfig_path parameter, if set
        if not kubeconfig_loaded and kubeconfig_path:
            try:
                log_info(f"Loading kubeconfig from {kubeconfig_path} ...")
                kubernetes.config.load_kube_config(ValidatedFilePath(kubeconfig_path))
                kubeconfig_loaded = True
            except InvalidPathException as e:
                log_warn(f"No kubeconfig file found at {e.path_normalized}")

        # Try loading kubeconfig from value of KUBECONFIG environment variable (path to kubeconfig file)
        if not kubeconfig_loaded:
            try:
                log_info("Loading kubeconfig file path from KUBECONFIG environment variable...")
                kubeconfig_path = ValidatedFilePath(os.environ["KUBECONFIG"])
                kubernetes.config.load_kube_config(kubeconfig_path)
                kubeconfig_loaded = True
            except KeyError:
                log_warn("Environment variable KUBECONFIG not set.")
            except InvalidPathException as e:
                log_warn(f"No kubeconfig file found at {e.path_normalized}")

        # Try loading kubeconfig from default path
        if not kubeconfig_loaded:
            try:
                log_info(f"Loading kubeconfig from default path {kubeconfig_default_path} ...")
                kubernetes.config.load_kube_config(ValidatedFilePath(kubeconfig_default_path))
                kubeconfig_loaded = True
            except InvalidPathException as e:
                log_warn(f"No kubeconfig file found at {e.path_normalized}")

        # Try loading cluster access information from KUBE_TOKEN, KUBE_URL and KUBE_CA_PEM (path to ca certificate pem file) environment variables
        # This is used for the CI pipeline
        if not kubeconfig_loaded:
            try:
                log_info("Loading cluster access information from environment variables ...")
                configuration = kubernetes.client.Configuration()

                configuration.api_key["authorization"] = os.environ["KUBE_TOKEN"]
                configuration.api_key_prefix["authorization"] = "Bearer"
                configuration.host = os.environ["KUBE_URL"]
                configuration.ssl_ca_cert = os.environ["KUBE_CA_PEM"]

                kubernetes.client.Configuration.set_default(configuration)
                kubeconfig_loaded = True
            except KeyError:
                log_warn("Environment variables KUBE_TOKEN/KUBE_URL/KUBE_CA_PEM not set.")

        if not kubeconfig_loaded:
            raise RuntimeError("Unable to load Kubernetes cluster access information.")

        log_info(f"Using kubernetes url '{kubernetes.client.ApiClient().configuration.host}'.")

    def init(
        self,
        topology_path: Union[Path, str],
        sequence_path: Optional[Union[Path, str]] = None,
        kubeconfig_path: Optional[Union[Path, str]] = None,
        components_dir_path: Optional[Union[Path, str]] = Path(COMPONENTS_DIR),
        mermaid_export_path: Optional[Union[Path, str]] = None,
        step_size: int = 1,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize the simulator.

        :param topology_path: Path to the file containing the topology.
        :param sequence_path: (Optional) Path to the file containing the simulation sequence.
        :param kubeconfig_path: (Optional) Path to the file containing the `kubeconfig` file.
        :param components_dir_path: (Optional) Path to the directory containing custom components. Default: rettij built-in components directory.
        :param mermaid_export_path: (Optional) Path for the mermaid topology export file.
        :param step_size: (Optional) Simulation step size, which is the simulation time increment for each step. Default: `1`.
        :param callback: (Optional) Callback function to be run when the simulation configuration has been parsed.
        """
        # Verify inputs. As this method is used externally, we cannot rely that the input parameters are valid.
        if not (
            isinstance(topology_path, Path)
            or isinstance(topology_path, ValidatedFilePath)
            or isinstance(topology_path, str)
        ):
            raise AttributeError("Parameter 'topology_path' must be of type 'Path', 'ValidatedFilePath' or 'str'.")

        if sequence_path and not (
            isinstance(sequence_path, Path)
            or isinstance(sequence_path, ValidatedFilePath)
            or isinstance(sequence_path, str)
        ):
            raise AttributeError("Parameter 'sequence_path' must be of type 'Path', 'ValidatedFilePath' or 'str.")

        if kubeconfig_path and not (
            isinstance(kubeconfig_path, Path)
            or isinstance(kubeconfig_path, ValidatedFilePath)
            or isinstance(kubeconfig_path, str)
        ):
            raise AttributeError("Parameter 'kubeconfig_path' must be of type 'Path', 'ValidatedFilePath' or 'str'.")

        if components_dir_path and not (
            isinstance(components_dir_path, Path)
            or isinstance(components_dir_path, ValidatedDirPath)
            or isinstance(components_dir_path, str)
        ):
            raise AttributeError("Parameter 'components_dir_path' must be of type 'Path', 'ValidatedDirPath' or 'str'.")

        if mermaid_export_path and not (isinstance(mermaid_export_path, Path) or isinstance(mermaid_export_path, str)):
            raise AttributeError("Parameter 'mermaid_export_path' must be of type 'Path' or 'str'.")

        if step_size:
            if not isinstance(step_size, int):
                raise AttributeError("Parameter 'step_size' must be of type 'int'.")
            if step_size < 1:
                raise ValueError("Parameter 'step_size' must be >= 1.")
        if callback and not isinstance(callback, Callable):  # type: ignore
            # Ignore the mypy check because of https://github.com/python/mypy/issues/6864
            raise AttributeError("Parameter 'callback' must be of type 'Callable[[], None]'.")

        try:

            self.load_kubeconfig(kubeconfig_path)
            self.kubeconfig_path = kubeconfig_path  # Save for later: needed again for finalize phase

            self.__load_topology(ValidatedFilePath(topology_path), ValidatedDirPath(components_dir_path))

            # export topology as mermaid graph
            if not mermaid_export_path:
                mermaid_export_path = Path(tempfile.mkdtemp()) / "mermaid_topology.txt"
            topo_exporter_mermaid: TopologyExporterMermaid = TopologyExporterMermaid(self.nodes, self.channels)
            topo_exporter_mermaid.export(Path(mermaid_export_path))

            # Load the simulation sequence
            if sequence_path:
                self.load_sequence(sequence_path)

            self.step_size = step_size

            self.phase = RettijPhase.INITIALIZED

            if callback:
                callback()

        except Exception as e:
            self._handle_error(e)

    def create(
        self,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Create the simulation components.

        :param callback: (Optional) Callback function to be run when the simulation components have been created.
        :raises: RettijRuntimeException.
        """
        # Verify inputs. As this method is used externally, we cannot rely that the input parameters are valid.
        if callback and not isinstance(callback, Callable):  # type: ignore
            # Ignore the mypy check because of https://github.com/python/mypy/issues/6864
            raise AttributeError("Parameter 'callback' must be of type 'Callable[[], None]'.")

        try:
            self.logger.info("Setting up simulation environment (may take several minutes per Node)...")

            self.sm.kubernetes_api = kubernetes.client.CoreV1Api()
            self.sm.create_simulation()

            self.phase = RettijPhase.CREATED

            if callback:
                callback()

        except Exception as e:
            self._handle_error(e)

    def step(
        self,
        current_time: int,
        inputs: dict,
        callback: Optional[Callable[[], None]] = None,
    ) -> int:
        """
        Execute a simulation step.

        :param current_time: Current time of the external co-simulator.
        :param inputs: Dict of inputs for the current step A dict of dicts mapping entity IDs to attributes of the simulation components.
        :param callback: (Optional) Callback function to be run once a step has finished.
        :raises: RettijRuntimeException
        :return: Next time rettij wants to be called (always the current_time plus the step_size, which defaults to 1).
        """
        # Verify inputs. As this method is used externally, we cannot rely that the input parameters are valid.
        if not isinstance(current_time, int):
            raise AttributeError("Parameter 'current_time' must be of type 'int'.")
        if not isinstance(inputs, dict):
            raise AttributeError("Parameter 'inputs' must be of type 'dict'.")
        if callback and not isinstance(callback, Callable):  # type: ignore
            # Ignore the mypy check because of https://github.com/python/mypy/issues/6864
            raise AttributeError("Parameter 'callback' must be of type 'Callable[[], None]'.")

        try:
            self.sm.step(current_time, inputs, self.fail_on_step_error)
            if callback:
                callback()
        except Exception as e:
            self._handle_error(e)

        # Return the minimum time increase as new scheduled time until the simulation end
        return current_time + self.step_size

    def get_data(self, outputs: Dict[str, List]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Retrieve output data from the simulation.

        Delegates to the corresponding method in SimulationManager.

        :param outputs: Attributes to be retrieved and returned. Format: {'n305': ['closed', 'active']}
        :return: Requested output data. Format: {'n305': {'closed': True, 'active': False}}
        """
        # Verify inputs. As this method is used externally, we cannot rely that the input parameters are valid.
        if not isinstance(outputs, dict):
            raise AttributeError("Parameter 'outputs' must be of type 'dict'.")

        return self.sm.get_data(outputs)

    def has_next_step(self, current_time: int) -> bool:
        """
        Check if there are more steps to execute for the Simulator.

        :return: True if more steps are present, false if not.
        """
        return self.sm.has_next_step(current_time)

    def connect(self, source_node: Node, target_node: Node, **kwargs: Any) -> None:
        """
        Connect one Node to another.

        The method is meant to be used to establish a logical, one way data connection between two Nodes, where the source node sends certain attribute values to the target node.
        Calls the respective components 'connect' hooks.

        :param source_node: Base Node that the connection is initiated on.
        :param target_node: Node to connect the base Node to.
        :param kwargs: Custom parameters. Contents depend on the specific implementation.
        """
        # Verify inputs. As this method is used externally, we cannot rely that the input parameters are valid.
        if not isinstance(source_node, Node):
            raise AttributeError("Parameter 'source_node' must be of type 'Node'.")
        if not isinstance(target_node, Node):
            raise AttributeError("Parameter 'target_node' must be of type 'Node'.")

        self.sm.connect(source_node, target_node, **kwargs)

    def finalize(
        self,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Stop the simulation and clean up all components.

        :param callback: Callback function to be run once the simulation has been taken down.
        """
        # Verify inputs. As this method is used externally, we cannot rely that the input parameters are valid.
        if callback and not isinstance(callback, Callable):  # type: ignore
            # Ignore the mypy check because of https://github.com/python/mypy/issues/6864
            raise AttributeError("Parameter 'callback' must be of type 'Callable[[], None]'.")

        if not self.phase == RettijPhase.FINALIZED:
            if self.confirm_finalize:
                input("[Rettij]: Press [Enter] to continue with cleanup...")
            self.logger.info("Finalizing...")
            # if something like reading the input files failed, there might be no sm-object to delete
            if self.sm is not None:

                # reinitialize the API client as its temporary cert directory will be removed when __del__ is called
                # see https://github.com/kubernetes-client/python/issues/1236 for more info
                self.load_kubeconfig(self.kubeconfig_path, debug_only=True)
                kubernetes_api = kubernetes.client.CoreV1Api()

                self.sm.cleanup(f"rettij-{self.uid}", kubernetes_api=kubernetes_api)
            self.logger.info("Finalization complete.")

            self.phase = RettijPhase.FINALIZED

            if callback:
                callback()

    def _handle_error(self, exception: Exception) -> None:
        """
        Handle errors during rettij execution.
        """
        self.logger.critical("Critical error encountered!")
        self.finalize()
        raise exception

    def __del__(self) -> None:
        print(f"Instance Rettij(uid={self.uid}) deleting...")
        self.finalize()

    @property
    def nodes(self) -> NodeContainer:
        """
        Retrieve the simulation Nodes.

        :return: NodeContainer with the simulation Nodes.
        """
        return self.sm.nodes

    @property
    def channels(self) -> Dict[str, Channel]:
        """
        Retrieve the simulation Channels.

        :return: Dictionary with the simulation Channels. Format: {'c1': Channel}
        """
        return self.sm.channels
