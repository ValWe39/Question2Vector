# Implementation Plan: 003-renommage-commande-qvector

**Branch**: `005-changement-nom-commande` | **Date**: 2026-10-27 |
**Spec**: [spec.md](spec.md)

**Input**: Feature specification from
`/specs/003-renommage-commande-qvector/spec.md`

## Summary

Renommer la commande console de l'outil : `vector` devient `qvector`.
Remplacement complet, sans alias de compatibilité, sans aucun changement
de comportement (options, sorties, schéma `Vector-2.0` inchangés).
Approche technique issue de l'assessment `renommer-vector-qvector`
(decision GO, option A) : renommer l'entry point dans `pyproject.toml`,
le nom de programme affiché par l'analyseur d'arguments, les docstrings
concernées, puis la documentation ; réinstaller le paquet dans le venv.

## Technical Context

**Language/Version**: Python 3.11+ (`requires-python = ">=3.11"`)

**Primary Dependencies**: `mistralai>=1.0.0`, `python-dotenv>=1.0.0` ;
stdlib : `argparse` (CLI), `json`. Aucune nouvelle dépendance.

**Storage**: fichiers JSON de sortie (dossier `output/`), inchangé.

**Testing**: `pytest` (tests unitaires et d'intégration, `tests/`).
Les tests importent `question2vector.cli.main` sans invoquer le
binaire : la suite est insensible au renommage.

**Target Platform**: machine locale de l'utilisateur (Windows, venv),
Python multiplateforme.

**Project Type**: cli (point d'entrée console unique, renommé).

**Performance Goals**: sans objet (aucun changement de comportement).

**Constraints**:

- zéro changement fonctionnel : mêmes options, mêmes sorties ;
- pas d'alias `vector` (il perpétuerait la collision) ;
- version du paquet inchangée (0.1.0, clarification du 2026-10-27) ;
- documentation markdown conforme aux hooks CI (lignes ≤ 80
  caractères, pas de mot-clé de service cloud ni de mesure d'usage).

**Scale/Scope**: outil mono-utilisateur, non publié.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Statut | Détail |
|----------|--------|--------|
| I. Isolation des secrets | Pass | Aucun secret manipulé ; rien ne change |
| II. Local-first | Pass | Tout reste local ; aucun service introduit |
| III. Open-source sans trackers | Pass | Aucune dépendance ajoutée |
| IV. Simplicité (YAGNI) | Pass | Renommage minimal, sans alias |

Re-check post Phase 1 : Pass. Aucune violation à justifier.

## Project Structure

### Documentation (this feature)

```text
specs/003-renommage-commande-qvector/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── cli.md           # Contrat CLI renommé (delta vs 001/002)
└── tasks.md             # Phase 2 output (/speckit-tasks - NOT created yet)
```

### Source Code (repository root)

```text
pyproject.toml                     # [project.scripts] : vector -> qvector
src/question2vector/
├── cli.py                         # prog="vector" -> "qvector" + docstring
└── config.py                      # docstring : mention de la commande
tests/
├── integration/                   # inchangé (importe main, pas le binaire)
└── unit/                          # inchangé
README.md                          # exemples d'usage + note de migration
specs/001-text-vectorization/
├── contracts/cli.md               # nom de commande dans le contrat
└── quickstart.md                  # exemples d'invocation
specs/002-sortie-tableau-json/
└── contracts/cli.md               # nom de commande dans le contrat
```

**Structure Decision**: aucune structure nouvelle. Le renommage
touche des points existants en place ; le paquet, les modules et
l'arborescence restent identiques.
