import logging
from importlib.resources import read_text
from pathlib import Path

logger = logging.getLogger(__name__)


def _write_moris_json(project_name: str):
    # load the template moris.json file and write it to the current directory with the
    # project name replaced
    template = read_text("moma.templates", "moris.json")
    template = template % {"project_name": project_name}
    with open("moris.json", "w") as f:
        f.write(template)


def new_project(args):
    if Path("moris.json").exists():
        logger.error("moris.json already exists")
        raise SystemExit(1)
    _write_moris_json(args.project_name)
