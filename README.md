# workflow-essai

Le workflow d'essai du socle [workflow-core](https://github.com/code-my-life/workflow-core) : une ligne de production
jetable, de clé `essai`, qui prouve qu'un workflow se branche sur le socle par un manifeste et des commandes, sans
toucher les autres workflows. Il reste ensuite comme test vivant de ce branchement.

## Ce que le dépôt déclare

- `workflow-manifest.json` : la clé `essai`, la fiche `workflow-sheet.json`, ce dépôt comme seul dépôt des issues, la
  commande `intake`, trois stations (`preparer`, une commande ; `revue`, une attente du propriétaire ; `clore`, une
  commande), chacune avec un délai de 60 secondes, et les gestes `valider`, `refaire` (un commentaire
  `/essai <geste> [note]` dans l'issue de l'élément) et `ouvrir` (ouvrir une issue dans ce dépôt).
- `commands/` : les quatre commandes que le socle lance. Chacune lit une entrée JSON sur l'entrée standard et rend une
  décision JSON sur la sortie standard, sans rien écrire ni appeler d'autre.

Les marques de titre servent aux preuves du socle :
- `[refus]` au début du titre de l'issue : `intake` la refuse ;
- `[echec]` dans le titre : `preparer` rend un échec ;
- `[lent]` dans le titre : `preparer` dort 90 secondes, au-delà de son délai.

Une issue au label `type:*` est refusée : elle appartient à la factory.

## Démarrer

```
uv sync --locked
uv run pytest
uv run ruff check
```

## Contribuer

Ouvrez une issue avec l'un des modèles de l'organisation. Ce dépôt n'est pas inscrit dans la software factory de
Code My Life : son contenu se fait en séance de travail du propriétaire, par pull request vers main.

## Licence

MIT, voir `LICENSE`.
