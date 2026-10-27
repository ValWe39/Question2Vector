# Feature Specification: Renommage de la commande « vector » en « qvector »

**Feature Branch**: `005-changement-nom-commande`

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "Remplacer le nom actuel de la commande
principale (\"vector\") par \"qvector\" sans changer le reste de l'outil"
(assessment `renommer-vector-qvector`, decision GO, option A : remplacement
complet sans alias)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Invoquer l'outil sous son nouveau nom (Priority: P1)

L'utilisateur met à jour l'outil dans son environnement puis lance
`qvector` avec les mêmes entrées et options qu'avant. L'outil se comporte
exactement comme précédemment : mêmes arguments acceptés, mêmes sorties,
même format de fichier de résultat.

**Why this priority**: c'est la valeur cœur du renommage — un nom de
commande utilisable, sans rien perdre du comportement existant.

**Independent Test**: peut être validé seul en lançant `qvector` sur une
question et un fichier d'exemple, et en vérifiant que les options
habituelles produisent les résultats attendus.

**Acceptance Scenarios**:

1. **Given** l'outil mis à jour dans l'environnement, **When**
   l'utilisateur lance `qvector --help`, **Then** l'aide s'affiche
   correctement avec le nom `qvector` dans l'usage.
2. **Given** une question en argument, **When** l'utilisateur lance
   `qvector "Question ?"`, **Then** le résultat est identique à celui
   obtenu auparavant avec l'ancien nom (même fichier de sortie, même
   contenu).
3. **Given** un dossier d'exemples, **When** l'utilisateur lance
   `qvector Examples/`, **Then** toutes les entrées sont traitées comme
   avant, sans erreur.

---

### User Story 2 - Utiliser les deux outils sans collision (Priority: P1)

L'utilisateur, qui possède un autre outil exposant lui aussi une commande
`vector`, veut pouvoir utiliser cet outil et son autre outil dans le même
environnement sans qu'une invocation n'aboutisse par erreur au mauvais
programme. Après la mise à jour, `vector` ne lance plus cet outil.

**Why this priority**: c'est la motivation directe du renommage — éliminer
les erreurs déjà observées de résolution de commande.

**Independent Test**: peut être validé seul en invoquant `vector` et
`qvector` dans un même environnement et en vérifiant que seul `qvector`
lance cet outil.

**Acceptance Scenarios**:

1. **Given** l'outil mis à jour dans l'environnement, **When**
   l'utilisateur lance `vector`, **Then** cet outil ne démarre pas (la
   commande est soit introuvable, soit résolue vers l'autre outil de
   l'utilisateur).
2. **Given** l'autre outil de l'utilisateur installé, **When**
   l'utilisateur lance `vector` puis `qvector` dans la même session,
   **Then** chaque commande lance l'outil attendu, sans invocation croisée.

---

### User Story 3 - Documentation cohérente et migration claire (Priority: P2)

L'utilisateur consulte la documentation : tous les exemples et
instructions d'usage emploient `qvector`, et une note de migration indique
que la commande était anciennement nommée `vector`.

**Why this priority**: sans documentation à jour, l'utilisateur reproduirait
des exemples obsolètes ; la note de migration prévient la confusion lors du
changement d'habitude.

**Independent Test**: peut être validé seul en relisant la documentation
courante et en vérifiant que chaque exemple est directement exécutable
avec `qvector`.

**Acceptance Scenarios**:

1. **Given** la documentation courante (README), **When** l'utilisateur
   la lit, **Then** tous les exemples d'invocation utilisent `qvector`.
2. **Given** la documentation, **When** l'utilisateur cherche ce qu'est
   devenu `vector`, **Then** une note de migration indique l'ancien nom
   et le remplacement complet (sans alias).
3. **Given** les contrats d'interface CLI des spécifications
   existantes, **When** ils sont consultés, **Then** ils désignent la
   commande sous le nom `qvector`.

---

### Edge Cases

- Que se passe-t-il quand l'ancien script `vector` subsiste encore dans
  l'environnement après la mise à jour (environnement non recréé) ? La
  documentation de migration doit indiquer comment l'éliminer pour éviter
  une collision résiduelle.
- Que se passe-t-il quand l'utilisateur tape `vector` par habitude ? Il
  obtient son autre outil ou une commande introuvable — le comportement
  est attendu (aucun alias ne doit être créé), la note de migration
  l'explique.
- Que se passe-t-il avec l'invocation secondaire par module Python
  (`python -m question2vector`) ? Elle reste inchangée et fonctionnelle.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: L'outil DOIT être invocable sous le nom de commande
  `qvector`, avec un comportement identique à l'existant (mêmes entrées,
  mêmes options, mêmes sorties).
- **FR-002**: L'outil NE DOIT PLUS être exposé sous le nom de commande
  `vector` après mise à jour de l'environnement.
- **FR-003**: L'aide en ligne et les messages d'usage DOIVENT afficher
  `qvector` comme nom de commande.
- **FR-004**: La documentation courante (README, quickstart) DOIT
  employer `qvector` dans tous les exemples et instructions, et DOIT
  contenir une note de migration mentionnant l'ancien nom et l'absence
  d'alias.
- **FR-005**: Les contrats d'interface CLI des spécifications existantes
  DOIVENT désigner la commande sous le nom `qvector` (mise à jour des
  contrats et exemples d'usage, sans réécriture des scénarios).
- **FR-006**: Le renommage NE DOIT PAS modifier le comportement
  fonctionnel : format de sortie et schéma `Vector-2.0` inchangés,
  options inchangées, résultat inchangé pour une même entrée.
- **FR-007**: L'invocation secondaire `python -m question2vector` DOIT
  rester fonctionnelle et inchangée.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 % des usages testés de `qvector` produisent les mêmes
  résultats qu'avant le renommage (suite de tests existante verte sans
  modification comportementale).
- **SC-002**: Après mise à jour de l'environnement, 0 invocation de
  `vector` ne lance cet outil (0 occurrence de l'ancien script résiduel
  après nettoyage).
- **SC-003**: La documentation courante ne contient aucune occurrence
  d'usage de `vector` hors de la note de migration (100 % des exemples
  utilisent `qvector`).
- **SC-004**: Les erreurs de résolution de commande entre les deux
  outils de l'utilisateur disparaissent : chaque appel `vector` et
  `qvector` dans un même environnement lance l'outil attendu.

## Assumptions

- Aucun script ni raccourci externe critique n'invoque `vector` ; si
  certains existent, l'utilisateur les adaptera (couvert par la note de
  migration).
- La mise à jour de l'environnement remplace l'ancien script ; l'éventuel
  script résiduel `vector` est éliminé lors du nettoyage documenté.
- Les spécifications historiques (001, 002) sont mises à jour
  uniquement dans les contrats d'interface et exemples d'usage, pas
  réécrites.
- Le schéma de sortie `Vector-2.0` et le paquet `question2vector`
  conservent leur nom (hors périmètre, cf. decision de l'assessment).
- L'outil reste mono-utilisateur et non publié : aucune note de
  migration externe n'est requise au-delà du README.
