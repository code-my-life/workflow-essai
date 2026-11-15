import itertools
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _load(name):
    return json.loads((REPO / name).read_text(encoding="utf-8"))


def test_the_manifest_declares_the_trial_workflow():
    manifest = _load("workflow-manifest.json")
    assert manifest["schema_version"] == 1
    assert manifest["key"] == "essai"
    assert manifest["sheet"] == "workflow-sheet.json"
    assert manifest["issues_repos"] == ["code-my-life/workflow-essai"]
    assert manifest["intake"] == {"command": ["python", "commands/intake.py"], "timeout_seconds": 60}
    assert [(station["key"], station["nature"]) for station in manifest["stations"]] == [
        ("preparer", "code"),
        ("revue", "owner"),
        ("clore", "code"),
    ]
    for station in manifest["stations"]:
        assert station["command"] == ["python", f"commands/{station['key']}.py"]
        assert station["timeout_seconds"] == 60
    assert manifest["gestures"] == [
        {"name": "valider", "kind": "comment"},
        {"name": "refaire", "kind": "comment"},
        {"name": "ouvrir", "kind": "issue", "repo": "code-my-life/workflow-essai"},
    ]


def test_every_declared_command_exists():
    manifest = _load("workflow-manifest.json")
    commands = [manifest["intake"]["command"], *(station["command"] for station in manifest["stations"])]
    for command in commands:
        assert command[0] == "python"
        assert (REPO / command[1]).is_file(), command


def test_the_sheet_draws_the_stations_of_the_manifest():
    manifest = _load("workflow-manifest.json")
    sheet = _load(manifest["sheet"])
    keys = [station["key"] for station in manifest["stations"]]
    assert [station["key"] for station in sheet["stations"]] == keys
    assert [station["label"] for station in sheet["stations"]] == ["Préparer", "Revue", "Clore"]
    screen_kind = {"code": "script", "owner": "owner"}
    for drawn, declared in zip(sheet["stations"], manifest["stations"], strict=True):
        assert drawn["kind"] == screen_kind[declared["nature"]]
    assert [(edge["from"], edge["to"]) for edge in sheet["edges"]] == list(itertools.pairwise(keys))
    assert sheet["item"] == {"type": "essai", "label": "Essai"}
    assert "agents" not in sheet
