# Decision: Renommer la commande « vector » en « qvector »

- **Slug**: renommer-vector-qvector
- **Decided**: 2026-10-27
- **Verdict**: go
- **Artifacts reviewed**: intake.md, research.md, problem.md, concept.md

## Scorecard

| Critère | Note | Justification |
|---------|------|---------------|
| Problem validity | strong | Collision réelle, erreurs vécues |
| Evidence strength | adequate | Code inspecté, motivation sûre |
| Value vs. inaction | strong | L'inaction ne corrige rien |
| Feasibility / appetite | strong | Appétit small, option A crédible |
| Strategic fit | strong | CLI unique, YAGNI respecté |
| Risk posture | adequate | Risques connus, 1 inconnu reporté |

Détail des justifications :

- **Problem validity** — collision réelle avec un autre outil de
  l'utilisateur, erreurs déjà observées (problem.md, motivation
  utilisateur explicite).
- **Evidence strength** — faits codebase vérifiés (2 points de code,
  tests/CI insensibles) ; motivation confirmée par l'utilisateur ;
  hypothèses restantes bornées (scripts externes).
- **Value vs. inaction** — les erreurs se reproduisent à chaque usage
  rapproché des deux outils ; l'inaction n'a aucun effet correctif
  (problem.md).
- **Feasibility / appetite** — option A crédible en appétit small :
  2 points exécutables + documentation + réinstallation (research.md,
  concept.md).
- **Strategic fit** — la constitution privilégie un point d'entrée CLI
  unique et la simplicité ; le renommage sans alias respecte YAGNI
  (`.specify/memory/constitution.md`).
- **Risk posture** — risques identifiés (script venv résiduel, churn
  doc, rupture des usages existants) avec mitigations connues ; un
  inconnu (scripts externes) est reporté comme question ouverte.

## Verdict & Rationale

Go. Le problème est réel et déjà générateur d'erreurs (validité forte),
l'évidence est adéquate — le codebase a été inspecté exhaustivement et la
motivation a été confirmée par l'utilisateur — et l'option A (remplacement
complet, sans alias) élimine la collision pour un appétit small. Les
options B (alias de transition) et C (contournement documentaire) ont été
écartées : B perpétuerait la collision qui est précisément le problème,
C l'ignore. Le seul inconnu matériel (existence de scripts externes
invoquant `vector`) n'invalide pas le renommage ; il est reporté à la
spécification pour être confirmé par l'utilisateur.

## If go — Handoff to `/speckit-specify`

- **Problem**: la commande `vector` de cet outil entre en collision avec
  celle d'un autre outil de l'utilisateur, provoquant des erreurs de
  résolution de commande déjà observées.
- **Chosen approach**: Option A — remplacement complet du nom de commande
  par `qvector`, sans alias de compatibilité (entry point, `prog`,
  docstrings, README, contrats CLI et exemples d'usage).
- **In scope / out of scope**: en périmètre — entry point pyproject.toml,
  `prog` et docstrings dans cli.py/config.py, README, quickstart et
  contrats d'interface des specs, réinstallation du venv, vérification de
  la disparition de la collision. Hors périmètre — renommage du paquet
  `question2vector`, du schéma `Vector-2.0`, tout alias `vector`,
  modification de l'autre outil, réécriture exhaustive des specs 001/002.
- **Success metrics**: `qvector` fonctionne après réinstallation et
  `vector` ne résout plus vers cet outil ; suite de tests verte sans
  modification comportementale ; zéro occurrence résiduelle du nom de
  commande `vector` dans la documentation courante.
- **Carried-forward open questions**:
  - [NEEDS CLARIFICATION: aucun script ou raccourci externe n'invoque
    `vector` (à confirmer par l'utilisateur)]
  - [NEEDS CLARIFICATION: l'ancien script `.venv\Scripts\vector` sera
    supprimé/nettoyé lors de la réinstallation]
  - [NEEDS CLARIFICATION: périmètre exact des mises à jour dans les specs
    historiques (contrats vs. scénarios Given/When/Then)]
