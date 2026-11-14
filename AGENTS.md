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
| Aucune mention du runtime | `uv run python scripts/check_runtime_absent.py` (code 0 attendu) |
| Une commande à la main | `echo '<entrée JSON>' \| uv run python commands/intake.py` (de même `preparer`, `revue`, `clore`) |

## Conventions

- Issues, branches et pull requests suivent les types de la software factory : un modèle d'issue de l'organisation par
  type, une branche `<préfixe>/<n° de l'issue>-<sujet>`, et le workflow « Conventions », qui juge chaque pull request.
- Aucun fichier ne nomme le runtime d'agents du socle : ce dépôt ne connaît que le socle. Le script
  `scripts/check_runtime_absent.py`, lancé par la CI, le vérifie sur chaque fichier suivi par git, dans son contenu et
  son chemin, en toute casse, avec ou sans accent. Ses seules exceptions, déclarées en tête du script, sont celles
  d'AD-1 : le dossier des profils d'agent, les décisions de `docs/decisions/`, le journal `docs/JOURNAL.md` et le nom
  du dépôt de la software factory, admis dans `.github/workflows/conventions.yml` seulement. Ni le script ni ses
  tests n'écrivent le nom en clair : ils le forment à l'exécution.
- Les commandes de `commands/` lisent un objet JSON sur l'entrée standard et écrivent une seule décision JSON sur la
  sortie standard ; leurs messages vont sur la sortie d'erreur. Elles n'écrivent aucun fichier, n'appellent ni le
  réseau, ni GitHub, ni le runtime, et la décision se calcule dans le paquet `workflow_essai`. Une entrée illisible ou
  de `schema_version` autre que 1 les fait sortir avec le code 2, sans rien sur la sortie standard.
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
- `workflow-manifest.json` : le manifeste que le socle branche ; il suit le contrat de l'issue
  `code-my-life/workflow-essai#1` octet pour octet.
- `workflow-sheet.json` : la fiche qui dessine les stations dans factory-live.
- `scripts/check_runtime_absent.py` : le contrôle d'AD-1 et sa liste d'exceptions.
