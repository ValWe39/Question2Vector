# Quickstart: valider la feature 001-text-vectorization

**Date**: 2026-10-07 | **Spec**: [spec.md](spec.md) |
**Contrat CLI**: [contracts/cli.md](contracts/cli.md)

Guide de validation exécutable bout-en-bout. Les détails des champs
sortie sont dans [data-model.md](data-model.md).

## Prérequis

1. Python 3.11+ installé
1. Clé API Mistral valide dans un fichier `.env` à la racine du projet
   (déjà couvert par `.gitignore`) :

```text
MISTRAL_API_KEY=YOUR_API_KEY
```

1. Installer l'outil en mode éditable :

```bash
pip install -e .
```

## Scénarios de validation

### Scénario 1 - Chaîne unique (scénario minimal)

```bash
vector "Comment fonctionne le dépôt git ?"
```

Attendu : code de sortie `0` ; un fichier JSON créé dans `output/`,
nommé d'après les 7 premiers caractères significatifs de la chaîne
(`Comment` → `Comment.json`), contenant les six champs du schéma
`Vector-1.0` avec `dimension_vecteur: 1024` et un vecteur de 1024
floats ; `reformulation` vide (option désactivée).

### Scénario 2 - Fichiers .txt et .md

```bash
vector Examples/Corsen.txt Examples/Tocqueville2.md
```

Attendu : deux JSON dans `output/`, chacun avec le contenu intégral du
fichier dans `entrée` et un vecteur ; le Markdown est traité comme du
texte brut (aucune transformation).

### Scénario 3 - Dossier en multi-input avec batching

```bash
vector Examples/
```

Attendu : 6 JSON (3 `.txt`, 3 `.md`) dans `output/`, un par fichier
éligible ; les requêtes d'embedding regroupées en un seul batch de 25
par défaut. Conforme à SC-001.

### Scénario 4 - Reformulation activée

```bash
vector --reformule on "Ça marche comment ?"
```

Attendu : le JSON contient la reformulation renvoyée par le LLM dans
`reformulation` et le vecteur correspond à la reformulation ; le texte
original reste dans `entrée`.

Variante ambiguë : une question volontairement ambiguë (ex. « Comment
l'importer ? » sans contexte) doit produire un échec de l'élément sans
fichier de sortie, signalé dans le résumé, code de sortie `2`.

Variante document long : `vector --reformule on Examples/CourCptes1.txt`
ne déclenche aucune reformulation (entrée > 500 caractères) ; le vecteur
porte sur le texte original, `reformulation` vide.

### Scénario 5 - Options de configuration

```bash
vector --choix-techno-embed 256 --taille-batch 0 \
       --output-folder resultats/ Examples/Corsen.txt
```

Attendu : JSON dans `resultats/` avec `dimension_vecteur: 256` et un
vecteur de 256 floats ; embedding envoyé en requête simple sans batch.

Variante bornes : `vector --taille-batch 150 Examples/Corsen.txt` doit
échouer avant tout appel API avec un message clair (code de sortie `1`).

### Scénario 6 - Conflit de nommage

Relancer le scénario 1. Attendu : le nouveau fichier est nommé
`Comment-1.json` (suffixe numérique, la sortie existante jamais
écrasée).

### Scénario 7 - Sécurité

```bash
MISTRAL_API_KEY= vector "test"
```

Attendu : échec immédiat avant tout appel réseau, message clair sur la
clé manquante, code de sortie `1` ; la clé n'apparaît jamais dans les
messages, les logs ou les fichiers de sortie.

## Tests automatisés

```bash
pytest
```

Attendu : suite verte (tests unitaires sans réseau — client Mistral
mocké — et tests d'intégration du flux complet).
