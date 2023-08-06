import sys
import threading
from pathlib import Path
from threading import Event
from typing import Any

from rettij import Rettij
from rettij.cli._interactive_history_console import _InteractiveHistoryConsole
from rettij.common.logging_utilities import LoggingSetup


class CLI:
    """
    The CLI class provides an interactive Python-based CLI for rettij.
    """

    def __init__(self, rettij: Rettij, exit_event: Event):
        """
        Intialize the CLI.

        :param rettij: The rettij simulator object
        """
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)

        hint_channels = "The 'channels' keyword has not yet been implemented!"

        class _CLIHelper:
            def __call__(self, *args: Any, **kwds: Any) -> None:
                print(
                    f"""
                    Available commands:
                    * 'nodes' / 'node'                  Access simulation nodes.
                    * 'channels' / 'channel'            {hint_channels}
                    * 'load_sequence(<sequence_path>)'  Load a simulation sequence from the file at <sequence_path>.
                    * 'sequence'                        Print the current simulation sequence (registered steps and their scheduled times).
                    """.replace(
                        "\n                    ", "\n"
                    )  # Remove the 20 leading spaces in each line
                )

            def __repr__(self) -> str:
                return "Use help() to display the help dialog."

        variables = {
            "node": rettij.nodes,
            "nodes": rettij.nodes,
            "channel": hint_channels,
            "channels": hint_channels,
            "load_sequence": rettij.load_sequence,  # method reference
            "sequence": rettij.sm.timed_steps,
            "__doc__": None,
            "__name__": "__console__",
            "help": _CLIHelper(),
        }

        init_file_path = Path(__file__).resolve().parent / "_init_interpreter.py"
        try:
            with open(init_file_path, "r") as init_file:
                init_code = init_file.read()
        except FileNotFoundError:
            self.logger.error(f"Couldn't find interpreter init file at '{init_file_path}'!")
            raise

        sys.ps1 = "rettij$ "  # set shell prompt

        shell = _InteractiveHistoryConsole(variables)

        # run our custom initialisation code which was read from the python file above
        shell.runsource(init_code, filename=str(init_file_path), symbol="exec")

        shell_thread: threading.Thread = threading.Thread(
            target=shell.interact,
            args=[
                "=================\nWelcome to the rettij shell!\n\nType 'help()' for help!\n",
            ],
            daemon=True,
        )
        shell_thread.start()
        shell_thread.join()

        print("=================\nrettij shell closed!")
        exit_event.set()
