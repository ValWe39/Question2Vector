# Quickstart: valider la feature 003-renommage-commande-qvector

**Date**: 2026-10-27 | **Spec**: [spec.md](spec.md) |
**Contrat CLI**: [contracts/cli.md](contracts/cli.md)

Guide de validation de bout en bout. Prérequis : venv actif,
`MISTRAL_API_KEY` chargée depuis le `.env` local (cf. contrat 001).

## 1. Réinstallation et remplacement de la commande

```bash
pip install -e .
```

Attendu : le script `qvector` apparaît dans les scripts du venv.
L'ancien script `vector` est retiré par la réinstallation ; sinon, le
supprimer manuellement du dossier des scripts du venv pour éliminer
toute collision résiduelle.

## 2. Aide sous le nouveau nom

```bash
qvector --help
```

Attendu : l'aide s'affiche, l'usage montre `qvector` comme nom de
programme, toutes les options habituelles sont présentes.

## 3. Comportement identique

```bash
qvector Examples/Corsen.txt
qvector --reformule on "Ça marche comment ?"
```

Attendu : mêmes résultats qu'avant le renommage — sortie groupée
`Vector-2.0` dans `output/sortie.json`, résumé console identique,
code de sortie `0`.

## 4. Disparition de la collision

```bash
vector --help
```

Attendu : cet outil ne démarre pas — la commande est soit
introuvable, soit résolue vers l'autre outil de l'utilisateur
(motif de la feature).

## 5. Invocation secondaire préservée

```bash
python -m question2vector --help
```

Attendu : l'outil démarre normalement, identique à avant.

## 6. Suite de tests

```bash
pytest
```

Attendu : suite verte, sans aucune modification comportementale des
tests existants.

## Résumé de validation

La feature est validée si les 6 scénarios ci-dessus produisent tous
les résultats attendus, en particulier : `qvector` fonctionne à
l'identique, `vector` ne lance plus cet outil, et aucun test n'a
dû être adapté.
