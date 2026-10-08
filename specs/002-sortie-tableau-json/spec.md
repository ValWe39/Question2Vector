# Feature Specification: Sortie tableau JSON regroupee

**Feature Branch**: `004-upgrade-sortie`

**Created**: 2026-10-08

**Status**: Draft

**Input**: User description: "Handoff de l'assessment regroupement-sorties
(decision GO, option B) : sortie toujours au format tableau JSON,
regroupement de toutes les question-vecteurs du run dans un seul
fichier par defaut, option CLI pour restaurer une sortie par entree
(chacune au format tableau)."

## Clarifications

### Session 2026-10-08

- Q: L'enregistrement d'echec doit-il contenir exactement trois
  champs, sans reformulation ni dimension_vecteur ? → A: Oui —
  `schema_version`, `entree`, `motif_echec` uniquement.
- Q: Pour une entree introuvable, quelle valeur porte le champ
  `entree` ? → A: l'argument brut fourni ; `motif_echec` porte la
  mention « chemin introuvable ».

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Livrable unique pour un run multi-entrees (Priority: P1)

En tant qu'utilisateur, je lance `vector` sur plusieurs entrees et je
recupere un seul fichier JSON contenant toutes mes question-vecteurs,
directement chargeable par mon consommateur aval sans fusion
manuelle.

**Why this priority**: tient le but premier du probleme (consommer les
resultats en bloc) et livre de la valeur meme sans les autres
stories.

**Independent Test**: lancer la commande sur 3 entrees et verifier
qu'un unique fichier contenant 3 enregistrements est produit et
chargeable en une seule lecture.

**Acceptance Scenarios**:

1. **Given** plusieurs entrees valides, **When** la commande se
   termine avec succes, **Then** un seul fichier JSON existe dans le
   dossier de sortie et contient un enregistrement par entree.
2. **Given** une seule entree valide, **When** la commande se termine
   avec succes, **Then** le fichier produit est un tableau contenant
   exactement un enregistrement.
3. **Given** des entrees de natures melangees (chaines, fichiers,
   dossier), **When** la commande se termine avec succes, **Then**
   chaque entree figure dans le livrable, dans l'ordre des
   arguments d'appel.

---

### User Story 2 - Choix du mode de livraison (Priority: P2)

En tant qu'utilisateur habitue a une sortie par entree, je peux
demander via une option que chaque entree produise son propre fichier,
chaque fichier restant au format tableau.

**Why this priority**: preserve l'usage existant fichier-par-entree
sans retirer la valeur du regroupement par defaut.

**Independent Test**: lancer la meme commande multi-entrees avec
l'option de degroupement activee et verifier qu'un fichier tableau
est produit par entree.

**Acceptance Scenarios**:

1. **Given** N entrees valides et l'option de degroupement activee,
   **When** la commande se termine avec succes, **Then** N fichiers
   sont ecrits, chacun etant un tableau a un enregistrement.
2. **Given** des entrees valides sans option de degroupement (ou
   option explicitement desactivee), **When** la commande se termine
   avec succes, **Then** le comportement regroupe par defaut
   s'applique.

---

### User Story 3 - Robustesse du livrable (Priority: P3)

En tant qu'utilisateur, chaque entree de mon run figure dans le
livrable — avec son vecteur si elle a reussi, avec son motif d'echec
sinon — et les fichiers existants du dossier de sortie ne sont
jamais ecrases.

**Why this priority**: l'exhaustivite du livrable (une ligne par
entree, reussie ou en echec) et la preservation des fichiers
existants sont des engagements de confiance, sans lesquels le
fichier unique n'est pas exploitable sereinement.

**Independent Test**: lancer la commande avec deux entrees valides
et un chemin inexistant, verifier que le livrable contient deux
enregistrements a vecteur et un enregistrement d'echec, et que le
code de sortie signale l'echec partiel ; relancer deux fois et
verifier qu'aucun fichier existant n'est ecrase.

**Acceptance Scenarios**:

1. **Given** des entrees valides et au moins un chemin inexistant,
   **When** la commande se termine, **Then** le livrable contient
   un enregistrement par entree — vecteur pour les reussies, motif
   d'echec pour les autres — et le code de sortie signale l'echec
   partiel.
2. **Given** un fichier du meme nom deja present dans le dossier de
   sortie, **When** la commande ecrit son livrable, **Then** aucun
   fichier existant n'est ecrase.

---

### Edge Cases

- Entree unique : tableau a un element (transparence du format).
- Toutes les entrees traitees en echec : livrable ecrit compose
  uniquement d'enregistrements d'echec, code de sortie d'echec.
- Aucune entree exploitable (chemins inexistants uniquement) :
  erreur de configuration, aucun livrable, comme aujourd'hui.
- Dossier en entree sans fichier eligible : erreur claire, aucun
  livrable.
- Vecteur de dimension differente du referrentiel du modele :
  enregistrement d'echec pour l'element concerne.
- Reexecution successive dans le meme dossier de sortie : suffixe
  d'unicite sur le fichier groupe, aucun ecrasement.
- Dossier de sortie inexistant : cree comme aujourd'hui.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La sortie MUST etre un tableau JSON d'enregistrements,
  quel que soit le nombre d'entrees (tableau a un element pour une
  entree unique).
- **FR-002**: Chaque enregistrement MUST conserver les champs
  actuels : `schema_version`, `entree`, `reformulation`, `vecteur`,
  `dimension_vecteur`, `nature_vecteur`.
- **FR-003**: Par defaut, tous les enregistrements du run
  (reussites et echecs) MUST etre regroupes dans un seul fichier
  JSON ecrit dans le dossier de sortie.
- **FR-004**: L'utilisateur MUST pouvoir demander une sortie par
  entree via l'option `--ungroup` (desactivee par defaut, donc
  regroupement actif), chaque fichier etant un tableau a un
  enregistrement.
- **FR-005**: L'ordre des enregistrements du livrable MUST suivre
  l'ordre des entrees fournies (la tracabilite repose sur l'ordre et
  le champ `entree`, sans champ supplementaire).
- **FR-006**: Le fichier groupe MUST etre nomme `sortie.json` ; si
  ce nom est deja pris sur le disque ou attribue dans la meme
  execution, un suffixe d'unicite `-X` (X demarrant a 1) MUST etre
  applique, par coherence avec la regle de conflit existante.
- **FR-007**: Chaque entree du run MUST figurer dans le livrable.
  Une entree en echec produit un enregistrement d'echec compose
  exactement de trois champs : `schema_version`, `entree` et
  `motif_echec` (non vide) — sans `reformulation`, `vecteur`,
  `dimension_vecteur` ni `nature_vecteur`. Une entree reussie
  produit un enregistrement complet avec vecteur. Le comportement
  s'applique aux deux modes de livraison (groupe et par entree).
  Pour une entree jamais lue (ex. chemin inexistant), `entree`
  MUST porter l'argument brut fourni par l'utilisateur et
  `motif_echec` la mention « chemin introuvable ».
- **FR-008**: La valeur de `schema_version` MUST etre `Vector-2.0`
  dans chaque enregistrement (succes et echec), marquant la rupture
  avec le format objet `Vector-1.0`.
- **FR-009**: Le resume de fin d'execution MUST lister les fichiers
  ecrits (unique ou par entree) et les elements en echec, sans jamais
  afficher de vecteur ni de cle d'API.
- **FR-010**: Les fichiers existants du dossier de sortie MUST
  ne jamais etre ecrases ; un nom deja pris entraine un suffixe
  d'unicite.

### Key Entities

- **EnregistrementVecteur** : une ligne du livrable, en deux
  formes — succes (entree + reformulation + vecteur, dimension,
  nature) ou echec (entree + motif) — chacune portant la version
  de schema.
- **LivrableUnique** : le fichier JSON tableau regroupant tous les
  EnregistrementVecteur du run (reussites et echecs), avec sa
  propre regle de nommage.
- **ModeLivraison** : le choix utilisateur — regroupe (defaut) ou
  un fichier par entree.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un run de N entrees reussies produit exactement 1
  fichier en mode regroupe, chargeable en une seule lecture par un
  consommateur, sans aucune etape manuelle de fusion (baseline
  actuelle : N fichiers a ouvrir et a concatener).
- **SC-002**: Le format du document est identique pour 1 et pour N
  entrees : meme structure de tableau, memes champs par
  enregistrement.
- **SC-003**: En mode sortie par entree, N entrees reussies
  produisent exactement N fichiers, chacun un tableau a un
  enregistrement.
- **SC-004**: Les documents de reference du projet (contrat CLI,
  README, tests) restent coherents avec le format reellement
  produit.
- **SC-005**: Quel que soit le mode de livraison, le livrable
  contient exactement un enregistrement par entree fournie
  (reussite ou echec) : taux d'exhaustivite de 100 % par rapport
  aux entrees du run.

## Assumptions

- Les volumes par run restent modestes (dizaines d'entrees) ; aucun
  traitement en flux n'est requis.
- La tracabilite repose sur l'ordre des enregistrements et le champ
  `entree` (texte complet), sans identifiant supplementaire.
- Le consommateur aval sait charger un tableau JSON d'objets.
- Aucune migration des sorties `Vector-1.0` existantes n'est
  fournie ; les anciens fichiers restent exploitables tels quels.
- Le pipeline de vectorisation (detection des entrees, reformulation,
  embeddings, batches, retries) reste inchange.
- L'option de degroupement suit le pattern de valeur existant du
  contrat CLI (valeurs activee/desactivee, desactivee par defaut).
