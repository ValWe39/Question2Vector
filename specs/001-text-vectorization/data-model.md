# Data Model: feature 001-text-vectorization

**Date**: 2026-10-07

**Spec**: [spec.md](spec.md)

**Plan**: [plan.md](plan.md)

## Entités

### InputItem (élément d'entrée)

Un texte à vectoriser, détecté depuis les arguments CLI.

- **Champs** :
  - `source_type` : `chaîne` | `txt` | `md`
  - `titre_source` : chaîne non vide (nom de fichier sans extension, ou
    texte brut pour une chaîne) — sert au nommage de la sortie
  - `texte` : contenu textuel complet (UTF-8), jamais vide
- **Règles de détection** (FR-001) :
  - argument correspondant à un fichier existant `.txt`/`.md` → fichier
  - argument correspondant à un dossier existant → 1 InputItem par
    fichier `.txt`/`.md` du premier niveau (FR-002) ; les autres formats
    sont ignorés silencieusement ; aucun fichier éligible → erreur claire
  - argument sans syntaxe de chemin (ni séparateur, ni extension) →
    chaîne littérale
  - argument avec syntaxe de chemin inexistant → erreur claire,
    l'élément est ignoré et l'échec signalé à la fin
- **Transitions d'état** :
  `detecté → lu` (échec si fichier illisible ou vide : l'élément est
  signalé non traitable, sans crash global)

### VectorizationOptions (options CLI normalisées)

Résultat du parsing d'argparse, validé avant tout appel API (FR-011).

| Champ | Type | Bornes | Défaut |
|-------|------|--------|--------|
| `embed_model` | `1024` \| `256` \| `128` | — | `1024` |
| `batch_size` | int | 0-100 | 25 |
| `reformule` | bool | — | false |
| `llm_model_alias` | un des 8 alias (cf. LlmModelRef) | — | `small` |
| `retry_occurrences` | int | 0-10 | 3 |
| `retry_time` | int (s) | 1-10 | 3 |
| `output_folder` | chemin | — | `output/` |
| `temperature_llm` | float | 0-1 | 0,2 |

Toute valeur hors bornes → refus immédiat avec message clair, code de
sortie d'erreur de configuration.

### EmbeddingModelRef (référentiel des modèles)

Table de correspondance stricte (FR-009, doc Mistral) :

| Alias | Nom API | Dimension | Nature |
|-------|---------|-----------|--------|
| `1024` | `mistral-embed` | 1024 | float32 |
| `256` | `mistral-embed-dim256-2510` | 256 | float32 |
| `128` | `mistral-embed-dim128-2510` | 128 | float32 |

Le choix détermine le `model` de la requête API, la dimension du vecteur
et les champs `dimension_vecteur`/`nature_vecteur` de la sortie.

### LlmModelRef (référentiel LLM)

| Alias | Nom API |
|-------|---------|
| `large4` | `mistral-large-4` |
| `large` | `mistral-large-latest` |
| `medium` | `mistral-medium-latest` |
| `small` | `mistral-small-latest` (défaut) |
| `14b` | `ministral-14b-latest` |
| `8b` | `ministral-8b-latest` |
| `3b` | `ministral-3b-latest` |
| `zai` | `zai-glm-5-3` |

### ReformulationResult (réponse LLM)

- **Champs** (schéma JSON imposé par le prompt, FR-012) :
  - `ambiguous` : bool
  - `reformulation` : chaîne non vide si `ambiguous` est faux, sinon `null`
  - `options` : liste de chaînes, présente seulement si `ambiguous` est
    vrai (non persistée dans la sortie)
- **Validation** : parsing JSON strict (JSON mode API + contrôle du
  schéma) ; toute réponse malformée après retries → échec de l'élément
- **Éligibilité** : la reformulation ne s'applique qu'aux InputItem de
  texte ≤ 500 caractères (FR-012) ; les documents longs passent
  directement à l'embedding, `reformulation` reste vide

### OutputRecord (schéma de sortie `Vector-1.0`)

Un fichier JSON par élément traité avec succès (FR-005) :

- `schema_version` : chaîne, toujours `"Vector-1.0"`
- `entrée` : texte original complet (chaîne ou contenu du fichier)
- `reformulation` : chaîne (vide si option désactivée ou entrée non
  éligible)
- `vecteur` : liste de floats de longueur exactement `dimension_vecteur`
- `dimension_vecteur` : 1024 | 256 | 128
- `nature_vecteur` : `"float32"` (cf. research.md, point 9)

**Invariant** : `len(vecteur) == dimension_vecteur` ; si l'API renvoie
une autre dimension que le référentiel du modèle, l'élément échoue (erreur
surfaite des appels, signalée).

### OutputFileName (nommage des sorties)

Dérivé de `titre_source` (FR-007, FR-008) :

1. prendre les 7 premiers caractères significatifs : ignorer les
   symboles, simplifier les accents (é→e, ç→c…), remplacer les espaces
   par `_`
2. si aucun caractère exploitable (titre en symboles uniquement) :
   repli `sans_titre`
3. en cas de conflit avec un fichier existant (ou un titre déjà produit
   dans la même exécution) : suffixe `-X`, X démarrant à 1 et incrémenté
   jusqu'à nom libre
4. extension `.json`

### ProcessingReport (bilan d'exécution)

- **Champs** : par InputItem — statut (`ok` | `echec`), fichier écrit le
  cas échéant, motif d'échec le cas échéant ; clé API et contenus jamais
  inclus.
- **Usage** : résumé affiché en console en fin d'exécution ; les échecs
  sont signalés à la fin sans interrompre les autres éléments (FR-014,
  cas limites de la spec).

## Relations

```text
VectorizationOptions ──détermine──> EmbeddingModelRef, LlmModelRef
InputItem ──0..1──> ReformulationResult   (si éligible et --reformule on)
InputItem + vecteur ──1──> OutputRecord    (si succès)
OutputRecord ──sérialise──> OutputFileName.json (dans output_folder)
N InputItems ──regroupés──> EmbeddingBatch (N = batch_size)
```
