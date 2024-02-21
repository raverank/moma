import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Moris Manager")
    subparsers = parser.add_subparsers(dest="command")

    # ----------------------------------- Store ---------------------------------- #
    store_parser = subparsers.add_parser(
        "store",
        help="Store data from runs",
    )
    store_parser.add_argument(
        "identifier",
        type=str,
        help="Identifier of the run",
    )
    store_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force overwrite of the directory contents if it exists",
    )

    # ------------------------------------ Run ----------------------------------- #
    run_parser = subparsers.add_parser(
        "run",
        help="Run a moris",
    )
    run_parser.add_argument(
        "--processors",
        "-np",
        type=int,
        default=1,
        help="Number of processors to use",
    )
    run_parser.add_argument(
        "--only-shared-object",
        "-so",
        action="store_true",
        help="Only build the shared object",
    )
    run_parser_build_type = run_parser.add_mutually_exclusive_group()
    run_parser_build_type.add_argument(
        "--dbg",
        "-d",
        action="store_true",
        help="Run the debug version of moris",
    )
    run_parser_build_type.add_argument(
        "--opt",
        "-o",
        action="store_true",
        help="Run the optimized version of moris",
    )

    # ----------------------------------- Clean ---------------------------------- #
    clean_parser = subparsers.add_parser(
        "clean",
        help="Clean the current directory",
    )
    clean_parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Clean all results",
    )

    return parser.parse_args()
