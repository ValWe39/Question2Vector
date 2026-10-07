# Implementation Plan: vectorisation via embeddings Mistral (`vector`)

**Branch**: `002-coeur-fct`

**Date**: 2026-10-07

**Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-text-vectorization/spec.md`

## Summary

L'outil `vector` est un CLI Python qui vectorise une chaîne de caractères, un
fichier `.txt`/`.md`, un dossier, ou un mélange de ces éléments, via l'API
d'embedding Mistral (`mistral-embed` par défaut, 1024 dimensions). Chaque
élément produit un JSON normalisé (`Vector-1.0`) dans un dossier de sortie
local (`output/` par défaut). En option (`--reformule on`), les entrées courtes
de type question (≤ 500 caractères) sont d'abord reformulées par un LLM Mistral
(mistral-small-latest par défaut, JSON mode) ; le vecteur porte alors sur la
reformulation. Les requêtes d'embedding sont regroupées par batch (25 par
défaut) avec retry exponentiel (3/6/12 s par défaut). L'approche technique
retenue : SDK officiel `mistralai`, argparse (stdlib), sortie fichier JSON,
aucune persistance au-delà des fichiers de sortie.

## Technical Context

**Language/Version**: Python 3.11+ (justifié dans [research.md](research.md))

**Primary Dependencies**: `mistralai` (SDK officiel Mistral, appels embeddings
et chat), `python-dotenv` (lecture du `.env` local). Dev : `pytest`.

**Storage**: fichiers locaux uniquement — JSON de sortie dans `output/` (ou
dossier fourni par `--output-folder`). Aucune base de données.

**Testing**: `pytest` avec `unittest.mock` standard ; le client Mistral est
enveloppé dans une interface fine injectable, donc mockable sans dépendance
supplémentaire ni réseau.

**Target Platform**: CLI locale multi-OS (Windows, Linux, macOS) ; réseau
requis uniquement pour les appels API Mistral explicites.

**Project Type**: cli (point d'entrée console `vector`).

**Performance Goals**: un élément unique vectorisé en moins de 10 s sans
reformulation, moins de 30 s avec (SC-002) ; batchs d'embedding de 25 par
défaut pour le multi-input.

**Constraints**: local-first (constitution II) — seuls appels sortants
autorisés : API Mistral ; clé `MISTRAL_API_KEY` jamais copiée, affichée ni
journalisée (constitution I) ; fonctionnalité locale (parsing, écriture)
utilisable hors-ligne.

**Scale/Scope**: 6 exemples du dossier `Examples/` comme jeu de validation ;
multi-input typique de quelques dizaines de fichiers, batchs jusqu'à 100.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Isolation des secrets** — Conforme : clé chargée de `.env`
  (git-ignoré, vérifié) via `MISTRAL_API_KEY` ; jamais logguée ni
  écrite ; `.env.example` committé avec placeholder uniquement.
- **II. Local-first** — Conforme : entrées, sorties et journaux
  100 % locaux ; appels sortants limités à l'URL de l'API Mistral
  (Network Surface).
- **III. Open-source sans trackers** — Conforme* : dépendances
  `mistralai`, `python-dotenv` (MIT), `pytest` (dev) ; licences et
  trackers vérifiés par le job `audit` (pip-audit) du workflow
  `diagnostic.yml`.
- **IV. Simplicité (YAGNI)** — Conforme : argparse stdlib, un seul
  paquet Python, modules fins, pas de plugins ni de serveur.

(*Vérification pip-audit déjà automatisée par la constitution ; tâche
d'implémentation incluse dans tasks.md pour confirmer les licences.)

Aucune violation : la section Suivi de complexité reste vide.

## Project Structure

### Documentation (this feature)

```text
specs/001-text-vectorization/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── cli.md           # Contrat d'interface CLI (commande `vector`)
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
pyproject.toml            # Packaging + dépendances + entry point `vector`
src/
└── question2vector/
    ├── __init__.py
    ├── __main__.py       # python -m question2vector
    ├── cli.py            # argparse, validation des bornes, codes de sortie
    ├── config.py         # Options normalisées + clé API depuis l'environnement
    ├── inputs.py         # Détection chaîne/fichier/dossier, lecture .txt/.md
    ├── reformulation.py  # Prompt constant + appel LLM + parsing JSON strict
    ├── embedding.py      # Appels embeddings + batching + retry exponentiel
    ├── output.py         # Nommage 7 caractères, conflits -X, écriture JSON
    └── mistral_client.py # Enveloppe fine injectable du SDK `mistralai`

tests/
├── unit/                 # inputs, output, config, retry, parsing reformulation
└── integration/          # flux bout-en-bout avec client mocké

.env.example              # Template avec placeholder YOUR_API_KEY
```

**Structure Decision**: projet unique en `src` layout, entry point console
`vector` déclaré dans `pyproject.toml`. Le SDK Mistral est isolé dans
`mistral_client.py` pour que le reste du code soit testable sans réseau ;
toutes les autres dépendances sont la stdlib.

## Suivi de complexité

> Aucune violation de la constitution à justifier — section vide.
