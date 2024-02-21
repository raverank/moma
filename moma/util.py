from pathlib import Path
import logging
import json
from typing import Any, Dict

logger = logging.getLogger(__name__)


def get_moris_config():
    # read the moris.json file and return the dictionary
    moris_config = Path("moris.json")
    try:
        with moris_config.open("r") as f:
            config = json.load(f)

        # make sure that the config file contains a project name
        config["project"]
    except KeyError:
        logger.error("No project name found in moris.json")
        raise SystemExit(1)
    except FileNotFoundError:
        logger.error("No moris.json file found")
        raise SystemExit(1)

    return config


def get_cpp_file(config: Dict[str, Any]) -> Path:
    # get the file name from the config and return the path
    try:
        return Path.cwd().joinpath(config["project"]).with_suffix(".cpp").absolute()
    except KeyError:
        logger.error("No project file found in moris.json")
        raise SystemExit(1)

def get_log_file(config: Dict[str, Any]) -> Path:
    # get the file name from the config and return the path
    try:
        return Path.cwd().joinpath(config["project"]).with_suffix(".log").absolute()
    except KeyError:
        logger.error("No project file found in moris.json")
        raise SystemExit(1)