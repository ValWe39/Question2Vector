# Research: Sortie tableau JSON regroupee

**Date**: 2026-10-08 | **Spec**: [spec.md](spec.md) | **Plan**:
[plan.md](plan.md)

Contexte amont : l'assessment `regroupement-sorties`
(`.specify/assessments/regroupement-sorties/`) a deja arbitre le
format (option B : tableau JSON groupe), documente les conventions
externes (tableau de reponse API vs JSONL de fichiers) et fixe le
verdict GO. Ce document tranche les decisions restantes au niveau
implementation et consigne les alternatives ecartees.

- **Decision : format du livrable — tableau JSON unique.**
  Rationale : transparence du format quel que soit le nombre
  d'entrees (FR-001), consommable en une lecture (SC-001), volumes
  modestes assumant un chargement en memoire. Alternatives :
  JSONL (un objet par ligne, convention batch industrielle) ecarte
  car il affaiblit la transparence entre modes et n'apporte de
  benefice qu'a grande echelle ; objet par fichier (statu quo)
  ecarte par l'assessment.

- **Decision : option `--ungroup` avec valeurs `on` / `no`, defaut
  `no`.** Rationale : toutes les options du contrat CLI actuel
  prennent une valeur (`--reformule on|no` en tete) ; l'homogeneite
  du contrat et de l'aide prime. Alternatives : drapeau sans valeur
  (premier du contrat, casse l'homogeneite) ; option inverse
  `--group` (inversion du defaut impose par le besoin d'origine).

- **Decision : version de schema `Vector-2.0`, portee par chaque
  enregistrement.** Rationale : la structure racine change (objet
  vers tableau) ; un lecteur doit pouvoir distinguer les deux
  formats. Alternatives : garder `Vector-1.0` (risque de
  confusion, ecarte en clarification Q3 de la specification) ;
  `Vector-1.1` (suggererait une compatibilite inexistante).

- **Decision : deux formes d'enregistrement explicites (reussite a
  6 champs, echec a 3 champs) plutot qu'un schema a champs
  optionnels.** Rationale : FR-007 impose des champsets disjoints ;
  deux structures explicites evitent les valeurs nulles ambigues et
  se valident par invariant simple. Alternatives : un record unique
  avec `vecteur` et `motif_echec` optionnels (champs nuls
  trompeurs, ecarte en clarification Q1).

- **Decision : champ `entree` d'un echec de detection = argument
  brut fourni ; motif standardise « chemin introuvable » pour ce
  cas.** Rationale : l'argument brut est le seul identifiant
  disponible pour une entree jamais lue ; un motif stable rend les
  tests d'acceptation deterministes. Alternatives : chaine vide
  (identification perdue) ; chemin resolu en absolu (diverge de la
  saisie utilisateur).

- **Decision : nommage du livrable — `sortie.json` avec suffixe
  `-X` via la regle de conflit existante (`resoudre_nom`).**
  Rationale : reutilisation de la regle FR-008 de la spec 001, nom
  previsible, aucun ecrasement. Alternatives : horodatage (ecarte
  en clarification Q1 de la specification) ; derivation du titre de
  la premiere entree (trompeur pour un lot heterogene).

- **Decision : nommage en mode degroupe — regle actuelle
  inchangee (`deriver_titre` + `resoudre_nom`).** Rationale : le
  besoin d'origine est de « revenir a la situation initiale a N
  output pour N entrees ». Alternatives : aucun, la continuite
  prime.

- **Pratiques d'implementation reprises du depot** : dataclasses
  figees avec `__post_init__` pour les invariants (modele de
  l'actuel `OutputRecord`) ; serialisation `json.dumps` avec
  `ensure_ascii=False` et `indent=2` ; fabrique de client fictif
  dans `tests/conftest.py` ; aucun nouveau package (constitution
  III).

Aucun NEEDS CLARIFICATION subsiste : les inconnues restantes ont
ete tranchees par les clarifications de la specification (session
2026-10-08) et par les decisions ci-dessus.
