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

Options principales : `--choix-techno-embed` (1024, 256 ou 128
dimensions, defaut 1024), `--taille-batch` (0 a 100, defaut 25),
`--choix-modele-llm`, `--retry-occurences`, `--retry-time`,
`--temperature-llm`, `--output-folder`.

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
