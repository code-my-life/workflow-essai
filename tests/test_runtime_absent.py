import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "check_runtime_absent.py"

# The runtime's name, built here as in the script: no tracked file holds it in clear.
NAME = "her" + "mes"
ACCENTED = "Her" + "mès"


def _repository(tmp_path, files):
    """A git repository outside the clone, with the given files tracked."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    for path, content in files.items():
        file = tmp_path / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "--all"], check=True)
    return tmp_path


def _check(root):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True, check=False, timeout=30
    )


def test_a_file_naming_the_runtime_is_refused(tmp_path):
    root = _repository(
        tmp_path,
        {
            "clean.md": "rien à signaler\n",
            "accent.md": f"première ligne\nle runtime {ACCENTED} ici\n",
            "upper.py": f"# {NAME.upper()}\n",
            "plain.txt": f"sans accent : {NAME}\n",
            f"tools/{NAME}_bridge.py": "pass\n",
            "docs/JOURNAL.md.bak": f"{NAME}\n",
            "form-feed.md": f"un\fdeux\n{NAME}\n",
        },
    )
    ran = _check(root)
    assert ran.returncode == 1
    lines = ran.stdout.splitlines()
    assert f"accent.md:2: le runtime {ACCENTED} ici" in lines
    assert f"upper.py:1: # {NAME.upper()}" in lines
    assert f"plain.txt:1: sans accent : {NAME}" in lines
    assert f"tools/{NAME}_bridge.py:0: tools/{NAME}_bridge.py" in lines
    assert f"docs/JOURNAL.md.bak:1: {NAME}" in lines
    assert f"form-feed.md:2: {NAME}" in lines
    assert not any(line.startswith("clean.md") for line in lines)
    assert len(lines) == 6


def test_the_bounded_exceptions_are_allowed(tmp_path):
    root = _repository(
        tmp_path,
        {
            "docs/decisions/0001-socle.md": f"Le socle parle à {ACCENTED}.\n",
            "docs/JOURNAL.md": f"{NAME} redémarré\n",
            f"{NAME}/profiles/agent.yaml": f"runtime: {NAME}\n",
            ".github/workflows/conventions.yml": f"# from code-my-life/{NAME}-software-factory\n",
        },
    )
    ran = _check(root)
    assert ran.returncode == 0, ran.stdout
    assert ran.stdout == ""


def test_the_factory_repository_is_allowed_only_in_the_conventions_workflow(tmp_path):
    root = _repository(
        tmp_path,
        {
            ".github/workflows/conventions.yml": f"# from code-my-life/{NAME}-software-factory\n",
            "README.md": f"voir code-my-life/{NAME}-software-factory\n",
            ".github/workflows/ci.yml": f"# from code-my-life/{NAME}-software-factory\n",
        },
    )
    ran = _check(root)
    assert ran.returncode == 1
    lines = ran.stdout.splitlines()
    assert f"README.md:1: voir code-my-life/{NAME}-software-factory" in lines
    assert f".github/workflows/ci.yml:1: # from code-my-life/{NAME}-software-factory" in lines
    assert len(lines) == 2


def test_the_repository_names_no_runtime():
    ran = _check(REPO)
    assert ran.returncode == 0, ran.stdout
