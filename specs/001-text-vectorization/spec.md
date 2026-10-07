# Feature Specification: vectorisation via embeddings Mistral (`vector`)

**Feature Branch**: `001-text-vectorization`

**Created**: 2026-10-07

**Status**: Draft

**Input**: User description: outil CLI `vector` qui vectorise une chaîne de
caractères, un fichier .txt/.md ou un ensemble d'éléments via l'API d'embedding
Mistral, avec reformulation LLM optionnelle, sortie JSON normalisée, batching et
retry exponentiel.

## Clarifications

### Session 2026-10-07

- Q: Comment l'outil doit-il réagir quand le LLM de reformulation répond
  `{"ambiguous": true}` (ambiguïté bloquante) ? → A: L'élément est marqué en
  échec et aucun JSON n'est produit pour lui ; les autres éléments d'un
  multi-input continuent d'être traités.
- Q: Quand l'argument fourni ne correspond à aucun fichier ou dossier existant,
  doit-il être traité comme une chaîne de caractères à vectoriser ? → A:
  Inversement : si l'argument n'a pas une syntaxe de chemin (pas de séparateur
  ni extension), il est vectorisé comme chaîne littérale ; s'il a une syntaxe de
  chemin mais n'existe pas, l'outil échoue avec un message clair.
- Q: Quand `--reformule on` est activé sur un document long, que doit vectoriser
  l'outil ? → A: Seules les entrées courtes de type question sont reformulées
  (par défaut ≤ 500 caractères) ; les documents longs sont vectorisés tels quels
  avec `reformulation` vide.
- Q: Quelle valeur exacte le champ `schema_version` doit-il contenir par défaut
  ? → A: `"Vector-1.0"` (versionnage sémantique explicite du schéma).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Vectoriser un texte unique (Priority: P1)

Un utilisateur fournit en entrée une chaîne de caractères, un fichier `.txt` ou
un fichier `.md`. L'outil détecte automatiquement la nature de l'entrée, appelle
le modèle d'embedding Mistral (par défaut `mistral-embed`, 1024 dimensions) et
produit un fichier JSON unique dans le dossier de sortie (par défaut `output/`).
Le JSON contient : la version du schéma, le texte original complet, la
reformulation (vide car option désactivée), le vecteur (liste de floats), la
dimension du vecteur et la nature des floats. Le nom du fichier de sortie
reprend les 7 premiers caractères significatifs de l'entrée (symboles ignorés,
accents simplifiés, espaces remplacées par `_`).

**Why this priority**: C'est la fonctionnalité cœur de l'outil ; sans elle,
aucun des autres scénarios n'a de sens. C'est le MVP.

**Independent Test**: Testable avec un seul appel `vector` sur n'importe lequel
des 6 exemples du dossier `Examples/` (ex. `Corsen.txt`) : un JSON valide avec
un vecteur de 1024 floats apparaît dans `output/`.

**Acceptance Scenarios**:

1. **Given** une chaîne de caractères en argument, **When** l'utilisateur lance
   la commande `vector` avec cette chaîne, **Then** un fichier JSON est créé
   dans `output/` contenant le texte original, un vecteur de 1024 floats,
   `dimension_vecteur: 1024` et la nature des floats du modèle.
2. **Given** un fichier `CourCptes1.txt`, **When** l'utilisateur lance `vector`
   avec ce chemin, **Then** le JSON de sortie contient l'intégralité du contenu
   du fichier dans `entrée` et le fichier de sortie est nommé d'après les 7
   premiers caractères significatifs du titre du fichier.
3. **Given** un fichier `Tocqueville2.md` (Markdown), **When** l'utilisateur
   lance `vector` avec ce chemin, **Then** le texte Markdown complet est traité
   et vectorisé comme n'importe quel texte.
4. **Given** un titre d'entrée `Corsen2.md` alors qu'un fichier `Corsen2.json`
   existe déjà dans le dossier de sortie, **When** l'outil écrit le résultat,
   **Then** le fichier est nommé `Corsen2-1.json` (suffixe numérique commençant
   à 1 en cas de conflit).

---

### User Story 2 - Vectoriser plusieurs éléments en entrée (Priority: P2)

Un utilisateur fournit plusieurs éléments textuels (chaînes, `.txt`, `.md`) ou
un dossier contenant des fichiers. L'outil détecte automatiquement qu'il s'agit
d'un multi-input, de façon transparente pour l'utilisateur. Chaque élément est
traité indépendamment et produit sa propre sortie JSON (N entrées = N sorties),
tous enregistrés dans le même dossier de sortie. Seule l'étape d'embedding est
mutualisée : les requêtes sont regroupées par batch (25 par défaut,
configurable).

**Why this priority**: Le traitement en masse est la principale valeur ajoutée
au-delà du cas unitaire ; le batching rend l'outil viable sur de gros volumes.

**Independent Test**: Testable en passant le dossier `Examples/` entier : 6 JSON
de sortie apparaissent dans `output/`, un par fichier (3 `.txt`, 3 `.md`), avec
les batchs d'embedding regroupés.

**Acceptance Scenarios**:

1. **Given** plusieurs chemins de fichiers en argument, **When** l'utilisateur
   lance `vector`, **Then** un fichier JSON par élément est produit dans le même
   dossier de sortie.
2. **Given** un dossier contenant des fichiers `.txt`, `.md` et d'autres formats
   (ex. images, PDF), **When** l'utilisateur lance `vector` sur ce dossier,
   **Then** seuls les fichiers `.txt` et `.md` sont traités ; les autres formats
   sont ignorés silencieusement.
3. **Given** 40 fichiers à traiter avec une taille de batch de 25, **When**
   l'embedding est exécuté, **Then** les requêtes sont regroupées en batchs (2
   batchs : 25 + 15) et chaque fichier obtient son propre vecteur dans son
   propre JSON.
4. **Given** un dossier ne contenant aucun fichier `.txt`/`.md`, **When**
   l'utilisateur lance `vector`, **Then** l'outil le signale clairement avec un
   message d'erreur explicite et ne crée pas de sortie vide.

---

### User Story 3 - Reformuler avant de vectoriser (Priority: P3)

Un utilisateur active l'option `--reformule on`. Avant l'embedding, chaque
entrée courte de type question (par défaut ≤ 500 caractères, voir Assumptions)
est envoyée à un LLM Mistral (par défaut `mistral-small-latest`, température
0,2) avec le prompt de reformulation fourni. Les documents longs ne sont pas
reformulés : ils sont vectorisés tels quels et `reformulation` reste vide. Le
LLM répond strictement en JSON (`{"ambiguous": false, "reformulation": "..."}`
ou `{"ambiguous": true, "reformulation": null, "options": [...]}`). Si la
reformulation est disponible, c'est elle qui est vectorisée (le texte original
reste dans `entrée`, la reformulation dans `reformulation`). Si l'entrée est
jugée ambiguë bloquante, l'élément est marqué en échec et aucun JSON n'est
produit pour lui (les autres éléments d'un multi-input continuent d'être
traités). Si l'option est désactivée (défaut), `reformulation` reste vide.

**Why this priority**: La reformulation améliore la qualité de vectorisation des
questions mal formulées, mais l'outil est pleinement fonctionnel sans elle.

**Independent Test**: Testable en lançant `vector --reformule on` sur la
question exemple « Ça marche comment ? » : le JSON contient la reformulation
renvoyée par le LLM et le vecteur correspond à la reformulation (dimension
identique à celle du modèle choisi).

**Acceptance Scenarios**:

1. **Given** une question reformulable et `--reformule on`, **When** le LLM
   renvoie `{"ambiguous": false, "reformulation": "..."}`, **Then** le JSON de
   sortie contient la reformulation et le vecteur est celui de la reformulation.
2. **Given** une question ambiguë et `--reformule on`, **When** le LLM renvoie
   `{"ambiguous": true, ...}`, **Then** l'élément est marqué en échec, aucun
   JSON n'est produit pour lui et les autres éléments continuent d'être traités.
3. **Given** `--reformule no` (ou absence de l'option), **When** un texte est
   traité, **Then** `reformulation` est vide dans le JSON et le vecteur est
   celui du texte original.
4. **Given** un document long (ex. `CourCptes1.txt`) et `--reformule on`,
   **When** l'élément est traité, **Then** aucune requête de reformulation n'est
   envoyée : le document est vectorisé tel quel et `reformulation` reste vide.
5. **Given** `--reformule on` avec `--choix-modele-llm large4`, **When** la
   reformulation est appelée, **Then** le modèle `mistral-large-4` est utilisé
   pour la reformulation, sans changement du modèle d'embedding.

---

### User Story 4 - Configurer l'outil via les options CLI (Priority: P4)

Un utilisateur ajuste le comportement via les options : choix du modèle
d'embedding (`--choix-techno-embed` : 1024/256/128 dimensions), taille des
batchs (`--taille-batch`, 0-100, 0 = pas de batch), modèle LLM
(`--choix-modele-llm`), retry (`--retry-occurences`, `--retry-time`), dossier de
sortie (`--output-folder`), température LLM (`--temperature-llm`). Les valeurs
hors bornes sont rejetées avec un message clair.

**Why this priority**: Les options offrent le contrôle fin (coût, latence,
volume) mais l'outil fonctionne avec les défauts.

**Independent Test**: Testable en lançant `vector --choix-techno-embed 256
--taille-batch 0 --output-folder resultats/` sur un exemple : le JSON contient
un vecteur de 256 floats dans le dossier `resultats/`, avec un appel d'embedding
simple sans batch.

**Acceptance Scenarios**:

1. **Given** `--choix-techno-embed` réglé sur le modèle 256 dimensions, **When**
   un texte est vectorisé, **Then** `dimension_vecteur` vaut 256 et le vecteur
   contient 256 floats.
2. **Given** `--taille-batch 0`, **When** plusieurs textes sont traités,
   **Then** chaque embedding est envoyé en requête simple, sans regroupement.
3. **Given** `--retry-time 1` et `--retry-occurences 2`, **When** une requête
   API échoue, **Then** l'outil réessaie jusqu'à 2 fois, à 1 s puis 2 s (délai
   doublé à chaque essai).
4. **Given** `--taille-batch 150` (hors bornes 0-100), **When** l'utilisateur
   lance la commande, **Then** la commande est refusée avec un message d'erreur
   explicite avant tout appel API.
5. **Given** `--output-folder mon_dossier/`, **When** l'utilisateur lance la
   commande, **Then** les sorties sont écrites dans `mon_dossier/` (créé si
   absent) au lieu de `output/`.

---

### Edge Cases

- Que se passe-t-il quand la clé API est absente ou invalide (`MISTRAL_API_KEY`)
  ? → L'outil doit échouer rapidement avec un message clair avant tout appel,
  sans jamais afficher ni journaliser la clé.
- Comment le système gère-t-il un échec de requête API après épuisement des
  retries ? → Message d'erreur explicite identifiant l'élément concerné ; en
  multi-input, les autres éléments continuent d'être traités et l'échec est
  signalé à la fin.
- Comment gérer une entrée vide (fichier vide ou chaîne vide) ? → L'élément est
  signalé comme non traitable avec un message clair, sans crash global.
- Comment gérer un argument qui ressemble à un chemin (séparateur ou extension)
  mais qui n'existe pas sur le disque ? → Erreur claire indiquant que le chemin
  est introuvable ; en multi-input, l'élément est ignoré et l'échec est signalé
  à la fin.
- Comment gérer une réponse LLM malformée (JSON invalide, texte autour, balise
  markdown) ? → Retente selon la politique de retry, puis marque l'élément en
  échec sans produire de JSON (cohérent avec le cas ambigu) ; les autres
  éléments continuent d'être traités.
- Comment gérer un nom de sortie en conflit après plusieurs suffixes (ex.
  `Titre-1.json` déjà pris) ? → Incrémenter X jusqu'à trouver un nom libre
  (`Titre-2.json`, etc.).
- Comment gérer un dossier en entrée contenant des sous-dossiers ? → Seuls les
  fichiers `.txt`/`.md` du dossier sont traités (les sous-dossiers sont ignorés,
  voir Assumptions).
- Comment gérer une entrée dont le titre contient uniquement des symboles ou
  fait moins de 7 caractères ? → Utiliser les caractères valides restants ; si
  aucun caractère exploitable, utiliser un nom de repli (ex. `sans_titre`).
- Comment gérer deux entrées produisant le même titre de sortie dans la même
  exécution ? → La règle de conflit s'applique aussi intra-exécution (deuxième
  élément suffixé `-1`).

## Requirements *(mandatory)*

### Functional Requirements

#### Détection et entrées

- **FR-001**: Le système DOIT accepter en entrée une chaîne de caractères, un
  fichier `.txt`, un fichier `.md`, plusieurs de ces éléments, ou un dossier ;
  il DOIT détecter automatiquement et de façon transparente s'il s'agit d'un ou
  plusieurs éléments. Règle de détection : un argument correspondant à un
  fichier/dossier existant est traité comme tel ; un argument sans syntaxe de
  chemin (ni séparateur, ni extension) est vectorisé comme chaîne littérale ; un
  argument avec une syntaxe de chemin mais inexistant déclenche une erreur
  claire.
- **FR-002**: Lorsqu'un dossier est fourni, le système DOIT ignorer tout fichier
  qui n'est ni `.txt` ni `.md`.
- **FR-003**: En multi-input, le système DOIT traiter chaque élément
  indépendamment et produire exactement une sortie JSON par élément, toutes
  écrites dans le même dossier de sortie.
- **FR-004**: En multi-input, le système DOIT regrouper les requêtes d'embedding
  par batch (25 par défaut), sauf si la taille de batch est 0 (une requête
  simple par texte). La reformulation LLM, elle, reste traitée élément par
  élément.

#### Sortie JSON

- **FR-005**: Chaque sortie DOIT être un objet JSON unique contenant :
  `schema_version` (défaut : `"Vector-1.0"`), `entrée` (texte original complet),
  `reformulation` (texte reformulé ou chaîne vide si option désactivée),
  `vecteur` (liste de floats de longueur `dimension_vecteur`),
  `dimension_vecteur` (entier, fonction du modèle d'embedding choisi),
  `nature_vecteur` (`float32` ou `float64`, fonction du modèle).
- **FR-006**: Le système DOIT créer par défaut un dossier `output` à la racine
  du projet et y inscrire les sorties, sauf si l'utilisateur fournit
  `--output-folder`.
- **FR-007**: Le titre de chaque fichier de sortie DOIT reprendre les 7 premiers
  caractères du titre d'entrée, en ignorant les symboles, simplifiant les
  accents et remplaçant les espaces par `_`.
- **FR-008**: En cas de conflit de nom de sortie, le système DOIT suffixer le
  titre de `-X` où X est un nombre commençant à 1 et incrémenté jusqu'à trouver
  un nom libre.

#### Modèles et options

- **FR-009**: Le système DOIT proposer trois modèles d'embedding Mistral — 1024
  dimensions (`mistral-embed`, défaut), 256 dimensions
  (`mistral-embed-dim256-2510`), 128 dimensions (`mistral-embed-dim128-2510`) —
  sélectionnables via `--choix-techno-embed` ; le choix détermine le nom de
  modèle utilisé dans l'appel API et la dimension du vecteur.
- **FR-010**: Le système DOIT accepter les modèles LLM suivants pour la
  reformulation via `--choix-modele-llm` (défaut `small`) : `large4`
  (mistral-large-4), `large`, `medium`, `small` (défaut), `14b`, `8b`, `3b`,
  `zai` (zai-glm-5-3).
- **FR-011**: Le système DOIT valider les bornes des options et refuser toute
  valeur hors bornes avec un message clair : `--taille-batch` (0-100, défaut
  25), `--retry-occurences` (0-10, défaut 3), `--retry-time` (1-10 s, défaut 3),
  `--temperature-llm` (0-1, défaut 0,2).

#### Reformulation

- **FR-012**: Le système DOIT utiliser le prompt de reformulation fourni sans
  modification, en y insérant le texte d'entrée, et exiger une réponse JSON
  strictement parsable (schéma `ambiguous`/`reformulation`/`options`). La
  reformulation ne s'applique qu'aux entrées courtes de type question (par
  défaut ≤ 500 caractères) ; les entrées plus longues sont vectorisées sans
  reformulation.
- **FR-013**: Quand la reformulation est activée et aboutit (`ambiguous: false`)
  sur une entrée éligible, le vecteur DOIT être celui de la reformulation ; le
  texte original reste dans `entrée`.
- **FR-014**: Quand la reformulation est activée mais que l'entrée est ambiguë
  bloquante (`ambiguous: true`) ou que la réponse LLM est malformée après
  retries, le système DOIT marquer l'élément en échec et ne produire aucune
  sortie pour lui ; en multi-input, les autres éléments continuent d'être
  traités et les échecs sont signalés à la fin.

#### Résilience et sécurité

- **FR-015**: En cas d'échec d'une requête API ou d'un batch, le système DOIT
  réessayer automatiquement avec délai exponentiel (délai initial
  `--retry-time`, doublé à chaque essai), jusqu'au nombre d'essais configuré
  (`--retry-occurences`).
- **FR-016**: Le système DOIT charger la clé API depuis la variable
  d'environnement `MISTRAL_API_KEY` (fichier `.env`) et ne JAMAIS la copier,
  l'afficher ou la journaliser ailleurs ; elle ne sert qu'aux appels API
  d'embedding et de LLM.
- **FR-017**: Le système DOIT échouer rapidement avec un message clair si la clé
  API est absente, avant tout appel réseau.
- **FR-018**: Toutes les données (entrées, sorties, journaux) DOIVENT rester sur
  la machine locale, conformément à la constitution du projet (local-first,
  aucun service tiers hors appels API Mistral explicites).

### Key Entities *(include if feature involves data)*

- **Élément d'entrée (InputItem)**: un texte à vectoriser — chaîne de caractères
  ou contenu d'un fichier `.txt`/`.md` — avec son titre source (pour la
  dérivation du nom de sortie) et son texte complet.
- **Résultat de vectorisation (OutputJSON)**: l'entité de sortie, composée du
  texte original, de la reformulation éventuelle, du vecteur, de sa dimension et
  de la nature de ses floats ; persistée sous `<titre>.json` dans le dossier de
  sortie.
- **Requête d'embedding par batch (EmbeddingBatch)**: regroupement temporaire de
  N textes (N = taille de batch) envoyé ensemble à l'API d'embedding, dont les
  résultats sont redistribués à chaque élément d'entrée.
- **Reformulation (LLMResponse)**: réponse du LLM, soit une question reformulée,
  soit une ambiguïté bloquante avec options d'interprétation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Les 6 fichiers du dossier `Examples/` traités en une seule
  commande produisent 6 JSON valides dans le dossier de sortie, chacun avec un
  vecteur de la dimension du modèle choisi.
- **SC-002**: Un utilisateur peut vectoriser une question unique et obtenir son
  JSON en moins de 10 secondes (hors reformulation LLM : moins de 30 secondes
  avec reformulation).
- **SC-003**: 100 % des fichiers de sortie respectent la convention de nommage
  (7 premiers caractères significatifs, accents simplifiés, espaces en `_`,
  suffixe `-X` en cas de conflit).
- **SC-004**: En cas d'échec API transitoire, la réussite du traitement est
  obtenue sans intervention de l'utilisateur dans au moins 95 % des cas grâce au
  retry automatique.
- **SC-005**: Chaque JSON produit est directement parsable et sa structure est
  identique quel que soit le type d'entrée (chaîne, `.txt`, `.md`) — la source
  est transparente pour l'utilisateur.
- **SC-006**: Aucune clé API n'apparaît dans les sorties, les journaux ou tout
  fichier écrit par l'outil.

## Assumptions

- Les sous-dossiers d'un dossier fourni en entrée ne sont pas parcourus
  récursivement ; seuls les fichiers `.txt`/`.md` du premier niveau sont
  traités.
- Un dossier en entrée et des fichiers individuels peuvent être mélangés dans la
  même commande ; tous les éléments retenus sont traités comme un multi-input.
- Le seuil séparant une « entrée courte de type question » (reformulable) d'un
  document long est fixé par défaut à 500 caractères ; un seuil différent pourra
  être ajouté en option sans changer le schéma de sortie.
- En cas de réponse ambiguë (`ambiguous: true`) ou malformée du LLM après
  retries, l'élément est marqué en échec et ne produit pas de sortie ; les
  options d'interprétation renvoyées ne sont pas persistées.
- La nature des floats (`float32`/`float64`) est déterminée par le modèle
  d'embedding utilisé et documentée dans la sortie, sans conversion de précision
  par l'outil.
- Le dossier `output` par défaut est créé à la racine du projet s'il n'existe
  pas ; les exécutions successives y ajoutent les fichiers sans jamais écraser
  les existants (règle de suffixe).
- Les encodages d'entrée sont gérés de façon standard (UTF-8 attendu) ; un
  fichier illisible est signalé et ignoré sans interrompre un multi-input.
- Les ressources documentaires du dossier `Ressources/` (doc Mistral d'octobre
  2026) font foi pour les noms exacts de modèles, presets de dimension et
  formats d'API d'embedding et de batch.
