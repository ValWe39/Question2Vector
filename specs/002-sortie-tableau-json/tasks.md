---
description: "Task list template for feature implementation"
---

# Taches: Sortie tableau JSON regroupee

**Input**: Design documents from `/specs/002-sortie-tableau-json/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/cli.md, quickstart.md

**Tests**: la reecriture des tests existants est incluse — le format
`Vector-1.0` objet est asserté par la suite actuelle, toute
implementation le casse (SC-004).

**Organization**: taches groupees par user story, chaque story est
implementable et testable independamment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: executable en parallele (fichiers differents, pas de
  dependance)
- **[US-1]/[US-2]/[US-3]**: story de rattachement (cf. spec.md)
- Chemins de fichiers exacts dans chaque description

## Path Conventions

Projet unique : `src/` et `tests/` a la racine (cf. plan.md,
structure reutilisee telle quelle).

## Phase 1: Verification initiale

**Purpose**: partir d'une base saine avant toute modification

- [x] T001 Verifier que la suite actuelle passe :
  `.venv/Scripts/python -m pytest` vert sur l'etat de la branche

---

## Phase 2: Fondations (prerequis bloquants)

**Purpose**: structures que toutes les stories partagent

- [x] T002 [P] Ajouter l'option `--ungroup` (`on` | `no`, defaut
  `no`) au parseur de src/question2vector/cli.py et le champ
  `ungroup` a `VectorizationOptions` dans
  src/question2vector/config.py ; toute autre valeur refusee avec
  `ErreurConfiguration` (data-model.md, ModeLivraison)
- [x] T003 [P] Dans src/question2vector/output.py : faire passer
  `SCHEMA_VERSION` a `"Vector-2.0"` et ajouter
  `EnregistrementEchec` — champs exacts `schema_version`,
  `entree`, `motif_echec` non vide, jamais de champ `vecteur`
  (data-model.md, EnregistrementEchec)

**Checkpoint**: fondations pretes — les stories peuvent commencer

---

## Phase 3: User Story 1 - Livrable unique (P1) — MVP

**Goal**: par defaut, toutes les entrees d'un run aboutissent dans
un seul fichier tableau `sortie.json`, un enregistrement par entree,
dans l'ordre des arguments (FR-001, FR-002, FR-003, FR-005,
FR-006).

**Independent Test**: lancer la commande sur 3 entrees et verifier
qu'un unique `sortie.json` chargeable en une lecture contient 3
enregistrements dans l'ordre des arguments (quickstart scenarios 1
et 2).

### Tests for User Story 1 (a reorienter en premier)

- [x] T004 [P] [US-1] Reorienter tests/unit/test_output.py :
  format tableau (liste, jamais un objet isole), ordre des
  enregistrements, nommage `sortie.json` et suffixe `-X`
- [x] T005 [P] [US-1] Reorienter tests/integration/test_single.py :
  entree unique → tableau a exactement un enregistrement a 6
  champs dans `sortie.json`

### Implementation for User Story 1

- [x] T006 [US-1] Implementer l'ecriture du livrable dans
  src/question2vector/output.py : liste ordonnee d'enregistrements
  serialisee en tableau JSON, nommage `sortie.json` avec suffixe
  d'unicite via `resoudre_nom` (FR-006, FR-010)
- [x] T007 [US-1] Restructurer `executer` dans
  src/question2vector/cli.py : collecter les enregistrements
  reussis dans l'ordre des entrees, ecrire le livrable unique en fin
  de run, adapter `RapportElement` et `_afficher_bilan` au fichier
  unique (FR-009)

**Checkpoint**: US-1 fonctionnelle et testable seule

---

## Phase 4: User Story 2 - Choix du mode de livraison (P2)

**Goal**: `--ungroup on` produit une sortie par entree, chaque
fichier etant un tableau a un enregistrement (FR-004, FR-007).

**Independent Test**: lancer la meme commande multi-entrees avec
`--ungroup on` et verifier un fichier tableau par entree, nomme
selon le contrat 001 (quickstart scenario 3).

### Tests for User Story 2

- [x] T008 [P] [US-2] Ajouter le scenario degroupe dans
  tests/integration/test_multi.py : N entrees → N fichiers, chacun
  un tableau a un enregistrement, nommage `deriver_titre` + suffixe
- [x] T009 [P] [US-2] Ajouter la validation de `--ungroup` dans
  tests/unit/test_config.py : `on`/`no` acceptes, valeur invalide
  refusee avant tout appel API

### Implementation for User Story 2

- [x] T010 [US-2] Brancher le mode degroupe dans
  src/question2vector/cli.py : un fichier par entree (tableau a un
  enregistrement), nommage selon le contrat 001 ; le comportement
  regroupe reste le defaut

**Checkpoint**: US-1 et US-2 fonctionnelles et testables
independamment

---

## Phase 5: User Story 3 - Robustesse du livrable (P3)

**Goal**: chaque entree du run figure dans le livrable — vecteur si
reussie, `motif_echec` sinon — et aucun fichier existant n'est
jamais ecrase (FR-007, FR-010).

**Independent Test**: lancer la commande avec deux entrees valides
et un chemin inexistant, verifier les trois enregistrements et le
code 2, puis relancer et verifier le suffixe sans ecrasement
(quickstart scenarios 4 et 6).

### Tests for User Story 3

- [x] T011 [P] [US-3] Scenario echec partiel dans
  tests/integration/test_multi.py : 2 reussites a vecteur + 1
  enregistrement d'echec (`entree` = argument brut,
  `motif_echec` = « chemin introuvable »), code de sortie 2
- [x] T012 [P] [US-3] Scenario reexecution dans
  tests/integration/test_multi.py : nouveau run dans le meme
  dossier → `sortie-1.json`, `sortie.json` inchange

### Implementation for User Story 3

- [x] T013 [US-3] Injecter les enregistrements d'echec dans
  src/question2vector/cli.py : echecs de detection de
  `resoudre_arguments` (motif standardise « chemin introuvable »),
  echecs de reformulation et d'embedding, en preservant l'ordre des
  arguments d'appel (FR-005, FR-007)
- [x] T014 [US-3] Verifier l'absence d'ecrasement pour le livrable
  unique dans src/question2vector/output.py : suffixe d'unicite
  systematique via `resoudre_nom`, y compris toutes entrees en echec
  (cas limite data-model.md)

**Checkpoint**: les trois stories sont independamment fonctionnelles

---

## Phase 6: Finitions et transversal

**Purpose**: coherence des documents de reference et validation
finale

- [x] T015 [P] Mettre a jour README.md : format de sortie tableau
  `Vector-2.0`, option `--ungroup` dans le tableau des options,
  lien vers specs/002-sortie-tableau-json/contracts/cli.md
- [ ] T016 Executer le guide
  specs/002-sortie-tableau-json/quickstart.md en entier et verifier
  chaque attendu (scenarios 1 a 6)
- [x] T017 Lancer `.venv/Scripts/python -m pytest` complet et
  `pre-commit run --all-files` avant cloture

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: aucune dependance, point d'entree
- **Phase 2**: apres la Phase 1 — BLOQUE toutes les stories
- **Phases 3 a 5**: apres la Phase 2 ; en sequentiel par priorite
  (P1 → P2 → P3), ou en parallele si plusieurs developpeurs
- **Phase 6**: apres toutes les stories retenues

### User Story Dependencies

- **US-1 (P1)**: demarre apres la Phase 2, aucune dependance entre
  stories
- **US-2 (P2)**: demarre apres la Phase 2 ; integre le mode degroupe
  au livrable deja produit par US-1
- **US-3 (P3)**: demarre apres la Phase 2 ; complete US-1 et US-2
  avec les enregistrements d'echec et la garantie d'unicite

### Within Each User Story

- Reorienter les tests en premier, les faire echouer, puis
  implementer
- Entites avant orchestration (T003 avant T006/T007)
- Une story complete avant de passer a la priorite suivante

### Parallel Opportunities

- T002 et T003 (Phase 2) : fichiers differents
- T004/T005 (US-1), T008/T009 (US-2), T011/T012 (US-3) : tests de
  fichiers differents, executables en parallele au sein de chaque
  story
- T015 (Phase 6) parallele aux validations manuelles T016

---

## Parallel Example: User Story 1

```text
# Lancer ensemble les reorientations de tests US-1 :
Task: "T004 Reorienter tests/unit/test_output.py"
Task: "T005 Reorienter tests/integration/test_single.py"

# Puis en sequence :
Task: "T006 Implementer l'ecriture du livrable dans output.py"
Task: "T007 Restructurer executer dans cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 : base verifiee
2. Phase 2 : option `--ungroup` + entites `Vector-2.0`
3. Phase 3 : US-1 (livrable unique)
4. STOP et VALIDER : quickstart scenarios 1 et 2

### Incremental Delivery

1. Phases 1-2 → fondations pretes
2. US-1 → test seul (MVP)
3. US-2 → test seul (mode degroupe)
4. US-3 → test seul (echecs et unicite)
5. Phase 6 → documents coherents et validation finale

---

## Notes

- [P] = fichiers differents, pas de dependance
- Le label [US-x] rattache chaque tache a sa story pour la
  tracabilite
- Les tests reorients doivent echouer avant implementation
- Commit apres chaque tache ou groupe logique
- S'arreter a chaque checkpoint pour valider la story seule
