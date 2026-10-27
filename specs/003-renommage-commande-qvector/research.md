# Research: feature 003-renommage-commande-qvector

**Date**: 2026-10-27 | **Input**: spec.md, assessment
`renommer-vector-qvector` (research.md, decision.md), inspection du dépôt.

Consolidation des décisions de conception. Aucun NEEDS CLARIFICATION ne
subsiste : la question de version a été tranchée en clarification le
2026-10-27 (rester en 0.1.0).

## Décisions

### Renommage complet, sans alias

- **Decision**: la commande s'appelle `qvector` ; aucun alias `vector`
  n'est conservé.
- **Rationale**: la collision de nom avec un autre outil de l'utilisateur
  est la cause même du problème ; un alias la perpétuerait pendant toute
  la période de transition et entretiendrait la confusion des deux
  scripts dans le venv.
- **Alternatives considered**: alias de transition déprécié (option B de
  l'assessment) ; contournement documentaire sans renommage (option C) —
  toutes deux écartées dans decision.md.

### Version du paquet inchangée

- **Decision**: rester en `0.1.0`, aucun incrément de version.
- **Rationale**: outil local non publié ; le renommage est traçable par
  l'historique git, une version n'apporte rien ici.
- **Alternatives considered**: bump mineur `0.2.0` (convention semver
  pré-1.0 pour changement cassant) ; bump majeur `1.0.0` — écartées par
  clarification utilisateur du 2026-10-27.

### Périmètre des mises à jour documentaires

- **Decision**: mettre à jour le README, le quickstart de la spec 001 et
  les contrats CLI des specs 001 et 002 ; ne pas réécrire les scénarios
  Given/When/When historiques ni le document d'archive
  `Prompts/PromptInit1.txt`.
- **Rationale**: les contrats sont la référence d'interface officielle ;
  les scénarios historiques et documents d'archive décrivent des états
  passés datés.
- **Alternatives considered**: mise à jour exhaustive de toutes les
  occurrences (churn inutile, rabbit hole identifié dans concept.md).

## Faits techniques établis (inspection du dépôt)

- Le nom de commande est défini par l'entry point
  `vector = "question2vector.cli:main"` (`pyproject.toml`,
  `[project.scripts]`) et par `prog="vector"` (`cli.py:55`).
- Les docstrings de module de `cli.py:1` et `config.py:20` mentionnent
  la commande `vector`.
- Aucun test n'invoque le binaire : tous importent `main` ; la suite
  pytest est insensible au renommage.
- Le CI n'invoque jamais la commande (lint et audits uniquement).
- Le renommage de l'entry point prend effet après réinstallation du
  paquet dans le venv ; l'ancien script `vector` doit être éliminé
  (supprimé par la réinstallation ou manuellement).
- `python -m question2vector` reste fonctionnel et indépendant du nom
  de l'entry point.
- Le schéma de sortie `Vector-2.0` est un nom de format : il ne fait
  pas partie du périmètre.
