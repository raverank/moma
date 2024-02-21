from io import BufferedReader
import logging
from typing import IO, Any, Callable
from pathlib import Path
import select
import threading
from subprocess import Popen, PIPE
from moma.log_filter import MorisLogFilter
from moma.util import (
    get_log_file,
    get_moris_config,
    get_cpp_file,
    get_moris_root,
    get_build_dir_name,
)

logger = logging.getLogger(__name__)


exit_event = threading.Event()


def handle_subprocess_stream(
    process: Popen,
    stream: BufferedReader,
    log_file: IO[Any],
    logging_func: Callable[[str], None] | None = None,
):
    while True:
        # Check if process has ended or exit_event is set
        if exit_event.is_set() or process.poll() is not None:
            break
        # Use select to wait for I/O readiness, with a timeout to periodically check exit conditions
        ready_to_read, _, _ = select.select([stream], [], [], 0.05)
        if stream in ready_to_read:
            line = stream.readline().decode("utf8").strip()
            log_file.write(line + "\n")
            log_file.flush()  # Ensure the line is written out immediately
            if logging_func and line:
                logging_func(line)
        else:
            # No data to read, loop back and check exit conditions again
            continue


def check_for_lock_file(line: str):
    if line.startswith("Warning: lock file"):
        logger.error(
            "Lock file detected. Check the log for more information. You can use the clean command with the --remove-lock option to remove the lock file."
        )
        exit_event.set()


def create_shared_object(build_type: str, cpp_file: Path, log_file: IO[Any]):
    moris_root = get_moris_root()
    cso_script = moris_root / "share" / "scripts" / "create_shared_object.sh"
    build_dir = get_build_dir_name(build_type)
    command = [
        str(cso_script),
        ".",
        build_dir,
        cpp_file.stem,
        " ",  # empty string for the last argument
    ]
    logger.debug(f"Removing so and o files for {cpp_file.stem}")
    cpp_file.with_suffix(".so").unlink(missing_ok=True)
    cpp_file.with_suffix(".o").unlink(missing_ok=True)

    logger.debug(f"Running command: {' '.join(command)}")
    with Popen(command, stdout=PIPE, stderr=PIPE) as proc:
        stdout_thread = threading.Thread(
            target=handle_subprocess_stream,
            args=(proc, proc.stdout, log_file, check_for_lock_file),
        )
        stderr_thread = threading.Thread(
            target=handle_subprocess_stream,
            args=(proc, proc.stderr, log_file, lambda line: logger.error(line)),
        )
        stdout_thread.start()
        stderr_thread.start()
        # Check if the exit_event is set after threads have completed
        if exit_event.is_set():
            raise SystemExit(1)
        stdout_thread.join()
        stderr_thread.join()

        if proc.poll() != 0 or not cpp_file.with_suffix(".so").exists():
            logger.error(
                f"Failed to create shared object for {cpp_file.stem}. Check the log at {log_file.name}"
            )
            raise SystemExit(1)
        else:
            logger.info(f"Shared object created for {cpp_file.stem}")


def get_moris_run_command(
    build_type: str,
    processors: int,
    cpp_file: Path,
) -> list[str]:
    moris_root = get_moris_root()
    build_dir = get_build_dir_name(build_type)
    moris_command = moris_root / build_dir / "projects" / "mains" / "moris"
    # make sure that the moris command exists
    if not moris_command.exists():
        logger.error(f"moris command not found at {moris_command}")
        raise SystemExit(1)
    return [
        "mpirun",
        "-np",
        str(processors),
        str(moris_command),
        str(cpp_file.with_suffix(".so")),
    ]


def run_moris(command: list[str], log_file: IO[Any]):
    logger.debug(f"Running command: {' '.join(command)}")
    with Popen(command, stdout=PIPE, stderr=PIPE) as proc:
        # Create threads for handling stdout and stderr
        stdout_logger = MorisLogFilter()
        stdout_thread = threading.Thread(
            target=handle_subprocess_stream,
            args=(proc, proc.stdout, log_file, stdout_logger.log),
        )
        stderr_thread = threading.Thread(
            target=handle_subprocess_stream,
            args=(proc, proc.stderr, log_file, lambda line: logger.error(line)),
        )
        stdout_thread.start()
        stderr_thread.start()
        stdout_thread.join()
        stderr_thread.join()
        if proc.poll() != 0:
            # logger.error(f"moris failed. Last {n_last} lines of log:\n{last_lines}")
            logger.error("moris run failed")
            raise SystemExit(1)
        else:
            logger.info("Moris run completed successfully")


def get_build_type(args):
    if args.dbg:
        return "dbg"
    elif args.opt:
        return "opt"
    else:
        logger.warning("No build type specified. Using default: dbg")
        return "dbg"


def run(args):
    config = get_moris_config()
    cpp_file = get_cpp_file(config)
    build_type = get_build_type(args)
    log_file = get_log_file(config)
    if log_file.exists():
        log_file.unlink()

    with log_file.open("w") as log:
        if not args.run_only:
            logger.info(f"Creating shared object for '{cpp_file.stem}'")
            create_shared_object(build_type, cpp_file, log)
            if args.shared_object_only:
                return

        logger.info(f"Running moris for '{cpp_file.stem}'")
        run_command = get_moris_run_command(build_type, args.processors, cpp_file)
        run_moris(run_command, log)

    # command = [MORIS_COMMAND, moris_build, args.processors, cpp_file.stem]

    # open a subprocess to run the command
