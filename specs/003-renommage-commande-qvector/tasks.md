---
description: "Task list for feature 003-renommage-commande-qvector"
---

# Tasks: 003-renommage-commande-qvector

**Input**: Design documents from `/specs/003-renommage-commande-qvector/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/cli.md, quickstart.md

**Tests**: aucune nouvelle suite de test demandée — la validation s'appuie
sur la suite pytest existante (qui ne doit pas être modifiée) et sur les
scénarios du quickstart, avec les questions réelles ci-dessous.

**Organization**: tâches groupées par user story. Entrées réelles de
validation fournies par l'utilisateur (remplacer les exemples de test) :

1. "Le crédit impôt recherche (CIR) est-il efficace ?"
2. "Le crédit impôt recherche (CIR) remplit il ses objectifs ?
   atteint il son but ?"
3. "Que représente le crédit impôt recherche (CIR) dans les dépenses
   de l'état ? quel poids occupe t-il dans le budget ? quelles part
   représente-t-il dans les aides aux entreprises ?"
4. "Les voisins de la France disposent ils d'un dispositif équivalent
   au crédit impôt recherche (CIR) ? Pour quel résultats dans le monde ?"

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallélisable (fichiers différents, pas de dépendance)
- **[Story]**: user story de la spec (US-1, US-2, US-3)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: état de référence avant tout changement

- [X] T001 Vérifier l'état de référence : lancer `pytest` dans tests/,
  confirmer la suite verte et noter le nombre de tests (aucun test ne
  devra être modifié par la suite)
- [X] T002 Inventorier les occurrences du nom de commande `vector`
  dans pyproject.toml, src/question2vector/cli.py,
  src/question2vector/config.py, README.md,
  specs/001-text-vectorization/ et specs/002-sortie-tableau-json/
  (base de vérification pour T014)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: point d'impact unique du renommage côté paquet

- [X] T003 Renommer l'entry point dans pyproject.toml :
  `[project.scripts]` `vector = "question2vector.cli:main"` devient
  `qvector = "question2vector.cli:main"` (version inchangée : 0.1.0,
  clarification du 2026-10-27)

**Checkpoint**: le paquet déclare `qvector` ; les user stories peuvent
démarrer.

---

## Phase 3: User Story 1 - Invoquer l'outil sous son nouveau nom (P1) — MVP

**Goal**: `qvector` fonctionne à l'identique de `vector` (FR-001,
FR-003, FR-006, FR-007)

**Independent Test**:
`qvector --help` affiche le nouveau nom ; puis, avec les entrées réelles
fournies par l'utilisateur :

```bash
qvector --reformule on "Le crédit impôt recherche (CIR) est-il efficace ?"
qvector "Le crédit impôt recherche (CIR) remplit il ses objectifs ?
atteint il son but ?" "Que représente le crédit impôt recherche (CIR)
dans les dépenses de l'état ? quel poids occupe t-il dans le budget ?
quelles part représente-t-il dans les aides aux entreprises ?"
```

Attendu : sortie groupée `Vector-2.0` dans `output/sortie.json`, un
enregistrement par entrée dans l'ordre des arguments, code de sortie 0 ;
`python -m question2vector --help` fonctionne toujours ; `pytest` vert.

### Implementation for User Story 1

- [X] T004 [US-1] Mettre à jour le nom de programme dans
  src/question2vector/cli.py : `prog="vector"` (ligne 55) devient
  `prog="qvector"`
- [X] T005 [P] [US-1] Mettre à jour les docstrings : module de
  src/question2vector/cli.py (ligne 1, « Ligne de commande `vector` »)
  et classe dans src/question2vector/config.py (ligne 20, « commande
  `vector` ») → `qvector`
- [X] T006 [US-1] Réinstaller le paquet dans le venv (`pip install -e .`)
  puis vérifier que le script `qvector` est présent et que l'ancien
  script `vector` a disparu des scripts du venv (sinon le supprimer
  manuellement, ex. `.venv/Scripts/vector.exe`)
- [X] T007 [US-1] Valider la story 1 : exécuter l'independent test
  ci-dessus puis `pytest` (suite verte, zéro test modifié)

**Checkpoint**: `qvector` est pleinement fonctionnel et identique.

---

## Phase 4: User Story 2 - Utiliser les deux outils sans collision (P1)

**Goal**: `vector` ne lance plus cet outil ; la collision avec l'autre
outil de l'utilisateur a disparu (FR-002)

**Independent Test**: dans une même session shell,
`vector --help` ne démarre plus cet outil (commande introuvable ou
résolue vers l'autre outil de l'utilisateur) tandis que
`qvector "Les voisins de la France disposent ils d'un dispositif
équivalent au crédit impôt recherche (CIR) ? Pour quel résultats dans
le monde ?"` fonctionne.

### Implementation for User Story 2

- [X] T008 [US-2] Vérifier la disparition de la collision après T006 :
  confirmer l'absence de tout script `vector` de cet outil dans le venv
  et dans le PATH utilisé, et documenter le résultat de la commande
  `vector --help` dans la session

**Checkpoint**: les deux outils de l'utilisateur cohabitent sans
invocation croisée.

---

## Phase 5: User Story 3 - Documentation cohérente et migration claire (P2)

**Goal**: toute la documentation courante désigne `qvector`, avec une
note de migration (FR-004, FR-005)

**Independent Test**: relecture des fichiers listés — chaque exemple
d'invocation utilise `qvector` ; l'ancien nom n'apparaît que dans la
note de migration du README.

### Implementation for User Story 3

- [X] T009 [P] [US-3] Mettre à jour README.md : tous les exemples
  d'usage (notamment `vector "Comment fonctionne le depot git ?"`,
  `.venv\Scripts\vector` ligne ~27) vers `qvector`, et ajouter une note
  de migration (ancien nom `vector`, remplacement complet sans alias,
  consigne de suppression du script résiduel du venv)
- [X] T010 [P] [US-3] Mettre à jour le nom de commande dans
  specs/001-text-vectorization/contracts/cli.md (titre, usage
  `vector [ENTRÉE...] [OPTIONS]`, références) et les exemples de
  specs/001-text-vectorization/quickstart.md — sans réécrire les
  scénarios Given/When/Then
- [X] T011 [P] [US-3] Mettre à jour le nom de commande dans
  specs/002-sortie-tableau-json/contracts/cli.md (ligne d'usage
  `vector [ENTREE...] [OPTIONS]`)

**Checkpoint**: documentation entièrement cohérente avec le contrat
`qvector` (specs/003-renommage-commande-qvector/contracts/cli.md).

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: vérifications transverses de fin de feature

- [X] T012 Scanner les occurrences résiduelles du nom de commande
  `vector` dans pyproject.toml, src/, README.md et specs/ (hors note de
  migration du README, documents d'archive Prompts/ et scénarios
  historiques) : attendu 0 résidu
- [X] T013 Exécuter la validation complète de
  specs/003-renommage-commande-qvector/quickstart.md (6 scénarios),
  en utilisant les 4 questions réelles sur le CIR fournies par
  l'utilisateur comme entrées
- [X] T014 Vérifier que la version du paquet reste 0.1.0 dans
  pyproject.toml (aucun bump, cf. clarification) et lancer une
  dernière fois `pytest`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: aucune dépendance — démarrage immédiat
- **Phase 2 (Foundational)**: après Phase 1 — bloque les stories
- **Phases 3-5 (US-1, US-2, US-3)**: après Phase 2
- **Phase 6 (Polish)**: après toutes les stories

### User Story Dependencies

- **US-1 (P1)**: après T003. T004 → T006 séquentiels (même interface),
  T005 parallélisable avec T004
- **US-2 (P1)**: dépend de T006 (réinstallation effective) — sinon
  indépendante
- **US-3 (P2)**: indépendante de US-1/US-2 (fichiers disjoints),
  parallélisable dès T003

### Within Each User Story

- Renommage du code avant réinstallation (T004/T005 avant T006)
- Validation (T007, T008) en dernier dans la story

### Parallel Opportunities

- T005 parallèle à T004 (fichiers différents : cli.py / config.py)
- T009, T010, T011 entièrement parallèles entre elles (README,
  specs/001, specs/002)
- US-3 parallélisable avec US-1 dès T003 terminé

---

## Parallel Example: User Story 1

```bash
# Après T003, en parallèle (fichiers différents) :
Task: "Mettre à jour prog= dans src/question2vector/cli.py"
Task: "Mettre à jour les docstrings de src/question2vector/config.py"

# Puis séquentiel :
Task: "Réinstaller le paquet dans le venv et vérifier les scripts"
Task: "Valider avec les questions CIR puis pytest"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 : état de référence
2. Phase 2 : entry point renommé
3. Phase 3 : US-1 complète
4. **STOP and VALIDATE** : `qvector` fonctionnel à l'identique
   (questions CIR + pytest)

### Incremental Delivery

1. US-1 → l'outil répond sous `qvector` (MVP)
2. US-2 → collision avec l'autre outil éliminée
3. US-3 → documentation cohérente et note de migration
4. Polish → scan des résidus + quickstart complet

### Notes

- Ne jamais créer d'alias `vector` (perpétuerait la collision)
- Ne pas modifier les tests existants ni le schéma `Vector-2.0`
- Les 4 questions CIR sont des entrées réelles fournies par
  l'utilisateur : les utiliser préférentiellement aux exemples
  Examples/*.txt pour les validations manuelles
