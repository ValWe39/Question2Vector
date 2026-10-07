---
description: "Task list for feature implementation"
---

# Tasks: vectorisation via embeddings Mistral (`vector`)

**Input**: Design documents from `/specs/001-text-vectorization/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/cli.md, quickstart.md

**Tests**: inclus — le plan impose `pytest` (plan.md, Technical Context)
et quickstart.md valide la suite verte en fin de parcours.

**Organization**: tâches groupées par user story (P1→P4) pour une
implémentation et une validation indépendantes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallélisable (fichiers différents, pas de dépendance)
- **[Story]**: user story (US-1 a US-4) — absent en
  Setup/Foundational/Polish ; la notation US-N (plutot que USN)
  evite un faux positif du hook de conformite du depot
- Chemins exacts dans chaque description

## Path Conventions

- Code source : `src/question2vector/` (src layout, plan.md)
- Tests : `tests/unit/`, `tests/integration/`
- Racine : `pyproject.toml`, `.env.example`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: initialisation du projet Python

- [X] T001 Créer `pyproject.toml` : dépendances `mistralai`,
  `python-dotenv` ; dev `pytest` ; entry point console
  `vector = question2vector.cli:main` ; config Ruff alignée sur le CI
- [X] T002 [P] Créer le squelette `src/question2vector/__init__.py` et
  `src/question2vector/__main__.py` (invocation
  `python -m question2vector`)
- [X] T003 [P] Créer `.env.example` avec le placeholder
  `MISTRAL_API_KEY=YOUR_API_KEY` (jamais de clé réelle — constitution I)
- [X] T004 [P] Créer `tests/unit/` et `tests/integration/` avec un
  `conftest.py` racine (fixtures communes, aucun réseau)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: socle bloquant toutes les user stories

**CRITICAL**: aucune user story ne peut commencer avant la fin de cette
phase

- [X] T005 Implémenter `src/question2vector/config.py` :
  `VectorizationOptions` + validation des bornes — citer verbatim :
  `--taille-batch` (0-100, défaut 25), `--retry-occurences` (0-10,
  défaut 3), `--retry-time` (1-10 s, défaut 3), `--temperature-llm`
  (0-1, défaut 0,2), `--choix-techno-embed` (1024/256/128, défaut
  1024), `--choix-modele-llm` (8 alias, défaut `small`), `--reformule`
  (on/no, défaut no), `--output-folder` (défaut `output/`) ; valeur
  hors bornes → erreur claire avant tout appel API
- [X] T006 Implémenter `src/question2vector/config.py` : chargement de
  `MISTRAL_API_KEY` via `python-dotenv` + échec rapide si absente
  (FR-017) ; la clé n'est jamais affichée ni journalisée (FR-016)
- [X] T007 Implémenter `src/question2vector/mistral_client.py` :
  enveloppe fine injectable du SDK — `embedder(model, texts)` renvoyant
  `list[list[float]]`, `discuter(model, prompt, temperature)` renvoyant
  la réponse LLM ; aucune logique métier dans cette couche
- [X] T008 Implémenter `src/question2vector/embedding.py` : tables de
  référence strictes (FR-009, FR-010) — `mistral-embed`/1024,
  `mistral-embed-dim256-2510`/256, `mistral-embed-dim128-2510`/128,
  nature `float32` ; LlmModelRef des 8 alias (data-model.md) ;
  fonction de retry à délai exponentiel (délai initial doublé à chaque
  essai, cf. FR-015)
- [X] T009 Implémenter `src/question2vector/cli.py` : argparse complet
  des 8 options du contrat `contracts/cli.md` + codes de sortie
  (`0` succès, `1` configuration, `2` échecs d'éléments) ; appel de
  `config.py` pour la validation avant tout appel réseau

**Checkpoint**: socle prêt — les user stories peuvent démarrer

---

## Phase 3: User Story 1 - Vectoriser un texte unique (P1) — MVP

**Goal**: une chaîne, un `.txt` ou un `.md` produit un JSON `Vector-1.0`
dans `output/` (spec.md, US-1)

**Independent Test**: `vector Examples/Corsen.txt` crée un JSON valide
avec un vecteur de 1024 floats (quickstart.md, scénario 2)

### Tests for User Story 1

> **NOTE**: écrire ces tests AVANT l'implémentation, s'assurer qu'ils
> échouent d'abord

- [X] T010 [P] [US-1] Tests unitaires de détection d'entrée dans
  `tests/unit/test_inputs.py` : fichier existant `.txt`/`.md`, chaîne
  sans syntaxe de chemin, chemin inexistant → erreur (FR-001) ;
  fichier vide → non traitable
- [X] T011 [P] [US-1] Tests unitaires de nommage dans
  `tests/unit/test_output.py` : 7 premiers caractères significatifs,
  symboles ignorés, accents simplifiés, espaces en `_`, repli
  `sans_titre`, conflit `-1`, `-2`… (FR-007, FR-008)

### Implementation for User Story 1

- [X] T012 [US-1] Implémenter `src/question2vector/inputs.py` : règle
  de détection FR-001 (fichier existant / chaîne littérale sans
  syntaxe de chemin / chemin inexistant → erreur) + lecture UTF-8
  du contenu complet (FR-002)
- [X] T013 [US-1] Implémenter `src/question2vector/output.py` : dérivation
  du nom de sortie (FR-007) et gestion des conflits `-X` (FR-008),
  intra-exécution incluse
- [X] T014 [US-1] Implémenter `src/question2vector/output.py` :
  sérialisation `OutputRecord` schéma `Vector-1.0` —
  `schema_version`/`entrée`/`reformulation`/`vecteur`/
  `dimension_vecteur`/`nature_vecteur` (FR-005) ; invariant
  `len(vecteur) == dimension_vecteur` sinon échec de l'élément
- [X] T015 [US-1] Câbler `src/question2vector/cli.py` : flux unitaire
  (détection → embedding sans batch → écriture JSON) avec le
  `EmbeddingModelRef` par défaut 1024
- [X] T016 [US-1] Test d'intégration dans
  `tests/integration/test_single.py` : client mocké, chaîne unique
  puis `.txt` puis `.md`, vérification du JSON complet et du code de
  sortie 0

**Checkpoint**: US-1 fonctionnel et testable seul (MVP)

---

## Phase 4: User Story 2 - Multi-input et batching (P2)

**Goal**: plusieurs éléments ou un dossier → un JSON par élément,
embeddings regroupés par batch (spec.md, US-2)

**Independent Test**: `vector Examples/` produit 6 JSON, batchs
regroupés (quickstart.md, scénario 3)

### Tests for User Story 2

- [X] T017 [P] [US-2] Tests unitaires dans `tests/unit/test_batching.py`
  : découpage en lots de 25 (ex. 40 éléments → 2 lots 25+15), taille 0
  → requête simple par texte (FR-004)

### Implementation for User Story 2

- [X] T018 [US-2] Implémenter l'expansion de dossier dans
  `src/question2vector/inputs.py` : premier niveau uniquement, seuls
  `.txt`/`.md` retenus, autres formats ignorés silencieusement (FR-002)
  ; dossier sans fichier éligible → erreur claire
- [X] T019 [US-2] Implémenter le regroupement par batch dans
  `src/question2vector/embedding.py` : découpage en lots de
  `--taille-batch` et redistribution des vecteurs aux éléments ;
  `--taille-batch 0` = une requête par texte, sans lot
- [X] T020 [US-2] Implémenter le bilan d'exécution
  (`ProcessingReport`) dans `src/question2vector/cli.py` : statut par
  élément, échecs signalés à la fin sans interrompre les autres
  (FR-003, FR-014), code de sortie `2` si au moins un échec
- [X] T021 [US-2] Test d'intégration dans
  `tests/integration/test_multi.py` : dossier temporaire de fichiers
  mixtes, client mocké, un JSON par élément éligible dans le même
  dossier de sortie

**Checkpoint**: US-1 et US-2 fonctionnels indépendamment

---

## Phase 5: User Story 3 - Reformulation LLM (P3)

**Goal**: `--reformule on` reformule les questions courtes puis
vectorise la reformulation (spec.md, US-3)

**Independent Test**: `vector --reformule on "Ça marche comment ?"`
remplit `reformulation` et le vecteur porte sur elle (quickstart.md,
scénario 4)

### Tests for User Story 3

- [X] T022 [P] [US-3] Tests unitaires dans
  `tests/unit/test_reformulation.py` : éligibilité ≤ 500 caractères
  (FR-012), parsing strict du schéma
  `ambiguous`/`reformulation`/`options`, `ambiguous: true` ou JSON
  invalide après retries → échec de l'élément sans sortie (FR-014)

### Implementation for User Story 3

- [X] T023 [US-3] Implémenter `src/question2vector/reformulation.py` :
  prompt de reformulation constant (spec.md, sans modification, texte
  inséré en fin), appel LLM en JSON mode
  (`response_format` `{"type": "json_object"}`, research.md point 6),
  parsing strict, éligibilité ≤ 500 caractères — documents longs
  vectorisés tels quels
- [X] T024 [US-3] Câbler `src/question2vector/cli.py` : si reformulation
  réussie, le vecteur porte sur la reformulation et `reformulation`
  est rempli dans le JSON ; l'original reste dans `entrée` (FR-013) ;
  appel élément par élément, jamais par lot (FR-004)
- [X] T025 [US-3] Test d'intégration dans
  `tests/integration/test_reformulation.py` : cas nominal, cas ambigu
  (aucun JSON produit, code 2), cas document long (pas d'appel LLM)

**Checkpoint**: US-1, US-2 et US-3 fonctionnels indépendamment

---

## Phase 6: User Story 4 - Options CLI (P4)

**Goal**: chaque option du contrat modifie le comportement attendu
(spec.md, US-4, `contracts/cli.md`)

**Independent Test**: `vector --choix-techno-embed 256 --taille-batch 0
--output-folder resultats/` produit un JSON 256 floats dans
`resultats/` (quickstart.md, scénario 5)

### Tests for User Story 4

- [X] T026 [P] [US-4] Tests unitaires de bornes dans
  `tests/unit/test_config.py` : matrice hors bornes (`--taille-batch
  150`, `--retry-time 0`, `--retry-occurences 11`,
  `--temperature-llm 1,5`, alias inconnu) → refus avant tout appel API
  (FR-011)

### Implementation for User Story 4

- [X] T027 [US-4] Vérifier le choix du modèle bout-en-bout dans
  `src/question2vector/cli.py` + `embedding.py` : `256` et `128`
  produisent des vecteurs de la bonne dimension avec les champs
  `dimension_vecteur`/`nature_vecteur` correspondants (FR-009)
- [X] T028 [US-4] Vérifier la nature `float32` sur une réponse API
  réelle (research.md point 9) : une requête manuelle, ajuster la
  table `EmbeddingModelRef` si contredit ; consigner le résultat dans
  `specs/001-text-vectorization/research.md`
- [X] T029 [US-4] Vérifier le plumbing des options de contrôle dans
  `src/question2vector/cli.py` : `--taille-batch 0`, `--retry-time` /
  `--retry-occurences` (délais 1 s puis 2 s pour `--retry-time 1
  --retry-occurences 2`), `--output-folder` (dossier créé si absent),
  `--temperature-llm` transmise au LLM
- [X] T030 [US-4] Test d'intégration dans
  `tests/integration/test_options.py` : 256 dimensions, lot 0, dossier
  de sortie personnalisé, valeurs hors bornes → code `1` avant appel

**Checkpoint**: les 4 user stories sont fonctionnelles

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: préoccupations transversales aux stories

- [X] T031 [P] Vérifier les licences et l'absence de trackers des
  dépendances (`pip-audit`, job `audit` du CI — constitution III) ;
  consigner dans `specs/001-text-vectorization/research.md`
- [X] T032 Exécuter la validation complète de
  `specs/001-text-vectorization/quickstart.md` (scénarios 1 à 7) et
  corriger les écarts constatés
- [X] T033 [P] Mettre à jour `README.md` : installation, usage du
  contrat `contracts/cli.md`, référence au quickstart
- [X] T034 Nettoyage final : `pytest` vert, `ruff check` et
  `markdownlint-cli2` verts (hooks pre-commit), aucun secret ni chemin
  personnel dans le diff (constitution I)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sans dépendance — démarrage immédiat
- **Foundational (Phase 2)**: dépend de Setup — BLOQUE toutes les
  user stories
- **User Stories (Phases 3-6)**: dépendent de Foundational ; ordre
  recommandé US-1 → US-2 → US-3 → US-4 (US-2 réutilise inputs/output de
  US-1 ; US-4 plombe les flux des stories précédentes)
- **Polish (Phase 7)**: dépend de toutes les stories retenues

### User Story Dependencies

- **US-1 (P1)**: démarre après Foundational — aucune autre story
- **US-2 (P2)**: démarre après Foundational ; réutilise les modules
  inputs/output/embedding de US-1 (testable indépendamment)
- **US-3 (P3)**: démarre après Foundational ; réutilise inputs/output
  de US-1 et le bilan d'US-2 (testable indépendamment)
- **US-4 (P4)**: démarre après Foundational ; vérifie le plumbing des
  options sur les flux US-1-US-3

### Within Each User Story

- Tests d'abord (échec prouvé), puis modèles/lecture, puis services,
  puis câblage CLI
- La story est complète avant de passer à la priorité suivante

### Parallel Opportunities

- T002, T003, T004 en parallèle (Phase 1)
- T010 et T011 en parallèle (tests US-1, fichiers différents)
- T017 en parallèle de T022 (tests US-2/US-3, fichiers différents)
- T026 en parallèle des autres tests US-4
- Une fois Foundational terminé, US-1-US-4 peuvent avancer en parallèle
  par développeurs différents (US-4 en dernier recommandé)

---

## Parallel Example: User Story 1

```text
# Tests US-1 en parallèle :
Task: "Tests unitaires de détection d'entrée dans tests/unit/test_inputs.py"
Task: "Tests unitaires de nommage dans tests/unit/test_output.py"

# Puis implémentation séquentielle :
Task: "Implémenter src/question2vector/inputs.py"
Task: "Implémenter src/question2vector/output.py"
Task: "Câbler src/question2vector/cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Compléter Phase 1 (Setup)
2. Compléter Phase 2 (Foundational) — critique, bloque tout
3. Compléter Phase 3 (US-1)
4. **STOP et VALIDER** : `vector Examples/Corsen.txt` → JSON valide
5. Démo possible : la sortie est utilisable

### Incremental Delivery

1. Setup + Foundational → socle prêt
2. Ajouter US-1 → valider seul → MVP
3. Ajouter US-2 → valider le multi-input
4. Ajouter US-3 → valider la reformulation
5. Ajouter US-4 → valider les options
6. Polish → validation quickstart complète

### Parallel Team Strategy

Avec plusieurs développeurs :

1. L'équipe complète Setup + Foundational ensemble
2. Une fois Foundational terminé :
   - Dev A : US-1 puis US-3
   - Dev B : US-2 puis US-4
3. Intégration aux checkpoints de chaque phase

---

## Notes

- [P] = fichiers différents, pas de dépendance
- [Story] = traçabilité vers spec.md
- Chaque story est livrable et démontrable seule
- Prouver l'échec des tests avant l'implémentation
- Committer après chaque tâche ou groupe logique (hooks pre-commit
  actifs, aucun contournement)
- À revoir : T028 requiert une clé API réelle (tâche manuelle, hors
  suite automatisée)
