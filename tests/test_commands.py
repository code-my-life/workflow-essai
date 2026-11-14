import json
import re
import subprocess
import sys
from pathlib import Path

from workflow_essai import decisions


def _issue(number=7, title="Essai", labels=()):
    return {
        "schema_version": 1,
        "issue": {
            "repo": "code-my-life/workflow-essai",
            "number": number,
            "url": f"https://github.com/code-my-life/workflow-essai/issues/{number}",
            "title": title,
            "body": "",
            "labels": list(labels),
        },
    }


def test_intake_accepts_an_ordinary_issue_under_its_number():
    accepted = {"decision": "accept", "id": "7", "reason": "issue d'essai acceptée"}
    assert decisions.intake(_issue()) == accepted
    assert decisions.intake(_issue(labels=["test"])) == accepted


def test_intake_refuses_a_title_marked_refus():
    refused = {"decision": "refuse", "reason": "titre marqué [refus]"}
    assert decisions.intake(_issue(title="[refus] Essai")) == refused
    assert decisions.intake(_issue(title="[refus] Essai", labels=["type:fonctionnalite"])) == refused


def test_intake_refuses_an_issue_with_a_type_label():
    assert decisions.intake(_issue(labels=["test", "type:fonctionnalite"])) == {
        "decision": "refuse",
        "reason": "une issue typée appartient à la factory",
    }


def _station(title="essai:7 · Essai", answer=None, station="preparer"):
    return {
        "schema_version": 1,
        "item": {"id": "essai:7", "issue": "https://github.com/code-my-life/workflow-essai/issues/7", "title": title},
        "station": station,
        "attempt": 1,
        "answer": answer,
    }


class _Sleep:
    """Records the delays asked for instead of sleeping."""

    def __init__(self):
        self.asked = []

    def __call__(self, seconds):
        self.asked.append(seconds)


PREPARED = {"decision": "advance", "reason": "élément préparé", "to": "revue"}


def test_preparer_sends_an_ordinary_item_to_the_review():
    sleep = _Sleep()
    assert decisions.preparer(_station(), sleep=sleep) == PREPARED
    assert sleep.asked == []


def test_preparer_fails_an_item_marked_echec():
    sleep = _Sleep()
    assert decisions.preparer(_station(title="essai:7 · Essai [echec]"), sleep=sleep) == {
        "decision": "fail",
        "reason": "préparation impossible : titre marqué [echec]",
        "to": None,
    }
    assert sleep.asked == []


REPO = Path(__file__).resolve().parent.parent


def _station_timeout(key):
    """The `timeout_seconds` of a station, read from the manifest the core plugs in."""
    manifest = json.loads((REPO / "workflow-manifest.json").read_text(encoding="utf-8"))
    (station,) = [station for station in manifest["stations"] if station["key"] == key]
    return station["timeout_seconds"]


def test_preparer_outlasts_its_delay_for_an_item_marked_lent():
    sleep = _Sleep()
    assert decisions.preparer(_station(title="essai:7 · [lent] Essai"), sleep=sleep) == PREPARED
    assert sleep.asked == [90]
    assert sleep.asked[0] > _station_timeout("preparer")


def test_preparer_moves_on_after_an_unblock():
    sleep = _Sleep()
    for title in ("essai:7 · Essai", "essai:7 · [echec] Essai", "essai:7 · [lent] Essai"):
        answer = {"gesture": "unblock", "note": "corrigé"}
        assert decisions.preparer(_station(title=title, answer=answer), sleep=sleep) == {
            "decision": "advance",
            "reason": "relancé : corrigé",
            "to": "revue",
        }
    for answer in ({"gesture": "unblock"}, {"gesture": "unblock", "note": ""}, {"gesture": "unblock", "note": None}):
        assert decisions.preparer(_station(answer=answer), sleep=sleep)["reason"] == "relancé"
    assert sleep.asked == []


def test_revue_validates_redoes_or_waits():
    waiting = {"decision": "wait", "reason": "en attente d'un geste connu", "to": None}
    assert decisions.revue(_station(answer={"gesture": "valider", "note": None}, station="revue")) == {
        "decision": "advance",
        "reason": "revue validée",
        "to": "clore",
    }
    assert decisions.revue(_station(answer={"gesture": "refaire", "note": "encore"}, station="revue")) == {
        "decision": "advance",
        "reason": "à refaire",
        "to": "preparer",
    }
    assert decisions.revue(_station(answer={"gesture": "ouvrir", "note": None}, station="revue")) == waiting
    assert decisions.revue(_station(answer=None, station="revue")) == waiting


def test_clore_ends_the_item():
    assert decisions.clore(_station(station="clore")) == {"decision": "advance", "reason": "élément clos", "to": None}


# One sample input per command, with an unknown field the command must ignore.
SAMPLES = {
    "intake": {**_issue(), "unknown": True},
    "preparer": {**_station(), "unknown": True},
    "revue": {**_station(answer={"gesture": "valider", "note": None}, station="revue"), "unknown": True},
    "clore": {**_station(station="clore"), "unknown": True},
}


def _launch(name, text):
    return subprocess.run(
        [sys.executable, f"commands/{name}.py"],
        input=text,
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
        timeout=30,
    )


def _status():
    return subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=REPO, check=True).stdout


def _valid_for_the_core(name, decision):
    """The rules the core applies to a command's decision, copied by hand from `workflow_core/model/decision.py` of
    code-my-life/workflow-core (`IntakeDecision` and `Decision`), since this repository depends on nothing. The copy
    is stricter than the core on one point: an unknown field, which the core ignores, is refused here. A change of
    those rules in the core must be copied here."""
    if name == "intake":
        assert set(decision) <= {"decision", "id", "reason"}
        assert decision["decision"] in {"accept", "refuse"}
        if decision["decision"] == "accept":
            assert re.fullmatch(r"[^\s/:]+", decision["id"])
        else:
            assert decision["reason"].strip()
    else:
        assert set(decision) <= {"decision", "reason", "to"}
        assert decision["decision"] in {"advance", "wait", "fail"}
        assert isinstance(decision["reason"], str)
        assert decision["to"] is None or isinstance(decision["to"], str)


def test_each_command_prints_one_decision_and_changes_nothing():
    expected = {
        "intake": decisions.intake(SAMPLES["intake"]),
        "preparer": decisions.preparer(SAMPLES["preparer"]),
        "revue": decisions.revue(SAMPLES["revue"]),
        "clore": decisions.clore(SAMPLES["clore"]),
    }
    before = _status()
    for name, sample in SAMPLES.items():
        first = _launch(name, json.dumps(sample))
        second = _launch(name, json.dumps(sample))
        assert first.returncode == 0, first.stderr
        assert second.returncode == 0, second.stderr
        assert first.stdout == second.stdout
        lines = first.stdout.splitlines()
        assert len(lines) == 1
        decision = json.loads(lines[0])
        assert decision == expected[name]
        _valid_for_the_core(name, decision)
    assert _status() == before


def test_an_unreadable_input_exits_with_code_2():
    station = _station()
    del station["item"]
    issue = _issue()
    del issue["issue"]["title"]
    unreadable = {
        "intake": ["pas du JSON", "[1, 2]", json.dumps(issue), json.dumps({**_issue(), "schema_version": 2})],
        "preparer": ["{", '"texte"', json.dumps(station), json.dumps({**_station(), "schema_version": 2})],
        "revue": [
            "",
            "null",
            json.dumps({"item": {"title": "x"}}),
            json.dumps({**_station(), "schema_version": 2}),
            json.dumps({**_station(), "schema_version": 1.0}),
            json.dumps({**_station(), "schema_version": True}),
        ],
        "clore": ["}", "42", json.dumps(station), json.dumps({**_station(), "schema_version": 2})],
    }
    for name, texts in unreadable.items():
        for text in texts:
            ran = _launch(name, text)
            assert ran.returncode == 2, (name, text)
            assert ran.stdout == "", (name, text)
            assert ran.stderr.strip(), (name, text)
