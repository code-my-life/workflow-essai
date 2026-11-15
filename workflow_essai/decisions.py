"""The decisions of the trial workflow's commands, computed from their JSON input.

Every function here is pure but for `preparer`, whose sleep is injected: no file written, no network, nothing else.
An input field this module does not know is ignored.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any

SCHEMA_VERSION = 1
# How long `preparer` sleeps for an item marked `[lent]`: beyond the 60-second delay of its station.
SLOW_SECONDS = 90

REFUSE_MARK = "[refus]"
FAIL_MARK = "[echec]"
SLOW_MARK = "[lent]"


class InvalidInputError(ValueError):
    """An input the command cannot read: not JSON, not an object, a required field missing, or another schema."""


def _object(value: Any, name: str) -> dict:
    if not isinstance(value, dict):
        raise InvalidInputError(f"{name} doit être un objet JSON")
    return value


def _field(container: dict, name: str, kind: type | tuple[type, ...], where: str) -> Any:
    if name not in container:
        raise InvalidInputError(f"champ requis absent : {where}{name}")
    value = container[name]
    # bool is an int in Python: a number given as true or false is not a number.
    if not isinstance(value, kind) or (kind is int and isinstance(value, bool)):
        raise InvalidInputError(f"champ de type inattendu : {where}{name}")
    return value


def _payload(text: str) -> dict:
    try:
        data = json.loads(text)
    except ValueError as error:
        raise InvalidInputError(f"entrée illisible : {error}") from error
    data = _object(data, "l'entrée")
    if "schema_version" not in data:
        raise InvalidInputError("champ requis absent : schema_version")
    version = data["schema_version"]
    # Only the integer 1: neither true nor 1.0, which Python holds equal to it.
    if type(version) is not int or version != SCHEMA_VERSION:
        raise InvalidInputError(f"schema_version {version!r} inconnue, seule {SCHEMA_VERSION} est lue")
    return data


def read_intake(text: str) -> dict:
    """The intake input, validated: `{"schema_version": 1, "issue": {"number", "title", "labels", ...}}`."""
    data = _payload(text)
    issue = _object(_field(data, "issue", dict, ""), "issue")
    _field(issue, "number", int, "issue.")
    _field(issue, "title", str, "issue.")
    labels = _field(issue, "labels", list, "issue.")
    if not all(isinstance(label, str) for label in labels):
        raise InvalidInputError("issue.labels doit être une liste de noms")
    return data


def read_station(text: str) -> dict:
    """A station's input, validated: `{"schema_version": 1, "item": {"title", ...}, "answer": null | {...}}`."""
    data = _payload(text)
    item = _field(data, "item", dict, "")
    _field(item, "title", str, "item.")
    answer = data.get("answer")
    if answer is not None and not isinstance(answer, dict):
        raise InvalidInputError("answer doit être null ou un objet JSON")
    return data


def intake(payload: dict) -> dict:
    """Whether an issue becomes an item: refused when marked `[refus]` or typed, accepted under its number otherwise."""
    issue = payload["issue"]
    if issue["title"].startswith(REFUSE_MARK):
        return {"decision": "refuse", "reason": "titre marqué [refus]"}
    if any(label.startswith("type:") for label in issue["labels"]):
        return {"decision": "refuse", "reason": "une issue typée appartient à la factory"}
    return {"decision": "accept", "id": str(issue["number"]), "reason": "issue d'essai acceptée"}


def _gesture(payload: dict) -> str | None:
    answer = payload.get("answer")
    return answer.get("gesture") if isinstance(answer, dict) else None


def preparer(payload: dict, sleep: Callable[[float], None] = time.sleep) -> dict:
    """Prepare an item: an unblock always moves on, `[echec]` fails, `[lent]` outlasts the station's delay."""
    if _gesture(payload) == "unblock":
        note = payload["answer"].get("note")
        reason = f"relancé : {note}" if isinstance(note, str) and note else "relancé"
        return {"decision": "advance", "reason": reason, "to": "revue"}
    title = payload["item"]["title"]
    if FAIL_MARK in title:
        return {"decision": "fail", "reason": "préparation impossible : titre marqué [echec]", "to": None}
    if SLOW_MARK in title:
        sleep(SLOW_SECONDS)
    return {"decision": "advance", "reason": "élément préparé", "to": "revue"}


def revue(payload: dict) -> dict:
    """The owner's review: `valider` closes, `refaire` prepares again, anything else waits."""
    gesture = _gesture(payload)
    if gesture == "valider":
        return {"decision": "advance", "reason": "revue validée", "to": "clore"}
    if gesture == "refaire":
        return {"decision": "advance", "reason": "à refaire", "to": "preparer"}
    return {"decision": "wait", "reason": "en attente d'un geste connu", "to": None}


def clore(payload: dict) -> dict:
    """Close the item: the last station, after which the core ends it."""
    del payload
    return {"decision": "advance", "reason": "élément clos", "to": None}
