# workflow-essai

Le workflow d'essai du socle `code-my-life/workflow-core`, de clé `essai`. Le socle le branche par un manifeste JSON à
la racine de ce dépôt, et lance ses commandes avec `uv run --directory <ce dépôt>` : chacune lit une entrée JSON sur
l'entrée standard et rend une décision JSON sur la sortie standard. Il sert à prouver le moteur du socle sans toucher
la factory ni le studio. Il n'est pas inscrit dans la software factory.

## Commandes

| Quoi | Commande |
|---|---|
| Installer | `uv sync --locked` |
| Tous les tests | `uv run pytest` |
| Un seul fichier de test | `uv run pytest tests/test_paquet.py` |
| Types | aucun pour l'instant |
| Build | aucun |
| Démarrer | aucun : le socle lance les commandes |
| Bout en bout | aucun |
| Lint et format | `uv run ruff check` et `uv run ruff format --check` |

## Conventions

- Issues, branches et pull requests suivent les types de la software factory : un modèle d'issue de l'organisation par
  type, une branche `<préfixe>/<n° de l'issue>-<sujet>`, et le workflow « Conventions », qui juge chaque pull request.
- Aucun fichier ne nomme le runtime d'agents du socle : ce dépôt ne connaît que le socle.
- Python 3.12, uv 0.12.3, versions figées dans `pyproject.toml` et `uv.lock`.
- Aucun secret dans le dépôt, qui est public.
- Les commentaires du code sont en anglais. Aucun nom de personne dans un commentaire ou un titre de test.
- Les décisions vivent dans `docs/decisions/`, une par fichier.

## Échecs connus

Aucun.

## Interdits

- Affaiblir ou retirer une assertion, allonger un timeout.
- Pousser sur main, forcer un push, contourner un hook git.

## Chemins sensibles

- `.github/workflows/ci.yml` : les contrôles du dépôt.
- `pyproject.toml` et `uv.lock` : les versions figées.
