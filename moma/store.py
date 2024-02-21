import glob
from pathlib import Path
from shutil import copy
import argparse
import json
import logging
from typing import Generator, List, Union
from moma.util import get_moris_config, get_cpp_file


logger = logging.getLogger(__name__)


def transfer_files(file_patterns: list, destination: Path):
    for file_pattern in file_patterns:
        files: Union[Generator[Path, None, None], List[Path]] = []
        if isinstance(file_pattern, str):
            files = Path.cwd().glob(str(file_pattern))
        else:
            files = [file_pattern]
        for file_name in files:
            try:
                # move the file to the results directory
                dest = destination / file_name.name
                copy(file_name, dest)
            except FileNotFoundError:
                logger.info(f"'{file_name}' is not available and will not be stored")


def store_results(args):
    config = get_moris_config()

    result_directory = Path(config.get("result_directory", "results"))
    result_directory.mkdir(exist_ok=True)

    identifier = args.identifier
    try:
        problem_dir = result_directory / identifier
        problem_dir.mkdir()
    except FileExistsError:
        if args.force:
            logger.warning(f"The directory {problem_dir} already exists. Overwriting")
            # remove contents of the directory
            for file in problem_dir.glob("*"):
                file.unlink()
        else:
            logger.error(
                f"The directory {problem_dir} already exists. Please choose a different name or use the --force option to overwrite."
            )
            raise SystemExit(1)
    logger.info(f"Results will be stored in {problem_dir}")

    problem_file = get_cpp_file(config)
    files = [
        problem_file,
        problem_file.with_suffix(".exo"),
        problem_file.with_suffix(".log"),
        "moris.json",
        "xtk_temp.exo",
        "Parameter_Receipt.xml",
    ]
    transfer_files(files, problem_dir)
