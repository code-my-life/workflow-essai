"""Refuse any mention of the core's agent runtime in the files tracked by git (AD-1 of the architecture).

A workflow's repository knows only the core. This check reads every tracked file, its path and its content, and
reports each line that names the runtime, in any case, with or without accents: `path:line: text`, line 0 for a path.
It exits with 1 when it finds one, with 0 otherwise. Only the bounded exceptions of AD-1 that hold for a workflow's
repository are allowed, declared below and nowhere else. The name itself is never written out in clear: it is built
when the script runs.

Usage: python3 scripts/check_runtime_absent.py [root]  (root: the repository to check, this one by default)
"""

from __future__ import annotations

import subprocess
import sys
import unicodedata
from pathlib import Path

# The runtime's name, built at run time so that no tracked file holds it in clear.
NAME = "her" + "mes"

# The bounded exceptions of AD-1 for a workflow's repository.
# Paths under these folders, and these exact files, are not read at all: the agent profiles, the decisions and the
# journal.
ALLOWED_FOLDERS = (f"{NAME}/profiles/", "docs/decisions/")
ALLOWED_FILES = ("docs/JOURNAL.md",)
# Names removed from a line before the search, in the one file that may hold them: the software factory's repository,
# cited by the conventions workflow inherited from the organization's template repository. Anywhere else, the name is
# refused like any other mention.
ALLOWED_NAMES_BY_FILE = {".github/workflows/conventions.yml": (f"{NAME}-software-factory",)}


def normalize(text: str) -> str:
    """The text without accents and in folded case, so that every spelling of the name matches."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).casefold()


def names_the_runtime(text: str, allowed_names: tuple[str, ...] = ()) -> bool:
    line = normalize(text)
    for allowed in allowed_names:
        line = line.replace(normalize(allowed), "")
    return normalize(NAME) in line


def tracked_files(root: Path) -> list[str]:
    listed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"], capture_output=True, text=True, check=True, encoding="utf-8"
    )
    return [path for path in listed.stdout.split("\0") if path]


def faults(root: Path) -> list[str]:
    """Every line of the tracked files under root that names the runtime, as `path:line: text`."""
    found = []
    for path in tracked_files(root):
        if path.startswith(ALLOWED_FOLDERS) or path in ALLOWED_FILES:
            continue
        if names_the_runtime(path):
            found.append(f"{path}:0: {path}")
        file = root / path
        if not file.is_file():
            continue
        allowed_names = ALLOWED_NAMES_BY_FILE.get(path, ())
        content = file.read_bytes().decode("utf-8", errors="replace")
        # Split on newlines only, so that the line numbers are those of git and the editors.
        for number, raw in enumerate(content.split("\n"), start=1):
            line = raw.removesuffix("\r")
            if names_the_runtime(line, allowed_names):
                found.append(f"{path}:{number}: {line.strip()}")
    return found


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    found = faults(root)
    for fault in found:
        print(fault)
    if found:
        print(f"{len(found)} mention(s) du runtime d'agents, interdites hors des exceptions d'AD-1", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
