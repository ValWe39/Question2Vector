# Quickstart: Sortie tableau JSON regroupee

**Date**: 2026-10-08 | **Spec**: [spec.md](spec.md) |
**Contrat CLI**: [contracts/cli.md](contracts/cli.md) |
**Data model**: [data-model.md](data-model.md)

Guide de validation pas a pas de la feature. Prerequis :
installation faite (README), `MISTRAL_API_KEY` renseignee dans
`.env`, venv non active → appeler directement
`.venv\Scripts\vector` (Windows). Chaque scenario part d'un dossier
de sortie vide via `--output-folder`.

## Scenario 1 : entree unique → tableau a un element

```text
.venv\Scripts\vector "Comment fonctionne le depot git ?" --output-folder output-test
```

Attendu : code de sortie 0 ; un seul fichier
`output-test\sortie.json` chargeable en une lecture, contenant un
tableau d'exactement un enregistrement a 6 champs dont
`schema_version` = `Vector-2.0`.

## Scenario 2 : plusieurs entrees → livrable regroupe

```text
.venv\Scripts\vector "Question A" "Question B" ^
  Examples/Corsen.txt --output-folder output-test
```

Attendu : code 0 ; `output-test\sortie.json` contient un tableau de
3 enregistrements, dans l'ordre des arguments ; chaque
enregistrement porte son vecteur de la dimension du modele
(1024 par defaut).

## Scenario 3 : sortie par entree (`--ungroup on`)

```text
.venv\Scripts\vector "Question A" "Question B" --ungroup on --output-folder output-test
```

Attendu : code 0 ; 2 fichiers dans `output-test`, nommes selon le
contrat 001 (ex. `Questio.json`, `Questio-1.json`), chacun un
tableau a exactement un enregistrement. Sans `--ungroup` (ou avec
`--ungroup no`), le meme appel produirait un unique
`sortie.json`.

## Scenario 4 : echec partiel → livrable exhaustif

```text
.venv\Scripts\vector "Question A" "Question B" ^
  chemin/inexistant.txt --output-folder output-test
```

Attendu : code 2 ; `output-test\sortie.json` contient 3
enregistrements : 2 reussites avec vecteur, 1 echec a 3 champs dont
`entree` = `chemin/inexistant.txt` et `motif_echec` =
« chemin introuvable » ; le bilan console liste l'echec.

## Scenario 5 : aucune entree exploitable

```text
.venv\Scripts\vector chemin/inexistant.txt --output-folder output-test
```

Attendu : code 1, message d'erreur clair, aucun fichier ecrit.

## Scenario 6 : reexecution → aucun ecrasement

Relancer le scenario 1 dans le meme dossier de sortie.

Attendu : un nouveau fichier `sortie-1.json` apparait ;
`sortie.json` est inchange.

## Tests automatises

```text
.venv\Scripts\python -m pytest
```

Attendu : tous les tests passent, aucun acces reseau (client
Mistral fictif). Les tests couvrent : le format tableau (entree
unique et multiple), le schema des enregistrements (6 et 3
champs), l'ordre, le nommage `sortie.json` et son suffixe, le mode
`--ungroup`, l'echec partiel et l'absence d'ecrasement.
