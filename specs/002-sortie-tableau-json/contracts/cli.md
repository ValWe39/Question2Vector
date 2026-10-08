# Contrat d'interface CLI : sortie tableau Vector-2.0

**Date**: 2026-10-08 | **Spec**: [spec.md](../spec.md) |
**Data model**: [data-model.md](../data-model.md)

Ce contrat complete celui de la spec 001
(`specs/001-text-vectorization/contracts/cli.md`) pour tout ce qui
touche a la forme et a la livraison de la sortie. Les entrees, la
detection, la reformulation, les lots, les reprises, la cle d'API et
les codes de sortie restent regis par le contrat 001.

## Usage

```text
vector [ENTREE...] [OPTIONS]
```

Inchange : resolution des entrees (chaine, fichier `.txt`/`.md`,
dossier, melange) selon le contrat 001 ; le mono-input et le
multi-input restent indistingues pour l'utilisateur.

## Options nouvelles

| Option | Valeurs | Bornes | Defaut |
| -------- | --------- | -------- | -------- |
| `--ungroup` | `on` \| `no` | — | `no` |

`--ungroup no` (defaut) : toutes les entrees du run aboutissent
dans un seul fichier regroupe. `--ungroup on` : une sortie par
entree. Toute autre valeur → refus immediat avant tout appel API,
message d'erreur clair, code de sortie 1.

Les options du contrat 001 restent valides et inchangees.

## Comportement de sortie

- **Format** : le contenu de chaque fichier produit est un
  tableau JSON d'enregistrements du schema `Vector-2.0`, jamais un
  objet isole — y compris pour une entree unique (tableau a un
  element).
- **Enregistrement de reussite** (6 champs) : `schema_version`,
  `entree`, `reformulation`, `vecteur`, `dimension_vecteur`,
  `nature_vecteur`.
- **Enregistrement d'echec** (3 champs) : `schema_version`,
  `entree`, `motif_echec` — sans `vecteur`. Le champ `entree` d'un
  echec de detection porte l'argument brut fourni ; `motif_echec`
  vaut « chemin introuvable » dans ce cas.
- **Mode regroupe (defaut)** : un seul fichier `sortie.json` dans
  le dossier de sortie, un enregistrement par entree du run, dans
  l'ordre des arguments ; suffixe `-X` si le nom est deja pris ;
  jamais d'ecrasement.
- **Mode degroupe (`--ungroup on`)** : un fichier par entree,
  chacun un tableau a un enregistrement, nommage selon le contrat
  001 (`deriver_titre` + suffixe de conflit).
- **Aucune entree exploitable** : erreur de configuration, code 1,
  aucun fichier — inchange.
- **Echec partiel** : le livrable reste ecrit avec les reussites et
  les echecs ; code de sortie 2, echecs listes au bilan.

## Codes de sortie

Inchanges (contrat 001) : `0` tous les elements reussis, `1`
erreur de configuration, `2` au moins un element en echec.

## Sortie console

- En fin d'execution : bilan — fichier(s) ecrit(s) avec chemin,
  elements en echec avec motif, decomptes.
- Aucun contenu d'entree, aucun vecteur ni cle d'API affiches.
