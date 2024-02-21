from typing import List, Tuple
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class NewtonIteration:
    def __init__(self):
        self.properties = {
            "Iteration": None,
            "ResidualNorm": None,
            "SolutionNorm": None,
            "RelResidualDrop": None,
            "Relaxation": None,
            "LoadFactor": None,
            "Time": None,
        }

        number_regex = r"[+\-]?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+\-]?\d+)?"
        self.patterns = {
            "Iteration": re.compile(r".*Newton - Iteration: (\d+).*"),
            "LoadFactor": re.compile(r".*LoadFactor: (" + number_regex + ").*"),
            "ResidualNorm": re.compile(
                r".*(?:ResidualNorm|ReferenceNorm): (" + number_regex + ").*"
            ),
            "SolutionNorm": re.compile(r".*SolutionNorm: (" + number_regex + ").*"),
            "RelResidualDrop": re.compile(
                r".*RelResidualDrop: (" + number_regex + ").*"
            ),
            "Relaxation": re.compile(
                r".*Relaxation(?:\s.*)?: (" + number_regex + ").*"
            ),
            "Time": re.compile(r".*Newton - IterationTime: (" + number_regex + ").*"),
        }
        
        self.csv_path = Path("./newton_iterations.csv")
        self.csv_header = ",".join(self.properties.keys()) 
        if self.csv_path.exists():
            self.csv_path.unlink() # remove old file
        Path(self.csv_path).write_text(self.csv_header + "\n")

    def parse_line(self, line: str):
        for key, pattern in self.patterns.items():
            if match := pattern.match(line):
                if key == "Iteration":
                    self._reset()
                    self.properties[key] = int(match.group(1))
                else:
                    self.properties[key] = float(match.group(1))

    def log(self):
        text = f"Newton Iteration {self.properties['Iteration']}:"
        row = 0
        for key, value in self.properties.items():
            if key != "Iteration":
                if row % 2 == 0:
                    text += "\n"
                text += f"  {key:16}: {value:.4e}  "
                row += 1
        logger.info(text)
        with open(self.csv_path, "a") as csv_file:
            csv_file.write(",".join(str(value) for value in self.properties.values()) + "\n")
        self._reset()
        
        
    def _reset(self):
        for key in self.properties:
            self.properties[key] = None

    def is_complete(self) -> bool:
        return all(self.properties.values())



class MorisLogFilter:
    """Create a nice output of the moris log (less verbose!)"""

    def __init__(self):
        self.sections: List[Tuple[int, str, str, str]] = []
        self.newton_iteration = NewtonIteration()

    def log(self, line: str):
        if self._parse_section(line):
            # self._log_section()
            pass
        else:
            self.newton_iteration.parse_line(line)
            if self.newton_iteration.is_complete():
                self.newton_iteration.log()
            self._log_walltime(line)

    def _log_section(self):
        newest_section = self.sections[-1]
        logger.info(
            f"{newest_section[0]}: {newest_section[1]} - {newest_section[2]} - {newest_section[3]}"
        )
        
    def _log_walltime(self, line: str) -> bool:
        search_str = "Global Clock Stopped. ElapsedTime = "
        if line.startswith(search_str):
            walltime = line.lstrip(search_str)
            logger.info(f"Walltime: {walltime}")
            return True
        return False
    
    def _parse_section(self, line: str) -> bool:
        regex = re.compile(r"(?:\|  )*\|__(.*)\s-\s(.*)\s-\s(.*)")
        if match := regex.match(line):
            line = line.strip()
            level = 0
            while line and not line.startswith("__"):
                if line.startswith("|"):
                    level += 1
                line = line[1:]

            sec = (level, match.group(1), match.group(2), match.group(3))
            self.sections.append(sec)
            return True
        return False
