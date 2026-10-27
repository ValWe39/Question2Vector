# Problem Definition: Collision du nom de commande « vector » avec un autre outil

- **Slug**: renommer-vector-qvector
- **Created**: 2026-10-27
- **Inputs used**: intake.md, research.md, user input

## Problem Statement

L'utilisateur maintient sur sa machine un autre outil qui expose lui aussi une
commande nommée `vector`. La coexistence des deux commandes de même nom sur le
PATH (notamment via le script `.venv\Scripts\vector` de ce projet) a déjà
provoqué des erreurs d'exécution : la mauvaise commande est invoquée selon le
contexte d'activation, et l'utilisateur ne peut pas utiliser les deux outils de
manière fiable dans un même environnement.

## Affected Users & Stakeholders

- **Users**: l'utilisateur unique de Question2Vector (également mainteneur) —
  il subit des erreurs concrètes et récurrentes quand les deux outils
  cohabitent sur le PATH ou dans le même shell.
- **Stakeholders**: le mainteneur (même personne) — décide du périmètre du
  renommage et de la politique de compatibilité.

## Goals

- Pouvoir invoquer cet outil sans ambiguïté avec un nom de commande qui
  n'entre plus en collision avec l'autre outil de l'utilisateur.
- Éliminer les erreurs déjà constatées liées à la confusion des deux
  commandes `vector`.
- Conserver l'intégralité du comportement actuel de l'outil (aucune
  régression fonctionnelle).

## Non-Goals

- Renommer le paquet Python `question2vector` ou les modules internes.
- Renommer le schéma de sortie JSON `Vector-2.0` (nom de format, hors
  périmètre).
- Ajouter de nouvelles fonctionnalités à la CLI (options, arguments).
- Résoudre le problème côté autre outil (le renommage ne concerne que ce
  projet).

## Success Metrics

- La commande `qvector` fonctionne après réinstallation dans le venv, et
  `vector` n'est plus résolu vers cet outil (qualitatif, signal: exit code
  ou message d'erreur de l'autre outil quand pertinent).
- Aucun test de la suite existante n'est modifié pour le comportement
  (baseline: suite verte actuelle) et reste vert.
- Aucune occurrence résiduelle du nom de commande `vector` dans la
  documentation courante (README) après le changement (baseline: ≥ 8
  occurrences aujourd'hui — cf. research.md).

## Cost of Inaction

Les erreurs déjà observées se reproduisent à chaque usage simultané ou
rapproché des deux outils : mauvaise commande résolue par le PATH, appels
ratés, frustration récurrente. La fiabilité perçue de l'outil se dégrade,
sans espoir de résolution spontanée puisque les deux noms sont figés.

## Open Questions

- [NEEDS CLARIFICATION: faut-il conserver un alias de compatibilité
  `vector` → `qvector` (transi- tion) ou un remplacement complet ? —
  noter qu'un alias perpétuerait la collision]
- [NEEDS CLARIFICATION: faut-il mettre à jour les specs historiques
  (001/002, contrats CLI) ou seulement la documentation courante
  (README) ?]
- [NEEDS CLARIFICATION: l'autre outil est-il distribué avec un script
  `vector` dans le même venv, sur le PATH global, ou les deux ? — pour
  cibler la vérification de la disparition de la collision]
