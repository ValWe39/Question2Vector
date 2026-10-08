# Implementation Plan: Sortie tableau JSON regroupee

**Branch**: `004-upgrade-sortie` | **Date**: 2026-10-08 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from `/specs/002-sortie-tableau-json/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its
definition describes the execution workflow.

## Summary

Remplacer la sortie objet `Vector-1.0` (un JSON par entree) par un
livrable tableau `Vector-2.0` : regroupement par defaut de toutes
les entrees d'un run dans `sortie.json` (suffixe d'unicite en cas de
conflit), option `--ungroup on` pour restaurer une sortie par
entree, et un enregistrement d'echec a trois champs pour chaque
entree en echec, quel que soit le mode de livraison.

## Technical Context

**Language/Version**: Python >= 3.11 (pyproject.toml ; venv local
en 3.14)

**Primary Dependencies**: mistralai >= 1.0.0, python-dotenv >= 1.0.0
(aucune dependance nouvelle)

**Storage**: fichiers JSON locaux dans le dossier de sortie
(`output/` par defaut, configurable via `--output-folder`)

**Testing**: pytest, tests unitaires et d'integration, client
Mistral fictif (`tests/conftest.py`)

**Target Platform**: CLI locale multiplateforme, Windows PowerShell
en priorite (cf. README)

**Project Type**: cli

**Performance Goals**: dizaines d'entrees par run, ecriture du
livrable en une operation (volumes modestes, cf. spec Assumptions)

**Constraints**: local-first (constitution II), appels reseaux
limites a l'API Mistral (aucun de nouveau), markdownlint 80
colonnes sur les fichiers .md, hooks pre-commit actifs

**Scale/Scope**: 3 modules touches (`output.py`, `cli.py`,
`config.py`), 4 fichiers de tests, 2 documents de reference a
mettre a jour (README, contrat CLI de la spec 001)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1
design.*

| Principe | Verdict | Verifie |
| ------- | ------ | ------- |
| I. Isolation des secrets | PASS | jamais de cle dans la sortie |
| II. Local-first | PASS | livrable local, aucun service externe |
| III. Open-source sans trackers | PASS | aucune dependance nouvelle |
| IV. Simplicite (YAGNI) | PASS | option unique justifiee |
| Path isolation | PASS | dossier resolu depuis les options |
| Network surface | PASS | aucun appel reseau nouveau |
| Data retention | PASS | aucune copie cachee |

Re-evaluation post Phase 1 : PASS — le design ne touche ni aux
secrets, ni au reseau, ni aux dependances ; aucun marqueur de
complexite a justifier (section Suivi de complexite vide).

## Project Structure

### Documentation (this feature)

```text
specs/002-sortie-tableau-json/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── cli.md
└── tasks.md             # Phase 2 output (/speckit-tasks, pas ici)
```

### Source Code (repository root)

```text
src/question2vector/
├── cli.py           # options, orchestration, bilan console
├── output.py        # enregistrements Vector-2.0, nommage, ecriture
├── config.py        # options normalisees (champ ungroup)
├── inputs.py        # detection des entrees (inchange)
├── embedding.py     # lots et reprises (inchange)
├── reformulation.py
└── mistral_client.py

tests/
├── unit/
│   ├── test_output.py    # schema Vector-2.0, nommage, echecs
│   └── test_config.py    # validation de --ungroup
└── integration/
    ├── test_single.py    # entree unique, tableau a 1 element
    └── test_multi.py     # groupe, ungroup, echec partiel
```

**Structure Decision**: la structure existante a package unique est
reutilisee telle quelle ; seuls `output.py`, `cli.py` et `config.py`
evoluent, aucun fichier nouveau hors spec.

## Suivi de complexite

> **Fill ONLY if Constitution Check has violations that must be
> justified**

Aucune violation : tableau vide, aucune justification requise.
