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

Chaque element traite produit un JSON `Vector-1.0` dans `output/`
(dossier configurable via `--output-folder`) :

```text
schema_version, entree, reformulation, vecteur,
dimension_vecteur, nature_vecteur
```

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

Alias LLM valides : `large4` (mistral-large-4), `large`
(mistral-large-latest), `medium` (mistral-medium-latest), `small`
(mistral-small-latest, defaut), `14b` (ministral-14b-latest), `8b`
(ministral-8b-latest), `3b` (ministral-3b-latest), `zai` (zai-glm-5-3).

`--taille-batch 0` desactive le regroupement en lots : une requete
d'embedding par texte. La reference complete est dans
[contracts/cli.md](specs/001-text-vectorization/contracts/cli.md).

La reference complete est dans
[contracts/cli.md](specs/001-text-vectorization/contracts/cli.md).

## Tests

```bash
.venv/Scripts/python -m pytest
```

Aucun test n'accede au reseau : le client Mistral est remplace par un
fictif.

## Validation

Le guide de validation pas a pas est dans
[quickstart.md](specs/001-text-vectorization/quickstart.md).

## Licence

MIT — voir [LICENSE](LICENSE).
