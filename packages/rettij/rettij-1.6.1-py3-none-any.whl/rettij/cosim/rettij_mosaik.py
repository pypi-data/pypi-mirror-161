import logging
import signal
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable

import mosaik_api

import rettij
from rettij.common.constants import COMPONENTS_DIR
from rettij.common.logging_utilities import Loglevel
from rettij.rettij import RettijPhase
from rettij.topology.network_components.node import Node

rettij_meta: Dict[str, Any] = {
    "api_version": "3.0",  # compatible with mosaik API version
    "type": "time-based",  # https://mosaik.readthedocs.io/en/latest/scheduler.html#stepping-types
    "models": {
        "Rettij": {
            "public": True,
            "params": [],  # currently, rettij_mosaik has no model params (only sim params)
            "attrs": [],
        },
    },
    "extra_methods": [
        "connect",
    ],
}

logger = logging.getLogger(__name__)


class RettijMosaik(mosaik_api.Simulator):
    """
    This class serves as a wrapper for using rettij with the mosaik co-simulator.

    It mostly handles data parsing for the mosaik meta model.
    Other function calls are generally passed directly to rettij.
    """

    def __init__(self, meta: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the RettijMosaik wrapper.

        :param meta: (Optional) Mosaik meta model. If not specified,  a default rettij meta model is
                     used. It can be specified as a parameter, so one can implement this class and override it with
                     `super().__init__(meta)` and pass a custom meta model.
        """
        if not meta:
            meta = rettij_meta
        super().__init__(meta)

        self.eid: str = ""
        self.rettij: Optional[rettij.Rettij] = None

        # configure SIGINT signal handler, so the user can stop rettij by CTRL+C
        signal.signal(signal.SIGINT, self.handle_interrupt)

    # Ignore non-matching signature of the parent method init(self, sid: str, **sim_params: Any), as this one is a subset.
    # noinspection PyMethodOverriding
    def init(
        self,
        sid: str,
        topology_path: Union[Path, str],
        file_loglevel: Loglevel = Loglevel.INFO,
        console_loglevel: Loglevel = Loglevel.WARNING,
        fail_on_step_error: bool = True,
        monitoring_config_path: Optional[Union[Path, str]] = None,
        sequence_path: Optional[Union[Path, str]] = None,
        kubeconfig_path: Optional[Union[Path, str]] = None,
        components_dir_path: Optional[Union[Path, str]] = Path(COMPONENTS_DIR),
        mermaid_export_path: Optional[Union[Path, str]] = None,
        step_size: int = 1,
        callback: Optional[Callable[[], None]] = None,
        rettij_instance: Optional[rettij.Rettij] = None,
        time_resolution: float = 1.0,
    ) -> Any:
        """
        Initialize the SimRettij mosaik simulator and rettij.

        Implements mosaik `init()` method.

        :param sid: Simulator id.
        :param topology_path: Path to the file containing the topology.
        :param file_loglevel: (Optional) File loglevel. Default: INFO
        :param console_loglevel: (Optional) Console loglevel. Default: WARNING
        :param fail_on_step_error: (Optional) If True, raise exception on step execution failure. If False, continue execution.
        :param monitoring_config_path: (Optional) Path to the InfluxDB monitoring logging config file.
        :param sequence_path: (Optional) Path to the file containing the simulation sequence.
        :param kubeconfig_path: (Optional) Path to the file containing the `kubeconfig` file.
        :param components_dir_path: (Optional) Path to the directory containing custom components. Default: rettij built-in components directory.
        :param mermaid_export_path: (Optional) Path for the mermaid topology export file.
        :param step_size: (Optional) Simulation step size, which is the simulation time increment for each step. Default: `1`.
        :param callback: (Optional) Callback function to be run when the simulation configuration has been parsed.
        :param rettij_instance: (Optional) Existing rettij instance. If supplied, it is used instead of creating a new one with the other parameters. This must be used when running other Mosaik simulators inside rettij, as rettij needs to fully run before the Mosaik models can be created.
        :param time_resolution: Mosaik time resolution. Default: `1.0`.
        :return: Mosaik meta model.
        """
        if not rettij_instance:
            self.rettij = rettij.Rettij(
                file_loglevel=file_loglevel,
                console_loglevel=console_loglevel,
                monitoring_config_path=monitoring_config_path,
            )
        else:
            self.rettij = rettij_instance

        if not self.rettij.phase >= RettijPhase.INITIALIZED:
            self.rettij.init(
                topology_path=topology_path,
                sequence_path=sequence_path,
                kubeconfig_path=kubeconfig_path,
                components_dir_path=components_dir_path,
                mermaid_export_path=mermaid_export_path,
                step_size=step_size,
                callback=callback,
            )

        for node_name, node in self.rettij.nodes.items():
            if node.mosaik_model:
                self.meta["models"][node.mosaik_model] = {
                    "public": True,
                    "params": [],
                    "attrs": set(),  # using a set to avoid duplicate entries
                }
                self.meta["models"][node.mosaik_model]["attrs"].update(node.mosaik_data.keys())

        return self.meta

    def create(self, num: int, model: str, **model_params: Any) -> List[Dict]:
        """
        Create the SimRettij mosaik simulator and the rettij simulation.

        Implements the mosaik `create()` method.

        Known limitations: Only one rettij model can be created (there was no use-case for multiple ones, yet).

        :param num: Number of instances to create.
        :param model: Model to create.
        :param model_params: Model parameters (meta['models'][model]['params']).
        :return: Return list with entitiy dicts created for the simulation.
        """
        if not self.rettij:
            raise RuntimeError("rettij not initialized, please run 'init()' first!")

        if num > 1 or self.eid:
            raise RuntimeError("Can only create one instance of rettij.")

        self.eid = f"{model}-0"

        # TODO: Allow Node creation during runtime (#72 / #73)
        if not self.rettij.phase >= RettijPhase.CREATED:
            self.rettij.create()

        children: List[Dict] = []
        for node_name, node in self.rettij.nodes.items():
            if node.mosaik_model:
                children.append(
                    {
                        "eid": node_name,
                        "type": node.mosaik_model,
                        "children": [],
                        "rel": [],  # relations are empty for now; not sure if this would really help anywhere
                    }
                )

        return [
            {
                "eid": self.eid,
                "type": "Rettij",
                "children": children,
            }
        ]

    def connect(self, source_node: Node, target_node: Node, **kwargs: Any) -> None:
        """
        Connect one Node to another.

        The method is meant to be used to establish a logical, one way data connection between two Nodes, where the source node sends certain attribute values to the target node.
        Calls the respective components 'connect' hooks.

        :param source_node: Base Node that the connection is initiated on.
        :param target_node: Node to connect the base Node to.
        :param kwargs: Custom parameters. Contents depend on the specific implementation.
        """
        if not self.rettij:
            raise RuntimeError("rettij not initialized, please run 'init()' first!")
        self.rettij.connect(source_node, target_node, **kwargs)

    def step(self, sim_time: int, inputs: Dict[str, Any], max_advance: int) -> int:
        """
        Run a single step.

        Will always sleep for one second after executing the step to account for data propagation through the simulated real-time network.
        :param sim_time: Current simulation time, i.e. at which the step should be simulated with.
        :param inputs: Inputs to the step. Example: `{'n305': {'closed': {'SimPowerSwitch-0.Model_power_switch_0': True}}}`
        :param max_advance: Required by Mosaik API, not used internally.
        :return: Next simulation time that rettij.step() should be called at.
        """
        if not self.rettij:
            raise RuntimeError("rettij not initialized, please run 'init()' and 'create()' first!")
        next_step_time = self.rettij.step(sim_time, inputs)

        # if rettij has a step at the current time, wait for step size / 100 (but at least 1 second) to allow network propagation
        if sim_time in self.rettij.sm.timed_steps.keys():
            time.sleep(max(self.rettij.step_size / 100, 1))

        return next_step_time

    def get_data(self, outputs: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
        """
        Get data from nodes. Implements mosaik API method get_data.

        :param outputs: Requested outputs, looks like this: {'n305': ['closed']})
        :return: Requested data from nodes, e.g.: {"n305": {"closed": True}}
        """
        if not self.rettij:
            raise RuntimeError("rettij not initialized, please run 'init()' and 'create()' first!")
        return self.rettij.get_data(outputs)

    def finalize(self) -> None:
        """
        Finalize the simulation.
        """
        if self.rettij:
            self.rettij.finalize()

    def handle_interrupt(self, _signal: Any, _frame: Any) -> None:
        """
        Handle ctrl+c interrupt and finalize the simulation.
        """
        self.finalize()

    @staticmethod
    def get_mosaik_nodes(rettij_instance: rettij.Rettij, model: str = "") -> List[Node]:
        """
        Retrieve Nodes in rettij that contain a Mosaik simulator.

        :param rettij_instance: Existing rettij instance. This is required as rettij needs to fully run before RettijMosaik is instantiated.
        :param model: (Optional) Mosaik model. When supplied, this method will only return the Nodes with that specific model, rather than all Nodes with any model.
        """
        if model:
            return [n for n in rettij_instance.nodes.values() if n.mosaik_model == model]
        else:
            return [n for n in rettij_instance.nodes.values() if n.mosaik_model]
