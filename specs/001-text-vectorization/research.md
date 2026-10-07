# Research: feature 001-text-vectorization

**Date**: 2026-10-07

**Spec**: [spec.md](spec.md)

**Plan**: [plan.md](plan.md)

Sources: documentation Mistral d'octobre 2026 (`Ressources/Mistral/`),
constitution du projet (`v1.4.0`), outillage CI existant (Ruff, pip-audit,
pre-commit), examen du dépôt.

## Décisions

### 1. Langage : Python 3.11+

- **Decision**: Python 3.11 ou supérieur.
- **Rationale**: l'outillage du dépôt est déjà Python (Ruff, pip-audit, hooks
  pre-commit en scripts Python) ; le SDK officiel Mistral documenté dans les
  ressources est Python (`pip install mistralai`) ; l'écosystème de tests est
  standard.
- **Alternatives considered**: TypeScript (SDK `@mistralai/mistralai`
  disponible) — écarté car le CI du projet ne linterait pas ce code ; appel
  HTTP direct en tout langage — moins maintenable.

### 2. Accès API : SDK officiel `mistralai`

- **Decision**: utiliser le SDK officiel `mistralai` (client `Mistral` avec
  `api_key`), enveloppé dans `mistral_client.py`.
- **Rationale**: la documentation fournie (`api-nettoye.md`,
  `embedders-nettoye.md`, `first-api-request-nettoye.md`) documente ce SDK ;
  il gère l'authentification, la sérialisation et les erreurs ; Mistral est
  européen (préférence souveraine de la constitution). L'enveloppe fine garde
  le reste du code testable sans réseau.
- **Alternatives considered**: `httpx`/`requests` bruts sur `/v1/embeddings`
  et `/v1/chat/completions` — réimplémenterait auth, erreurs et types pour
  aucun gain ; retenu uniquement comme fallback si le SDK s'avérait
  inadéquat.

### 3. Modèles d'embedding : correspondance exacte

- **Decision**: table de correspondance stricte issue de la doc
  (`embedders-nettoye.md`) :
  - 1024 → `mistral-embed` (défaut), preset MISTRAL_EMBED_DIM_1024
  - 256 → `mistral-embed-dim256-2510`, preset MISTRAL_EMBED_DIM_256
  - 128 → `mistral-embed-dim128-2510`, preset MISTRAL_EMBED_DIM_128
- **Rationale**: le nom du modèle dans la requête API et la dimension du
  vecteur en dépendent (FR-009) ; la doc donne les constantes officielles
  (`MODEL_1024_EMBEDDING`, `MODEL_256_EMBEDDING`, `MODEL_128_EMBEDDING`).
- **Alternatives considered**: aucune — la doc fait foi.

### 4. CLI : argparse (stdlib)

- **Decision**: argparse de la stdlib pour toutes les options.
- **Rationale**: constitution IV (YAGNI) ; les 8 options sont simples ;
  zéro dépendance supplémentaire.
- **Alternatives considered**: `click`, `typer` — dépendances non justifiées.

### 5. Clé API : `.env` lu par `python-dotenv`

- **Decision**: charger `MISTRAL_API_KEY` depuis l'environnement, avec
  `.env` lu par `python-dotenv` (MIT). Échec rapide si absente (FR-017).
  Un `.env.example` avec placeholder `YOUR_API_KEY` est committé ; le
  `.env` réel est déjà couvert par `.gitignore` (vérifié).
- **Rationale**: standard Python, conforme constitution I ; la clé ne
  transite jamais dans les arguments, les logs ni les sorties.
- **Alternatives considered**: parsing manuel du `.env` — fragile (quotes,
  commentaires, encodage) ; injection manuelle `export` — friction
  multi-OS (PowerShell/bash).

### 6. Reformulation : JSON mode + parsing strict

- **Decision**: appel `chat.complete` avec `response_format`
  `{"type": "json_object"}` (documenté dans `json_mode-nettoye.md`), le
  prompt de reformulation fourni dans la spec étant passé comme message.
  Parsing strict du JSON renvoyé ; si `ambiguous: true` ou JSON invalide
  après retries → élément en échec, aucune sortie (FR-014).
- **Rationale**: le JSON mode garantit une sortie parsable, en complément
  du prompt qui impose déjà le schéma ; le comportement d'échec a été
  tranché en clarification (session 2026-10-07).
- **Alternatives considered**: parsing tolérant avec extraction au
  premier `{` — masque des erreurs et contredit la décision de rejet.

### 7. Batching : découpage applicatif

- **Decision**: découper la liste des textes en groupes de taille
  `--taille-batch` (25 par défaut) côté application et envoyer chaque
  groupe au endpoint embeddings (une requête, liste d'entrées) ;
  redistribuer les vecteurs à chaque élément. Si taille 0 : une requête
  par texte, sans regroupement (FR-004). La reformulation LLM reste
  élément par élément.
- **Rationale**: le endpoint embeddings accepte une liste d'entrées ; le
  regroupement est une exigence explicite de la spec.
- **Alternatives considered**: `MistralEmbedder` du Search Toolkit
  (`embedders-nettoye.md`) — conçu pour l'ingestion de chunks de recherche,
  apporterait des dépendances et concepts non requis (YAGNI).

### 8. Retry : backoff exponentiel applicatif

- **Decision**: boucle de retry maison autour des appels SDK : délai
  initial `--retry-time` (3 s), doublé à chaque essai (3, 6, 12), jusqu'à
  `--retry-occurences` (3). Appliqué par requête (embedding ou batch) et
  par appel LLM.
- **Rationale**: exigence explicite de la spec (FR-015) ; la doc Mistral
  fournie ne documente pas de retry natif pour les embeddings.
- **Alternatives considered**: `tenacity` — dépendance non justifiée pour
  une boucle de 10 lignes (YAGNI).

### 9. Nature des floats du vecteur : `float32`

- **Decision**: renseigner `nature_vecteur: "float32"` pour les trois
  modèles d'embedding, par convention Mistral. À confirmer en
  implémentation sur une réponse API réelle (tâche dédiée dans tasks.md).
- **Rationale**: la sérialisation JSON renvoie des nombres décimaux que
  Python lit en float64 ; le champ documente la précision du modèle
  embarqué, pas celle du stockage. La doc fournie ne précise pas la
  nature exacte : la valeur est vérifiable empiriquement en une requête.
- **Alternatives considered**: `float64` — aucun modèle d'embedding
  n'utilise cette précision en pratique ; si la vérification réelle
  contredit, la table de correspondance sera corrigée (une ligne).

### 10. Tests : `pytest` + `unittest.mock`

- **Decision**: `pytest` avec mocks stdlib sur `mistral_client.py`
  (interface fine injectée dans les services).
- **Rationale**: aucun réseau en test (constitution II) ; zéro dépendance
  de test au-delà de pytest ; le hook pre-commit Ruff et le job CI lint
  couvrent le style.
- **Alternatives considered**: `respx` (mock httpx) — couple les tests à
  l'implémentation HTTP du SDK ; `pytest-mock` — sucre syntaxique non
  indispensable.

## Verifications d'implementation (2026-10-07)

Les deux points différés en tâche sont résolus :

- **Licences des dépendances** (T031) : `mistralai` Apache-2.0,
  `python-dotenv` BSD-3-Clause, `pytest` MIT (dev) ; transitives
  permissives (pydantic MIT, anyio MIT, h11 MIT, idna BSD,
  packaging Apache-2.0/BSD, colorama BSD). Seul écart au « préféré » :
  `certifi` en MPL-2.0, open-source acceptable. Aucun tracker ni
  télémétrie détecté dans les paquets installés.
- **Nature des vecteurs** (T028) : une requête réelle sur
  `mistral-embed` confirme 1024 dimensions et des valeurs dyadiques à
  7-8 chiffres significatifs, typiques de la précision float32 ; la
  table `EmbeddingModelRef` est confirmée telle quelle.

## Inconnues résiduelles

Aucune balise NEEDS CLARIFICATION ne subsiste.
