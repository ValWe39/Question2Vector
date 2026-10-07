# Contrat d'interface CLI : commande `vector`

**Date**: 2026-10-07 | **Spec**: [spec.md](../spec.md) |
**Data model**: [data-model.md](../data-model.md)

L'outil expose une seule interface : la commande console `vector`
(entry point déclaré dans `pyproject.toml`, également invocable via
`python -m question2vector`).

## Usage

```text
vector [ENTRÉE...] [OPTIONS]
```

`ENTRÉE` : un ou plusieurs arguments (1 minimum). Chaque argument est
résolu selon la règle de détection du data model (`InputItem`) :

- fichier `.txt`/`.md` existant → contenu du fichier
- dossier existant → un élément par fichier `.txt`/`.md` du premier
  niveau (autres formats ignorés, sous-dossiers non parcourus)
- argument sans syntaxe de chemin → chaîne littérale à vectoriser
- argument avec syntaxe de chemin inexistant → erreur signalée,
  l'élément est ignoré

Le mono-input et le multi-input sont indétinguables pour l'utilisateur :
le nombre d'éléments traités découle des arguments, sans option dédiée.

## Options

| Option | Valeurs | Bornes | Défaut |
|--------|---------|--------|--------|
| `--choix-techno-embed` | `1024` \| `256` \| `128` | — | `1024` |
| `--taille-batch` | entier | 0-100 (0 = pas de batch) | `25` |
| `--reformule` | `on` \| `no` | — | `no` |
| `--choix-modele-llm` | un des 8 alias (cf. ci-dessous) | — | `small` |

Alias LLM valides : `large4`, `large`, `medium`, `small` (défaut),
`14b`, `8b`, `3b`, `zai` — correspondances complètes dans
[data-model.md](../data-model.md) (`LlmModelRef`).
| `--retry-occurences` | entier | 0-10 | `3` |
| `--retry-time` | entier (s) | 1-10 | `3` |
| `--output-folder` | chemin | — | `output/` |
| `--temperature-llm` | décimal | 0-1 | `0,2` |

Toute valeur hors bornes ou inconnue → refus immédiat, avant tout appel
API, avec un message d'erreur clair indiquant les bornes attendues.

## Comportement

- **Sorties** : un fichier JSON `Vector-1.0` par élément traité avec
  succès, écrit dans le dossier de sortie (créé si absent) ; nommage et
  conflits selon le data model (`OutputFileName`).
- **Reformulation** : si `--reformule on`, les entrées ≤ 500 caractères
  sont reformulées par le LLM choisi ; le vecteur porte sur la
  reformulation. Les entrées ambiguës (ou réponses malformées après
  retries) échouent sans sortie.
- **Batchs** : les embeddings sont regroupés par groupes de
  `--taille-batch` ; la reformulation reste élément par élément.
- **Retry** : chaque requête API (embedding, batch, LLM) est retentée
  avec délai exponentiel : `--retry-time`, doublé à chaque essai, jusqu'à
  `--retry-occurences` essais.

## Prérequis d'environnement

- Variable d'environnement `MISTRAL_API_KEY` (chargée depuis un `.env`
  local git-ignoré). Absente ou vide → échec immédiat avant tout appel
  réseau ; la clé n'apparaît jamais dans la console, les logs ni les
  fichiers écrits.

## Codes de sortie

- `0` : tous les éléments traités avec succès
- `1` : erreur de configuration (option hors bornes, clé absente,
  aucune entrée fournie ou exploitable)
- `2` : au moins un élément en échec après traitement (échecs listés
  dans le résumé final)

## Sortie console

- En fin d'exécution : résumé — éléments traités, éléments en échec
  avec motif, fichiers écrits (chemins).
- Aucun contenu d'entrée, aucun vecteur ni clé API n'est affiché.
