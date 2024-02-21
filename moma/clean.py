from pathlib import Path
import logging
from moma.util import get_moris_config

logger = logging.getLogger(__name__)



def clean_dir(args):
    config = get_moris_config()
    project_name = config["project"]
    
    clean_patterns = [
        f"{project_name}.exo",
        f"{project_name}.log",
        f"{project_name}.so",
        "xtk_temp.exo",
        "Parameter_Receipt.xml",
        "debug_mesh_*.json",
        "mapping_result_*.json",
        "surface_meshes_*.json"
    ]
    
    num_files_removed = 0
    for pattern in clean_patterns:
        logger.debug(f"Looking for files with pattern: {pattern}")
        for file in Path.cwd().glob(pattern):
            file.unlink()
            logger.debug(f"Removing file: {file}")
            num_files_removed += 1
    if num_files_removed == 0:
        logger.info("No files to remove")
    else:
        logger.info(f"Removed {num_files_removed} files from the current directory")