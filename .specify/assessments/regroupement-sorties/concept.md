# Concept: Livrable de sortie unique pour les runs multi-entrees

- **Slug**: regroupement-sorties
- **Created**: 2026-10-08
- **Recommended option**: Option B — Tableau JSON groupe par defaut,
  sortie par entree en option

## Options

### Option A — Ne rien construire (statu quo documente)

- **Sketch**: l'outil continue de produire un fichier JSON objet
  par entree dans `output/`. Le README documente une recette de
  fusion (par ex. une ligne `jq -s . output/*.json > lot.json`)
  pour assembler les resultats en un jeu unique quand l'utilisateur
  en a besoin.
- **Appetite**: nul (quelques lignes de documentation)
- **Trade-offs**: gagne — zero rupture du contrat `Vector-1.0`,
  zero code, zero test reecrit. Sacrifie — le but premier
  (consommer en bloc sans assemblage manuel) n'est tenu que par un
  outil externe (`jq`) non garanti sous Windows PowerShell natif ;
  la friction demeure a chaque run multi-entrees ; le format reste
  incapable de porter plusieurs question-vecteurs.
- **Rabbit holes**: aucun ; mais l'arbitrage se reposera plus tard
  sur un stock de sorties existantes plus grand a migrer.

### Option B — Tableau JSON groupe par defaut, sortie par entree en option

- **Sketch**: la sortie devient toujours un tableau JSON
  (`[ {record}, {record}, ... ]`), identique qu'il y ait une ou
  plusieurs entrees. Par defaut, toutes les question-vecteurs du
  run aboutissent dans un seul fichier JSON. Une option CLI laisse
  a l'utilisateur le choix d'une sortie par entree, chaque fichier
  restant au format tableau. Le consommateur charge un document
  unique ; l'utilisateur habituel au fichier-par-entree retrouve
  son usage via l'option.
- **Appetite**: small (quelques jours — `output.py`, options CLI,
  tests et contrat a reecrire)
- **Trade-offs**: gagne — tient directement les quatre buts
  (livrable unique, format uniforme, maitrise du mode de livraison,
  tracabilite a definir dans le livrable) ; aligne avec le pattern
  reponse API (liste d'objets embeddings). Sacrifie — rupture du
  contrat `Vector-1.0` objet (tests, README, contrats spec 001) ;
  s'ecarte de la convention JSONL pour les fichiers multi-records
  (valide a l'echelle moderee observee, sans appui au-dela) ; le
  nommage actuel lie-a-la-source (FR-007/FR-008) doit etre repense
  pour le livrable unique.
- **Rabbit holes**: semantique d'echec partiel du livrable unique
  (reussites seules ? code de sortie ?) ; regle de nommage et de
  conflit du fichier groupe ; conservation de la tracabilite
  entree → enregistrement (ordre, champ identifiant) ; decision de
  version de schema (`Vector-2.0` ?) et eventuelle coexistence des
  deux formes ; tentation d'ajouter des metadonnees de run
  (horodatage, options) dans le livrable — hors sujet.

### Option C — Livrable JSONL groupe, sortie par entree en option

- **Sketch**: meme livraison que B (un fichier unique par defaut,
  option par-entree), mais le format du fichier groupe est JSONL :
  une question-vecteur par ligne, un objet JSON par ligne. Chaque
  ligne garde la structure actuelle des champs.
- **Appetite**: small (equivalent a B)
- **Trade-offs**: gagne — conforme a la convention industrielle
  pour les fichiers multi-enregistrements (OpenAI Batch, BigQuery,
  Spark...) ; streamable, appendable, robuste aux lignes
  corrompues ; la sortie par entree reste un JSON classique.
  Sacrifie — diverge de la solution envisagee par l'auteur (tableau
  JSON explicite) ; un `.jsonl` n'est pas lisible d'un bloc par un
  lecteur JSON standard (deux formats de fait au lieu d'un) ; le
  caractere « un meme format qu'il y ait une ou plusieurs
  question-vecteurs » est affaibli entre le mode groupe et le mode
  par entree.
- **Rabbit holes**: les memes que B (echec partiel, nommage,
  tracabilite, version de schema), plus l'arbitrage double format
  JSON/JSONL qui double la surface de tests et de documentation.

## Recommendation

**Option B**. Elle est la mise en oeuvre la plus directe des buts
du probleme : livrable unique chargeable en une lecture (metrique :
zero etape de fusion manuelle), format identique quel que soit le
nombre d'entrees (metrique : une seule forme de document), maitrise
utilisateur du mode de livraison (l'option restaure l'usage
existant). L'appetite est small et le projet est jeune (un seul
mainteneur, spec 001 seule publiee) : le cout de la rupture du
format `Vector-1.0` est aujourd'hui minimal. L'option C est plus
conforme aux conventions fichiers mais n'apporte de benefice reel
qu'a grande echelle, qu'aucune donnee ne documente ; elle affaiblit
en revanche la transparence de format recherchee. L'option A ne
tient aucun but. La variante minimale de B (groupement obligatoire
sans option) est ecartee : elle supprimerait l'usage actuel
fichier-par-entree sans gain de simplicite significatif.

## Out of Scope (for the recommended option)

- Toute modification du pipeline de vectorisation (detection,
  reformulation, embeddings, batches, retries) — herite des
  non-goals.
- Nouveaux types d'entrees, nouvelles cibles de sortie (base
  vectorielle, binaire, compression) — herite.
- Cloud, sync, stockage distant — herite (constitution II-III).
- Format JSONL pour le livrable groupe — ecarte au profit du
  tableau JSON unique et uniforme.
- Outil de migration des sorties `Vector-1.0` existantes (le
  dossier `output/` est un artefact local jetable de
  l'utilisateur).
- Metadonnees de run (horodatage, options, compteurs) dans le
  livrable — aucune demande.
- Optimisation memoire/streaming a grande echelle — aucun volume
  cible documente.

## Assumptions to Validate

- Les volumes reels restent modestes (dizaines d'entrees, < 10 Mo
  par livrable) : le tableau JSON charge en memoire ne pose pas de
  probleme. Si des runs massifs existent, revisiter l'option C.
- Le consommateur aval sait charger un tableau JSON d'objets (aucun
  consommateur identifie a ce jour — a confirmer aupres de
  l'auteur).
- La tracabilite entree → enregistrement peut etre portee par
  l'ordre du tableau ou un champ existant, sans nouveau champ
  d'identification.
- La rupture du format `Vector-1.0` est acceptable : pas de
  consommateur externe connu, projet pre-adoption, tests du depot
  seul impact.
- Une entree unique produit un tableau a un element (transparence
  du format), et l'option par-entree produit egalement des
  tableaux (a un element).
