# Idea Research: Sortie JSON regroupee (tableau) et option --ungroup

- **Slug**: regroupement-sorties
- **Created**: 2026-10-08
- **Evidence confidence (overall)**: medium

## Users & Demand

- Aucune demande externe documentee : l'idee emane de l'utilisateur
  du projet lui-meme, sans ticket, interview ni donnee d'usage tiers. —
  [source: intake.md] (confidence: high)
- Comportement observe : le dossier `output/` du projet contient des
  lots multi-fichiers issus d'executions multi-entrees (ex.
  `Tocquev.json` + `Tocquev-1.json` + `Tocquev-2.json`, `Corsen.json` +
  `Corsen-1.json`), ce qui montre un usage reel du multi-input avec la
  sortie actuelle un-fichier-par-entree. — [source: `output/` du depot]
  (confidence: medium)
- Aucune donnee sur le nombre d'entrees typiques par execution ni sur
  les consommateurs aval des fichiers JSON. —
  [NEEDS CLARIFICATION: qui consomme les fichiers Vector-1.0 aujourd'hui
  et en quel volume ?]

## Prior Art

- **Interne** : le contrat actuel impose « un fichier JSON `Vector-1.0`
  par element traite avec succes » (FR-005), avec nommage derive du
  titre source et suffixation des conflits (FR-007, FR-008) —
  `specs/001-text-vectorization/contracts/cli.md` et
  `data-model.md`. Les tests d'integration verifient explicitement
  un fichier par entree (ex. `test_fichiers_txt_et_md` attend
  `Corsen.json` + `Tocquev.json`) — [source: depot] (confidence: high)
- **Interne** : le format de sortie est codé dans
  `src/question2vector/output.py` (`OutputRecord.vers_dict()` produit
  un objet, jamais un tableau) ; `SCHEMA_VERSION = "Vector-1.0"` est
  teste en unitaire et en integration. Toute modification du format
  casse ces tests et le contrat. — [source: depot] (confidence: high)
- **Externe, precedent favorable au tableau** : l'API embeddings
  d'OpenAI renvoie nativement plusieurs embeddings dans une reponse
  unique sous forme de liste d'objets (`data: [{index, embedding, ...}]`)
  — un tableau d'enregistrements est donc un pattern reconnu pour
  transporter plusieurs vecteurs en un seul document. —
  [source: https://platform.openai.com/docs/guides/embeddings,
  https://developers.openai.com/api/docs/guides/batch] (confidence: medium)
- **Externe, convention contraire pour les fichiers** : pour des fichiers
  contenant plusieurs enregistrements, la convention industrielle est
  JSONL/NDJSON (un objet JSON par ligne), pas un tableau JSON :
  l'OpenAI Batch API exige un `.jsonl` en entree et fournit un
  `.jsonl` en sortie (« Batches start with a .jsonl file where each
  line contains the details of an individual request to the API ») ;
  BigQuery exige du NDJSON pour le chargement ; Spark, Elasticsearch,
  ClickHouse, DuckDB et Hugging Face utilisent JSON Lines. —
  [source: https://developers.openai.com/api/docs/guides/batch,
  https://ndjson.rest/case-studies/,
  https://www.elysiate.com/blog/ndjson-vs-json-array-streaming-friendly-interchange]
  (confidence: medium)
- **Externe, arbitrage tableau vs JSONL** : le tableau JSON reste
  recommande quand le document forme un tout coherent et que la taille
  est moderee ; JSONL surpasse le tableau au-dela d'environ 10 Mo ou
  pour le streaming/appending (un tableau doit etre parse d'un bloc et
  ne supporte pas l'ajout increment). —
  [source: https://jsonltools.com/what-is-ndjson,
  https://superjson.ai/blog/2025-09-07-jsonl-vs-json-data-processing/]
  (confidence: medium)
- **Externe, preservation du lien entree/sortie** : les systemes de
  batch (OpenAI, Parasail) associent chaque sortie a son entree par un
  identifiant (`custom_id` ou `index`), car l'ordre seul ne suffit pas
  toujours. Le format propose, qui regroupe plusieurs entrees dans un
  seul fichier sans identifiant, devra garantir la tracabilite
  entree → enregistrement. —
  [source: https://docs.parasail.io/parasail-docs/batch/batch-file-format,
  https://stackoverflow.com/questions/74907244] (confidence: medium)

## Market & Context

- Alternative actuelle : l'utilisateur multi-entrees recupere N
  fichiers `.json` dans `output/` et doit lui-merger les fusionner
  (script `jq`, concatenation manuelle) pour les charger d'un bloc dans
  un consommateur aval. Cout de l'inaction : friction d'assemblage a
  chaque usage multi-entree. — ASSUMPTION (aucun consommateur aval
  identifie) (confidence: low)
- Les bases vectorielles et pipelines ML ingerent typiquement des lots
  (arrays ou JSONL) ; aucun standard n'impose le tableau JSON ni le
  JSONL pour un fichier de sortie d'outil CLI autonome. —
  [source: https://ndjson.com/use-cases/machine-learning/] (confidence: medium)

## Data & Constraints

- Taille des donnees : un enregistrement contient le texte d'entree
  complet plus un vecteur de 128 a 1024 floats ; en JSON texte, un
  float ~ 20 caracteres, soit ~20 Ko a 160 Ko par vecteur seul. Un
  fichier groupe reste compact pour des dizaines d'entrees, mais le
  tableau JSON impose un chargement integral en memoire. — ASSUMPTION
  sur les volumes reels d'usage (confidence: low)
- Constitution du projet : la modification ne touche ni les secrets ni
  le local-first (principes I-II non concernes) ; en revanche le
  principe IV (Simplicite/YAGNI) s'applique a l'ajout d'une option
  `--ungroup` : elle devra etre justifiee face au comportement par
  defaut. — [source: `.specify/memory/constitution.md`] (confidence: high)
- Contrat CLI existant : toutes les options actuelles prennent une
  valeur (`on`/`no`, entier, chemin) ; `--ungroup` tel que decrit serait
  le premier drapeau sans valeur du contrat, ou devrait suivre le
  pattern `--reformule on|no`. — [source:
  `specs/001-text-vectorization/contracts/cli.md`] (confidence: high)
- Impact tests : `tests/integration/test_single.py` et
  `tests/unit/test_output.py` assert le format objet actuel
  (`schema_version`, cle `entrée`, etc.) ; toute evolution du format
  exige de les reecrire. — [source: depot] (confidence: high)
- Semantique d'echec partiel : aujourd'hui, un element en echec ne
  produit simplement pas de fichier ; en mode groupe, il faut definir
  si le fichier unique contient uniquement les reussites, et ce que
  devient le code de sortie 2. — [source: contrat CLI actuel,
  codes de sortie] (confidence: high)

## Evidence Against the Idea

- **Divergence avec la convention fichier** : pour des fichiers
  multi-enregistrements, l'industrie ML/data privilegie JSONL, pas le
  tableau JSON ; le format propose s'ecarte du precedent dominant,
  meme s'il reste valide a echelle moderee. — [sources citees
  ci-dessus] (confidence: medium)
- **Rupture de format** : le passage objet → tableau casse la
  compatibilite avec tous les consommateurs (et tests) du format
  `Vector-1.0` actuel ; la valeur de `schema_version` et l'absence de
  strategie de transition pesent sur l'idee. — [source: depot]
  (confidence: high)
- **Perte de tracabilite par nom de fichier** : le nommage actuel
  (FR-007/FR-008) lie chaque sortie a sa source ; un fichier groupe
  unique doit reinventer cette liaison (ordre ? identifiant ?) sous
  peine de perdre une fonctionnalite existante. — [source:
  data-model.md] (confidence: high)
- **YAGNI** : aucune demande externe ni consommateur identifie ne
  justifie aujourd'hui le regroupement ; le benefice repose sur
  l'usage personnel de l'auteur. — ASSUMPTION (confidence: medium)
- **Echec partiel non specifie** : le comportement du fichier groupe
  quand certaines entrees echouent n'est defini nulle part dans l'idee.
  — [source: intake.md] (confidence: high)

## Gaps & Open Questions

- [NEEDS CLARIFICATION: qui consomme les fichiers de sortie et dans
  quel outil (base vectorielle, script, LLM) ? Le tableau JSON est-il
  impose par ce consommateur ?]
- [NEEDS CLARIFICATION: nom du fichier unique en mode groupe (fixe ?
  derive de quoi ?) et gestion des conflits si le fichier existe deja]
- [NEEDS CLARIFICATION: en mode `--ungroup`, chaque fichier contient-il
  un tableau a un element ?]
- [NEEDS CLARIFICATION: `schema_version` change-t-il (Vector-2.0 ?) et
  une transition/migration des sorties existantes est-elle requise ?]
- [NEEDS CLARIFICATION: comportement du fichier groupe en echec
  partiel (reussites seules ? code de sortie ?) et en cas d'entree
  unique (tableau a 1 element ?)]
- [NEEDS CLARIFICATION: syntaxe de `--ungroup` — drapeau sans valeur
  ou option `on`/`no` coherente avec le contrat existant ?]
- [NEEDS CLARIFICATION: volumes cibles — nombre d'entrees par
  execution — pour arbitrer tableau JSON vs JSONL]

## Sources

Sources collectees via recherche web (snippets de moteur, pages non
integrallement ouvertes — fiabilite medium) :

- <https://developers.openai.com/api/docs/guides/batch> (host:
  developers.openai.com, policy: allowlisted via recherche)
- <https://platform.openai.com/docs/guides/embeddings> (host:
  platform.openai.com, policy: recherche)
- <https://ndjson.rest/case-studies/> (host: ndjson.rest, policy:
  recherche, host non liste — snippet seulement)
- <https://jsonltools.com/what-is-ndjson> (host: jsonltools.com,
  policy: recherche, snippet seulement)
- <https://superjson.ai/blog/2025-09-07-jsonl-vs-json-data-processing/>
  (host: superjson.ai, policy: recherche, snippet seulement)
- <https://www.elysiate.com/blog/ndjson-vs-json-array-streaming-friendly-interchange>
  (host: elysiate.com, policy: recherche, snippet seulement)
- <https://docs.parasail.io/parasail-docs/batch/batch-file-format>
  (host: docs.parasail.io, policy: recherche, snippet seulement)
- <https://stackoverflow.com/questions/74907244/how-can-i-use-batch-embeddings-using-openais-api>
  (host: stackoverflow.com, policy: allowlisted via recherche)
- <https://ndjson.com/use-cases/machine-learning/> (host: ndjson.com,
  policy: recherche, snippet seulement)

Sources internes (lecture directe, fiabilite haute) : `intake.md`,
`specs/001-text-vectorization/{contracts/cli.md,data-model.md}`,
`src/question2vector/output.py`, `tests/integration/test_single.py`,
`tests/unit/test_output.py`, `.specify/memory/constitution.md`,
dossier `output/` du depot.
