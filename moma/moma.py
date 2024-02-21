from moma import clean
from moma.args import parse_args
from rich.logging import RichHandler
import logging
from moma.store import store_results
from moma.clean import clean_dir
from moma.run import run
from moma.post import plot_residuals, extract_csv_from_log

logging.basicConfig(
    level=logging.INFO,
    handlers=[RichHandler()],
    datefmt="[%X]",
    format="%(message)s",
)

logger = logging.getLogger(__name__)


def main():
    args = parse_args()

    if args.command == "store":
        store_results(args)
    elif args.command == "run":
        clean_dir(args)
        run(args)
    elif args.command == "clean":
        clean_dir(args)
    elif args.command == "post":
        if args.post_command == "residuals":
            plot_residuals()
        elif args.post_command == "extract":
            extract_csv_from_log(args)