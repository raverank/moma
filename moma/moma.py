from moma import clean
from moma.args import parse_args
from rich.logging import RichHandler
import logging
from moma.store import store_results
from moma.clean import clean_dir, remove_lock
from moma.run import run
from moma.post import plot_residuals, extract_csv_from_log
from moma.parameter import apply_parameters
from moma.new import new_project


def configure_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,  # Adjust root logger level
        handlers=[RichHandler(level=level)],  # Ensure handler level matches
        datefmt="[%X]",
        format="%(message)s",
    )


def main():
    args = parse_args()
    configure_logging(args.verbose)

    if args.command == "store":
        store_results(args)
    elif args.command == "run":
        if not args.no_clean and not args.run_only:
            clean_dir(args)
        if args.apply_parameters:
            apply_parameters(args)
        run(args)
    elif args.command == "clean":
        clean_dir(args)
        if args.remove_lock:
            remove_lock()
    elif args.command == "new":
        new_project(args)
    elif args.command == "post":
        if args.post_command == "residuals":
            plot_residuals()
        elif args.post_command == "extract":
            extract_csv_from_log(args)
