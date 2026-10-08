# Decision: Livrable de sortie unique pour les runs multi-entrees

- **Slug**: regroupement-sorties
- **Decided**: 2026-10-08
- **Verdict**: go
- **Artifacts reviewed**: intake.md | research.md | problem.md |
  concept.md

## Scorecard

- **Problem validity** : adequate — usage multi-entrees reel et
  observe (`output/` contient des lots multi-fichiers), friction
  d'assemblage manuelle a chaque run ; mais signal limite a un
  seul utilisateur, aucun consommateur externe identifie.
- **Evidence strength** : adequate — faits internes verifies
  (contrat FR-005, tests, code) et conventions externes citees
  (tableau API vs JSONL fichier) ; la demande, elle, repose sur le
  seul temoignage de l'auteur — assume et non dissimule.
- **Value vs. inaction** : strong — l'inaction laisse une friction
  recurrente et un format incapable d'evoluer vers le
  multi-vecteurs ; l'appetite small rend le rapport valeur/cout
  tres favorable, d'autant que la rupture `Vector-1.0` ne coute
  presque rien aujourd'hui.
- **Feasibility / appetite** : strong — option B bornee :
  `output.py`, une option CLI, contrats et tests a reecrire ;
  quelques jours, aucune dependance nouvelle, alignee avec le
  pattern reponse API (liste d'objets).
- **Strategic fit** : adequate — constitution II-III non touchees ;
  le principe IV (YAGNI) s'applique a l'option supplementaire mais
  celle-ci preserve l'usage existant au lieu de le supprimer —
  arbitrage du mainteneur, valide par lui.
- **Risk posture** : adequate — risques majeurs identifies dans
  research.md/concept.md (rupture de format, nommage du livrable
  unique, echec partiel, tracabilite, version de schema, divergence
  JSONL) ; aucun n'est non-mitige au point de bloquer : tous sont
  tranchables en specification, et le volume modere observe
  neutralise le risque memoire du tableau JSON.

## Verdict & Rationale

**Go, sur l'option B** (tableau JSON groupe par defaut, sortie par
entree en option), confirmee par le mainteneur. La problematique est
reelle pour l'usage observe du projet, les quatre buts du probleme
sont tenus par l'option B, et l'appetite small correspond a un
changement borne. Les deux conditions du gate sont reunies : probleme
adequate et evidence adequate — les conventions de format sont
documentees et les faits internes verifies ; seule la demande
externe est assumee comme inexistante, ce qui est coherent avec un
outillage personnel. Les incertitudes restantes sont des decisions de
specification (nommage, echec partiel, tracabilite, version de
schema), pas des lacunes d'evidence.

## If go — Handoff to `/speckit-specify`

- **Problem** : un run multi-entrees produit N fichiers JSON separes
  que l'utilisateur doit fusionner a la main pour consommer ses
  resultats en bloc, et le format objet actuel ne peut pas porter
  plusieurs question-vecteurs.
- **Chosen approach** : Option B — sortie toujours au format tableau
  JSON (`[ {schema_version, entree, reformulation, vecteur,
  dimension_vecteur, nature_vecteur}, ... ]`), regroupement de
  toutes les question-vecteurs du run dans un seul fichier par
  defaut, option CLI pour restaurer une sortie par entree (chacune
  au format tableau).
- **In scope** : forme et livraison de la sortie (`output.py`,
  option CLI, nommage, contrats, tests, README). **Out of scope** :
  pipeline de vectorisation, nouveaux types d'entrees, cibles de
  sortie nouvelles, JSONL, migration des sorties existantes,
  metadonnees de run, cloud/sync, streaming grande echelle.
- **Success metrics** : livrable chargeable en une seule lecture
  sans fusion manuelle ; zero etape manuelle entre le run et l'usage
  aval ; une seule forme de document quel que soit le nombre
  d'entrees ; tests et contrats coherents avec le format produit.
- **Carried-forward open questions** :

  - [NEEDS CLARIFICATION: nom et emplacement du fichier unique
    groupe, et comportement si un fichier du meme nom existe
    deja]
  - [NEEDS CLARIFICATION: comportement en echec partiel (reussites
    seules dans le livrable ? code de sortie ?) et entree unique
    (tableau a 1 element ?)]
  - [NEEDS CLARIFICATION: valeur de `schema_version` (maintien de
    `Vector-1.0` ou passage a `Vector-2.0`) et reecriture des
    tests/contrats impactes]
  - [NEEDS CLARIFICATION: tracabilite entree → enregistrement
    dans le livrable unique (ordre ? champ ?)]
  - [NEEDS CLARIFICATION: syntaxe exacte de l'option (drapeau
    sans valeur vs `on`/`no` coherents avec le contrat CLI
    existant)]
  - [NEEDS CLARIFICATION: consommateur aval reel et volumes
    cibles — a confirmer aupres de l'auteur, sans bloquer la
    specification]
