"""The `revue` command of the trial workflow: its decision is computed in `workflow_essai.decisions`."""

import sys

from workflow_essai.cli import run
from workflow_essai.decisions import read_station, revue

if __name__ == "__main__":
    sys.exit(run(read_station, revue))
