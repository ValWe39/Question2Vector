# Idea Intake: Renommer la commande principale « vector » en « qvector »

- **Slug**: renommer-vector-qvector
- **Created**: 2026-10-27
- **Source**: pasted text (session utilisateur, branche `004-upgrade-sortie`)
- **Type**: improvement

## Idea (as captured)

> Je souhaiterais remplacer le nom actuel de la commande principale
> ("vector") par "qvector" sans changer le reste de l'outil qui fonctionne
> très bien.

Contexte codebase relevé (lecture seule) : le nom de commande est défini
par l'entry point `vector = "question2vector.cli:main"` dans
`pyproject.toml:19` et par `prog="vector"` dans
`src/question2vector/cli.py:55` (docstring de module : « Ligne de commande
`vector` »). D'autres mentions existent vraisemblablement dans `README.md`,
les specs et les tests.

## Restated

Renommer l'exécutable CLI du projet, actuellement `vector`, en `qvector`, en
conservant l'intégralité du comportement et des fonctionnalités existants.

## Origin & Context

- **Raised by**: [NEEDS CLARIFICATION: qui a formulé la demande —
  utilisateur principal, mainteneur, tiers ?]
- **Trigger**: [NEEDS CLARIFICATION: conflit de nom avec un autre binaire
  `vector` sur le système, souci de cohérence avec le nom du projet
  `question2vector`, ou autre raison ?]

## First-Glance Unknowns

- [NEEDS CLARIFICATION: motivation du renommage (collision avec la CLI
  `vector` de Vector.dev ? alignement avec le nom du projet ?)]
- [NEEDS CLARIFICATION: faut-il conserver un alias de compatibilité
  `vector` → `qvector` ou le renommage est-il complet et sans transition ?]
- [NEEDS CLARIFICATION: périmètre exact des mentions à mettre à jour —
  entry point, `prog`, README, specs, tests, exemples, docs
  Prompts/Ressources ?]
- [NEEDS CLARIFICATION: la version publiée actuelle expose-t-elle
  `vector` à des utilisateurs externes, ce qui imposerait une note de
  migration / bump de version majeure ?]
- [NEEDS CLARIFICATION: impact sur les scripts, alias shell ou
  intégrations existants de l'utilisateur qui invoquent `vector`]
