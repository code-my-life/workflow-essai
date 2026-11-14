"""The shared body of the commands in `commands/`: read the input, compute the decision, write it."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from typing import TextIO

from workflow_essai.decisions import InvalidInputError

# The exit code of an input the command cannot read; its standard output stays empty.
INVALID_INPUT = 2


def run(
    read: Callable[[str], dict],
    decide: Callable[[dict], dict],
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Read one JSON object from stdin, write its decision as one JSON line on stdout; return the exit code."""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    try:
        payload = read(stdin.read())
    except InvalidInputError as error:
        print(f"workflow-essai : {error}", file=stderr)
        return INVALID_INPUT
    stdout.write(json.dumps(decide(payload), ensure_ascii=False) + "\n")
    return 0
