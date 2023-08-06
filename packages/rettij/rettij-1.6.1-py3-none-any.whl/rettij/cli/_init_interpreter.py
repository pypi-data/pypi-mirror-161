"""
This init-script is run inside the rettij CLI at initialization.

Anything that should be set up and initialized before the user actually sees the CLI prompt, should be integrated into this script.
"""

import readline
import sys

# enable auto-completion in the InteractiveConsole for Linux and MacOS
from rlcompleter import Completer

if sys.platform == "darwin" and "libedit" in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")
readline.set_completer(Completer(locals()).complete)
