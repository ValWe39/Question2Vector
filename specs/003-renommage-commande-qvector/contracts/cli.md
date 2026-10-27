# Contrat d'interface CLI : commande `qvector`

**Date**: 2026-10-27 | **Spec**: [spec.md](../spec.md) |
**Data model**: [data-model.md](../data-model.md)

Contrat de la feature 003 : la commande console `vector` est renommée
en `qvector`. Ce contrat est un delta sur les contrats existants —
tout ce qui n'est pas cité ici reprend
[specs/001-text-vectorization/contracts/cli.md](../../../001-text-vectorization/contracts/cli.md)
et
[specs/002-sortie-tableau-json/contracts/cli.md](../../../002-sortie-tableau-json/contracts/cli.md)
à l'identique.

## Usage

```text
qvector [ENTRÉE...] [OPTIONS]
```

- Invocation principale : `qvector` (entry point du paquet).
- Invocation secondaire inchangée : `python -m question2vector`.
- L'aide (`qvector --help`) et les messages d'usage affichent
  `qvector` comme nom de programme.

## Ce qui change

| Élément | Avant | Après |
| -------- | ----- | ----- |
| Nom de commande | `vector` | `qvector` |
| Aide et messages d'usage | `vector` | `qvector` |

## Ce qui ne change pas

- Arguments, options, bornes et valeurs par défaut (contrat 001).
- Résolution des entrées (fichiers, dossiers, chaînes).
- Sortie groupée `Vector-2.0` dans le dossier de sortie (contrat 002).
- Prérequis d'environnement (`MISTRAL_API_KEY` via `.env` local).
- Codes de sortie : `0` succès, `1` erreur de configuration, `2`
  éléments en échec.
- Comportement de reformulation, batch, retry (contrat 001).

## Compatibilité

- Aucun alias : après mise à jour de l'environnement, `vector` ne
  lance plus cet outil (suppression de la collision avec l'autre
  outil de l'utilisateur — motivation de la feature).
- Les scripts et habitudes invoquant `vector` doivent être adaptés ;
  la note de migration du README le documente.
