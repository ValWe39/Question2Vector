# Idea Intake: Sortie JSON regroupee (tableau) et option --ungroup

- **Slug**: regroupement-sorties
- **Created**: 2026-10-08
- **Source**: pasted text (commande `/speckit-assess-intake`), idee
  portant sur le code existant du projet (sortie actuelle : un JSON
  `Vector-1.0` par entree dans `output/`, cf.
  `src/question2vector/output.py`)
- **Type**: improvement

## Idea (as captured)

> J'envisage de modifier l'outil actuel avec les caracteristiques
> suivantes :
>
> **1. sortie :**
>
> **objectif general de la modification**
>
> J'envisage de remplacer l'actuel json par un json sous forme de
> tableau, afin :
>
> - d'avoir la possibilite d'avoir plusieurs question-vecteur dans
>   une meme sortie,
> - et que cela reste transparent en matiere de format (un meme
>   format qu'il y ait une question-vecteur ou plusieurs)
>
> **exemple de sortie**
>
> un json de se format pour plusieurs vecteurs :
>
> ```json
> [
>   {
>     "schema_version",
>     "entree",
>     "reformulation",
>     "vecteur": [float, float, etc.],
>     "dimension_vecteur",
>     "nature_vecteur"
>   },
>   {
>     "schema_version",
>     "entree",
>     "reformulation",
>     "vecteur": [float, float, etc.],
>     "dimension_vecteur",
>     "nature_vecteur"
>   },
>   etc.
> ]
> ```
>
> **2. Commande optionnelle**
>
> Je souhaite offrir la possibilite a l'utilisateur de choisir de
> regrouper toutes ses sorties (s'il a plusieurs entrees) dans un
> meme json (cf. ci-dessus). Ce point est parametre par defaut et la
> commande optionnelle `--ungroup` permet de revenir a la situation
> initiale a N output pour N entrees (cette fois au format de #1).

## Restated

L'idee propose de faire sortir l'outil en un JSON de type tableau
(array de records question-vecteur) quel que soit le nombre d'entrees,
avec par defaut toutes les sorties regroupees dans un seul fichier
JSON ; une option `--ungroup` restaurerait un fichier de sortie par
entree, chacun au nouveau format tableau.

## Origin & Context

- **Raised by**: l'utilisateur du projet (via la commande d'intake)
- **Trigger**: [NEEDS CLARIFICATION: evenement declencheur —
  constat d'usage, besoin d'integration aval, autre ?]

## First-Glance Unknowns

- [NEEDS CLARIFICATION: en mode groupe, nom et emplacement du
  fichier unique (un seul fichier dans `output/` ? nom derive de
  quoi ?) et interaction avec `deriver_titre` / `resoudre_nom`
  actuels]
- [NEEDS CLARIFICATION: en mode `--ungroup`, chaque fichier
  contient-il un tableau a un seul element ?]
- [NEEDS CLARIFICATION: la valeur de `schema_version` change-t-elle
  (ex. `Vector-1.0` -> `Vector-2.0`) pour marquer le changement de
  format ?]
- [NEEDS CLARIFICATION: retrocompatibilite — des consommateurs
  existants du format objet `Vector-1.0` doivent-ils etre
  preserves ?]
- [NEEDS CLARIFICATION: le regroupement par defaut s'applique-t-il
  aussi a une seule entree (tableau a 1 element) et aux entrees de
  type dossier ?]
- [NEEDS CLARIFICATION: bornes/contraintes de `--ungroup`
  (drapeau sans valeur ?) et impact sur les tests et contrats CLI
  existants]
