# workflow-essai

Le workflow d'essai du socle [workflow-core](https://github.com/code-my-life/workflow-core) : une ligne de production
jetable, de clé `essai`, qui prouve qu'un workflow se branche sur le socle par un manifeste et des commandes, sans
toucher les autres workflows. Il reste ensuite comme test vivant de ce branchement.

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
