from io import StringIO
import logging
import pandas as pd
import matplotlib.pyplot as plt
from moma.util import get_log_file, get_moris_config
import csv
import numpy as np

logger = logging.getLogger(__name__)


def plot_residuals():
    config = get_moris_config()
    try:
        df = pd.read_csv("newton_iterations.csv")
    except FileNotFoundError:
        logger.error("No newton_iterations.csv file found")
        raise SystemExit(1)

    fig, ax = plt.subplots()
    ax.plot(df["Iteration"], df["ResidualNorm"], label="Residual Norm")
    ax.plot(df["Iteration"], df["SolutionNorm"], label="Solution Norm")
    ax.plot(df["Iteration"], df["RelResidualDrop"], label="Relative Residual Drop")

    # check if load stepping was used (i.e. the LoadFactor changes)
    if df["LoadFactor"].nunique() > 1:
        ax.plot(df["Iteration"], df["LoadFactor"], label="Load Factor")

    ax.set_yscale("log")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Norm")
    ax.set_title(f"'{config['project']}' Residuals")
    ax.legend()
    fig.savefig("residuals.png", dpi=300)


def _convert_to_coordinate_column(df, name) -> pd.DataFrame:
    """
    Converts columns <name>x, <name>y, ... into a single column <name>
    with a numpy array of coordinates.

    Parameters:
    - df: pandas DataFrame.
    - name: Base name of the columns to convert (e.g., 'A' for 'Ax', 'Ay').

    Returns:
    - Modified DataFrame with a new column <name> containing numpy arrays of coordinates.
    """
    # Identify columns that start with the name and end with 'x' or 'y'
    coord_columns = [
        col for col in df.columns if col.startswith(name) and col[-1] in ["x", "y", "z"]
    ]

    # Sort columns to ensure x, y order
    coord_columns = sorted(coord_columns)

    # Combine the identified columns into a single column with numpy arrays
    df[name] = df.apply(
        lambda row: np.array([row[col] for col in coord_columns]), axis=1
    )

    # Optionally, drop the original coordinate columns if you no longer need them
    df.drop(columns=coord_columns, inplace=True)
    return df


def extract_csv_from_log(args):
    if args.marker is None:
        logger.error("No marker for extraction provided!")
        raise SystemExit(1)
    marker = args.marker
    sep = args.sep

    data = args.header + "\n" if args.header else ""

    config = get_moris_config()
    log_file = get_log_file(config)

    try:
        with log_file.open("r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        logger.error(f"Cannot extract from log file: {log_file} not found")
        raise SystemExit(1)

    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith(marker):
            data += line.lstrip(marker).strip() + "\n"

    df = pd.read_csv(
        StringIO(data),
        sep=sep,
        skipinitialspace=True,
        skip_blank_lines=True,
        quoting=csv.QUOTE_NONNUMERIC,
        quotechar='"',
        index_col=False,
        header=0 if args.header else None,
    )
    logger.info(f"Extracted data from log file:\n{df}")
    logger.info(f"Saving to {args.output}")
    df.to_csv(args.output, index=False, header=True if args.header else False)
