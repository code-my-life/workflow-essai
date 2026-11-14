"""The `intake` command of the trial workflow: its decision is computed in `workflow_essai.decisions`."""

import sys

from workflow_essai.cli import run
from workflow_essai.decisions import intake, read_intake

if __name__ == "__main__":
    sys.exit(run(read_intake, intake))
