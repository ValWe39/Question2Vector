# Data Model: feature 003-renommage-commande-qvector

**Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

## Impact sur le modèle de données

Aucun. La feature renomme l'interface console sans toucher aux données,
aux entités ni au format de sortie. Les entités définies par la feature
001 (`InputItem`, `OutputFileName`, `LlmModelRef`, etc. — cf.
`specs/001-text-vectorization/data-model.md`) et la sortie groupée
`Vector-2.0` (feature 002) restent strictement inchangées.

## Référence de l'interface renommée

- **Commande** : `qvector` (anciennement `vector`).
- **Invocation secondaire** : `python -m question2vector` (inchangée).
- **Arguments, options, bornes, codes de sortie, sortie console** :
  inchangés, cf. [contracts/cli.md](contracts/cli.md).

## Règles de validation

- Toute entrée, option, borne ou comportement accepté par `vector` doit
  l'être à l'identique par `qvector` (FR-001, FR-006 de la spec).
- Aucune structure de fichier de sortie ne change (`Vector-2.0`).
