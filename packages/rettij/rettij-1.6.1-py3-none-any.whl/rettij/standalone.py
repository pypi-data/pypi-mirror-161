import argparse
import os
import sys
import threading
import traceback
from pathlib import Path


def standalone() -> None:
    """
    Run rettij in standalone mode.

    Will drop the user into the shell by default.
    """
    from rettij.common.constants import SRC_DIR

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="rettij standalone script")
    parser.add_argument(
        "-t",
        "--topology",
        type=str,
        help=f"Path to topology file (required). Use '{SRC_DIR}/examples/topologies/simple-switch_topology.yml' to apply an example topology.",
        required=True,
    )

    parser.add_argument(
        "-s",
        "--sequence",
        default="",
        type=str,
        help=f"Path to simulation sequence file (optional). Use '{SRC_DIR}/examples/sequences/script_ping_sequence.py' to run an example sequence.",
    )

    parser.add_argument(
        "-k",
        "--kubeconfig",
        default="",
        type=str,
        help="Path to kubeconfig file (optional).",
    )

    parser.add_argument(
        "--components",
        default=os.path.join(SRC_DIR, "components"),
        type=str,
        help="Path to the custom components root directory (optional).",
    )

    parser.add_argument(
        "-l",
        "--loglevel",
        default="INFO",
        const="INFO",
        nargs="?",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Set loglevel for logfile, default: %(default)s",
    )

    parser.add_argument(
        "-c",
        "--console",
        default="INFO",
        const="INFO",
        nargs="?",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"],
        help="Set loglevel for console, default: %(default)s",
    )

    parser.add_argument(
        "--monitoring",
        action="store_true",
        help="Activate monitoring logging",
    )

    parser.add_argument(
        "--monitoring-config",
        default="",
        type=str,
        help="Path to the monitoring logging config file.",
    )

    parser.add_argument(
        "-q",
        "--no-cli",
        action="store_true",
        help="Disable the CLI (quiet / non-interactive mode). Default: CLI enabled.",
    )

    parser.add_argument(
        "--mermaid-export-path",
        default="",
        type=str,
        help="Path for the mermaid topology export file (optional).",
    )

    args = parser.parse_args()

    # Check if proper Python version is used for execution
    if not sys.version_info >= (3, 8):
        print("[rettij]:[CRITICAL]: The simulator requires a Python version >= 3.8")
        sys.exit(1)

    # Check if OS supports `readline`. Only relevant when run in interactive mode.
    if not args.no_cli:
        try:
            import readline

            _ = readline
        except ModuleNotFoundError:
            print(
                "[rettij]:[CRITICAL]: The interactive standalone mode requires the `readline` package (not available on Windows). Use -q or --no-cli parameter to run in quiet mode."
            )
            sys.exit(1)

    from rettij import Rettij
    from rettij.common.logging_utilities import Loglevel

    print("[rettij]:[INFO] Starting rettij...")
    print(f"[rettij]:[INFO] Running with Python {sys.version}")
    print("[rettij]:[INFO] Press ctrl + c to cancel the current simulation!")

    constructor_params: dict = {}
    if args.loglevel:
        constructor_params["file_loglevel"] = Loglevel[args.loglevel]
    if args.console:
        constructor_params["console_loglevel"] = Loglevel[args.console]
    if args.monitoring:
        constructor_params["monitoring_config_path"] = Path(args.monitoring_config)

    init_params: dict = {}
    if args.topology:
        init_params["topology_path"] = Path(args.topology)
    if args.sequence:
        init_params["sequence_path"] = Path(args.sequence)
    if args.kubeconfig:
        init_params["kubeconfig_path"] = Path(args.kubeconfig)
    if args.components:
        init_params["components_dir_path"] = Path(args.components)
    if args.mermaid_export_path:
        init_params["mermaid_export_path"] = Path(args.mermaid_export_path)

    rettij: Rettij = Rettij(**constructor_params)  # create rettij simulator object

    cli_exit_event: threading.Event = threading.Event()

    try:
        rettij.init(**init_params)
        rettij.create()

        current_time: int = 0

        # Run until no more steps are present
        if args.no_cli:
            while True:
                rettij.step(current_time, {})
                if rettij.has_next_step(current_time):
                    current_time += 1
                else:
                    break

        # Run as long as the CLI is open
        else:
            from rettij.cli.cli import CLI

            cli_thread = threading.Thread(target=CLI, args=[rettij, cli_exit_event], daemon=True)
            cli_thread.start()

            # TODO: CLI should be able to manipulate timer
            while not cli_exit_event.is_set():
                rettij.step(current_time, {})
                current_time += 1

    except KeyboardInterrupt:
        print("[rettij]:[INFO] Network simulation cancelled...\n\n\n")
    except Exception:
        print(
            f"[rettij]:[CRITICAL] Critical error encountered!\n-----\n{traceback.format_exc()}-----",
            file=sys.stderr,
        )  # print exception to stderr
        sys.exit(1)  # exit program with error

    # cleanup simulation environment
    rettij.finalize()
