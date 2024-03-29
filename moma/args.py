import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Moris Manager")
    subparsers = parser.add_subparsers(dest="command")
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

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
        "--shared-object-only",
        "-so",
        action="store_true",
        help="Only build the shared object",
    )
    run_parser.add_argument(
        "--run-only",
        action="store_true",
        help="Do not create the shared object before run",
    )
    run_parser.add_argument(
        "--apply-parameters",
        action="store_true",
        help="Apply the parameters from the moris.json to the C++ file",
    )
    run_parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not clean the directory before running",
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
    
    # ----------------------------------- Post ----------------------------------- #
    post_parser = subparsers.add_parser(
        "post",
        help="Post process the results",
    )
    post_subparsers = post_parser.add_subparsers(dest="post_command")
    
    # residuals
    post_subparsers.add_parser(
        "residuals",
        help="Plot the residuals",
    )
    
    # extract
    extract_parser = post_subparsers.add_parser(
        "extract",
        help="Extract the results",
    )
    extract_parser.add_argument(
        "--marker",
        "-m",
        type=str,
        help="Name of the marker that indicates which lines to extract",
    )
    extract_parser.add_argument(
        "--sep",
        type=str,
        default=",",
        help="Separator for the values",
    )
    extract_parser.add_argument(
        "--header",
        type=str,
        help="Header for the csv file. Has to have the same number of columns as the values. All column names have to be separated by the separator.",
    )
    extract_parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="extracted.csv",
        help="Output file",
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
    clean_parser.add_argument(
        "--remove-lock",
        action="store_true",
        help="Remove the lock file",
    )
    
    # ------------------------------------ New ----------------------------------- #
    new_parser = subparsers.add_parser(
        "new",
        help="Create a new moris",
    )
    new_parser.add_argument(
        "project_name",
        type=str,
        help="Name of the new moris project",
    )
    return parser.parse_args()
