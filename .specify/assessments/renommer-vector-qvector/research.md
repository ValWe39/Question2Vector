# Idea Research: Renommer la commande « vector » en « qvector »

- **Slug**: renommer-vector-qvector
- **Created**: 2026-10-27
- **Evidence confidence (overall)**: medium
  (preuves internes solides ; signal utilisateur et motivation non documentés)

## Users & Demand

- La demande émane de l'utilisateur unique et mainteneur de l'outil (idée
  capturée en intake, session du 2026-10-27). Aucun autre utilisateur connu.
  — [source: .specify/assessments/renommer-vector-qvector/intake.md]
  (confidence: high)
- Aucune donnée d'usage (tickets, télémétrie, issues) n'existe dans le dépôt
  pour mesurer la demande. — [source: inspection du dépôt, absence
  d'issues ni de mesure d'usage] (confidence: high)
- La motivation précise (collision avec un autre binaire `vector`, cohérence
  avec le nom du projet `question2vector`) n'est pas documentée.
  — ASSUMPTION (confidence: low)

## Prior Art

- Le nom `vector` est déjà répandu hors projet : `vector` est la CLI de
  l'outil d'observabilité Vector.dev, ce qui rend une collision de nom
  plausible sur PATH. — ASSUMPTION (connaissance générale, aucune recherche
  web menée à la demande de l'utilisateur) (confidence: medium)
- Précédent interne : l'assessment `regroupement-sorties` a déjà abouti à la
  feature 002 (sortie tableau JSON) via le même pipeline — le processus
  d'assessment est éprouvé, mais aucun précédent de renommage d'interface
  n'existe dans le dépôt. — [source: .specify/assessments/regroupement-sorties/
  decision.md, historique git] (confidence: high)
- Aucune tentative antérieure de renommage de la commande dans l'historique
  du dépôt. — [source: `git log` branches 001-005] (confidence: high)

## Market & Context

- Alternative actuelle des utilisateurs : appeler `vector` avec le PATH du
  venv (`.venv\Scripts\vector`) ou `python -m question2vector`, qui reste
  disponible et indépendant du nom de l'entry point.
  — [source: README.md:27, `src/question2vector/__main__.py:1-3`]
  (confidence: high)
- Coût de l'inaction : quasi nul tant que l'outil reste privé et mono-
  utilisateur ; le renommage est un confort, pas une correction.
  — ASSUMPTION (confidence: medium)

## Data & Constraints

- Le nom de commande est défini à exactement 2 endroits du code exécutable :
  l'entry point `vector = "question2vector.cli:main"`
  (pyproject.toml:19) et `prog="vector"` (src/question2vector/cli.py:55) ;
  plus la docstring du module cli.py:1 et celle de config.py:20.
  — [source: inspection du code] (confidence: high)
- Aucun test n'invoque le binaire `vector` : tous les tests importent
  `main` depuis `question2vector.cli`, donc la suite de tests est
  insensible au renommage. — [source: tests/ (grep exhaustif)]
  (confidence: high)
- Le CI (.github/workflows/diagnostic.yml) ne lance jamais la commande
  `vector` (lint et audits uniquement). — [source: inspection du workflow]
  (confidence: high)
- Surface documentaire à mettre à jour : README.md (≥ 8 occurrences,
  notamment `.venv\Scripts\vector` ligne 27), specs/001 (contracts/cli.md,
  plan.md, spec.md, quickstart.md, tasks.md : la CLI y est le contrat
  d'interface officiel), specs/002/contracts/cli.md:15, et
  Prompts/PromptInit1.txt:152 (document historique).
  — [source: grep exhaustif du dépôt] (confidence: high)
- Le renommage de l'entry point nécessite une réinstallation du paquet
  (`pip install -e .`) pour que le script `qvector` apparaisse dans
  `.venv\Scripts` ; l'ancien script `vector` y subsiste sinon.
  — ASSUMPTION (mécanique pip/venv standard, non vérifiée dans ce dépôt)
  (confidence: medium)
- Le nom du schéma de sortie `Vector-2.0` (schema_version JSON) est un nom
  de format, pas de commande : il ne doit pas être confondu avec le
  périmètre du renommage. — [source: README.md, spec 002]
  (confidence: high)
- Aucun indice de publication sur PyPI dans le dépôt (pas de configuration
  de publish) : l'impact d'un changement cassant semble limité à
  l'utilisateur local. — ASSUMPTION (confidence: medium)

## Evidence Against the Idea

- Large surface documentaire : le contrat d'interface CLI
  (specs/001/contracts/cli.md) et tous les scénarios Given/When/Then des
  specs 001 et 002 citent `vector` ; un renommage incomplet laisse des
  docs contradictoires. — [source: grep des specs] (confidence: high)
- Aucune pression externe identifiée (mono-utilisateur, pas publié) : le
  bénéfice dépend entièrement d'une motivation non documentée.
  — ASSUMPTION (confidence: medium)
- Sans alias de transition, tout script, raccourci ou habitude shell
  invoquant `vector` casse silencieusement. — ASSUMPTION
  (confidence: medium)
- Risque de confusion de périmètre : le nom `qvector` est proche du nom de
  schéma `Vector-2.0` ; il faut borner le renommage à la commande seule.

## Gaps & Open Questions

- [NEEDS CLARIFICATION: motivation réelle (collision Vector.dev, cohérence
  de nom, autre ?)]
- [NEEDS CLARIFICATION: alias de compatibilité `vector` conservé ou
  remplacement complet ?]
- [NEEDS CLARIFICATION: faut-il mettre à jour les specs 001/002 (contrats
  historiques) ou seulement la doc courante (README) ?]
- [NEEDS CLARIFICATION: existence de scripts/alias externes à l'utilisateur
  invoquant `vector`]

## Sources

- Inspection du dépôt local (branche 005-changement-nom-commande, commit
  fc2e579) : `pyproject.toml`, `src/question2vector/cli.py`,
  `src/question2vector/__main__.py`, tests/, README.md, specs/001,
  specs/002, `.github/workflows/diagnostic.yml`,
  `.specify/memory/constitution.md`, Prompts/PromptInit1.txt
  (aucune ressource distante consultée, à la demande de l'utilisateur ;
  policy: auto-refused par choix local)
