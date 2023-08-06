import code
import os
import readline
import atexit
from typing import Any


class _InteractiveHistoryConsole(code.InteractiveConsole):
    """
    This class extends the InteractiveConsole with a persistent history.

    After leaving and restarting the rettij CLI, the user can press the arrow up key to scroll through the
    commands of the last session, just das expected by experienced UNIX users.
    """

    def __init__(
        self,
        local_vars: Any = None,
        filename: str = "<console>",
        history_file: str = os.path.expanduser("~/.rettij-cli-history"),
    ):
        """
        Initialize InteractiveConsole with command history.

        :param local_vars: list of variables which should be passed to the InteractiveConsole
        :param filename: input stream, defaults to the console
        :param history_file: file to safe the console history to, defaults to the Python default
        """
        code.InteractiveConsole.__init__(self, local_vars, filename)
        self.__init_history(history_file)

    def __init_history(self, history_file: str) -> None:
        """
        Configure the history.

        :param history_file: path to the history file
        """
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(history_file)
            except FileNotFoundError:
                pass
            atexit.register(self.__save_history, history_file)

    @staticmethod
    def __save_history(history_file: str) -> None:
        """
        Save the history when the InteractiveConsole is terminated.

        Used as an exit callback in __init_history().
        :param history_file: path to the history file
        """
        # only save the last 1000 lines
        readline.set_history_length(1000)
        readline.write_history_file(history_file)
