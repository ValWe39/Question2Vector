# Question2Vector

Outil CLI 100 % local qui vectorise une chaine de caracteres, un
fichier `.txt`/`.md`, un dossier ou un melange de ces elements via les
embeddings Mistral, avec reformulation LLM optionnelle.

## Installation

```bash
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"   # Windows
# ou : .venv/bin/pip install -e ".[dev]"   # Linux / macOS
```

Copiez `.env.example` vers `.env` et renseignez votre cle :

```text
MISTRAL_API_KEY=YOUR_API_KEY
```

Le fichier `.env` est exclu de git (cf. `.gitignore`).

Sur Windows (PowerShell), le venv n'est pas toujours active : dans ce cas,
appelez directement l'executable du venv, sans activation :

```text
.venv\Scripts\vector "de quelle couleur est le cheval blanc d'heri IV ?"
```

Pour activer le venv, si la strategie d'execution de PowerShell bloque
`Activate.ps1`, autorisez les scripts pour la fenetre en cours puis
activez :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
```

Apres activation, le prompt affiche un prefixe `(...)` et la commande
`vector` seule suffit ; `deactivate` pour sortir.

## Usage

```bash
vector "Comment fonctionne le depot git ?"      # chaine
vector Examples/Corsen.txt Examples/Tocqueville2.md   # fichiers
vector Examples/                               # dossier complet
vector --reformule on "Ca marche comment ?"     # avec reformulation LLM
```

Par defaut, toutes les questions vectorisees du run sont regroupees
dans un seul fichier `output/sortie.json` (dossier configurable via
`--output-folder`) : un tableau JSON `Vector-2.0`, avec un
enregistrement par entree, dans l'ordre des arguments.

```text
[
  {
    "schema_version": "Vector-2.0",
    "entree": ...,
    "reformulation": ...,
    "vecteur": [float, ...],
    "dimension_vecteur": ...,
    "nature_vecteur": "float32"
  }
]
```

Une entree en echec produit un enregistrement reduit a trois champs
(`schema_version`, `entree`, `motif_echec`), sans vecteur. L'option
`--ungroup on` restaure une sortie par entree, chaque fichier
restant un tableau a un enregistrement.

| Option | Valeurs | Bornes | Defaut |
| ------ | ------- | ------ | ------ |
| `--choix-techno-embed` | `1024`, `256`, `128` | - | `1024` |
| `--taille-batch` | entier | 0 a 100 | `25` |
| `--reformule` | `on`, `no` | - | `no` |
| `--choix-modele-llm` | alias LLM (liste ci-dessous) | - | `small` |
| `--retry-occurences` | entier | 0 a 10 | `3` |
| `--retry-time` | entier (secondes) | 1 a 10 | `3` |
| `--temperature-llm` | decimal | 0 a 1 | `0,2` |
| `--output-folder` | chemin | - | `output/` |
| `--ungroup` | `on`, `no` | - | `no` |

Alias LLM valides : `large4` (mistral-large-4), `large`
(mistral-large-latest), `medium` (mistral-medium-latest), `small`
(mistral-small-latest, defaut), `14b` (ministral-14b-latest), `8b`
(ministral-8b-latest), `3b` (ministral-3b-latest), `zai` (zai-glm-5-3).

`--taille-batch 0` desactive le regroupement en lots : une requete
d'embedding par texte. La reference complete du contrat CLI est dans
[contracts/cli.md](specs/002-sortie-tableau-json/contracts/cli.md).

## Tests

```bash
.venv/Scripts/python -m pytest
```

Aucun test n'accede au reseau : le client Mistral est remplace par un
fictif.

## Validation

Le guide de validation pas a pas est dans
[quickstart.md](specs/002-sortie-tableau-json/quickstart.md).

## Licence

MIT — voir [LICENSE](LICENSE).
