from moma.util import get_moris_config, get_cpp_file
import logging
import re

logger = logging.getLogger(__name__)


def apply_parameters(args):
    config = get_moris_config()
    cpp_file = get_cpp_file(config)
    try:
        parameters = config["parameters"]
    except KeyError:
        logger.error("No parameters found in moris.json")
        raise SystemExit(1)
    logger.info(f"Applying parameters to {cpp_file}")

    # regular expression that matches a variable assignment in a C++ file
    parameter_regex = re.compile(r"^\s*(?:[^\/\n]+)\s+(\w+)\s*=\s*([^;]+);")

    out = []
    with cpp_file.open("r") as cpp:
        for line in cpp.readlines():
            if match := parameter_regex.match(line):
                var, value = match.groups()
                if var in parameters:
                    formatted = f"{parameters[var]}"
                    line = line.replace(value, f"{formatted}")
                    logger.debug(f"Replaced {var} value {value} with {formatted}")
                    parameters.pop(var)
            out.append(line)
    
    if parameters:
        not_found = "\n".join("  - " + k + ": " + str(v) for k, v in parameters.items())
        logger.warning(
            f"Could not find the following parameter in the file {cpp_file}:\n"
            + f"{not_found}"
        )
    
    with cpp_file.open("w") as cpp:
        logger.info(f"Writing parameters to {cpp_file}")
        cpp.writelines(out)


