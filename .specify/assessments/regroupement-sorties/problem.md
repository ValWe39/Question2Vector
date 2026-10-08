# Problem Definition: Resultats multi-entrees difficiles a consommer en bloc

- **Slug**: regroupement-sorties
- **Created**: 2026-10-08
- **Inputs used**: intake.md | research.md

## Problem Statement

L'utilisateur de Question2Vector qui traite plusieurs entrees en une
seule execution recoit autant de fichiers JSON separes que d'entrees,
sans moyen d'obtenir directement un jeu de donnees unique : pour
consommer l'ensemble des resultats en aval, il doit identifier,
ouvrir et fusionner lui-meme chaque fichier, et le format actuel
(objet unique par fichier) ne se prete pas a contenir plusieurs
question-vecteurs.

## Affected Users & Stakeholders

- **Users** : l'utilisateur CLI du projet (auteur de l'idee) —
  l'usage multi-entrees est reel et observe (`output/` contient des
  lots `Corsen.json`+`Corsen-1.json`, `Tocquev.json`+`Tocquev-1.json`
  +`Tocquev-2.json` issus d'executions multi-fichiers) ; chaque run
  multi-entree le contraint a un assemblage manuel. — [source:
  research.md]
- **Users (potentiels, non confirmes)** : tout consommateur aval des
  fichiers de sortie (script, base vectorielle, LLM) qui devrait
  aujourd'hui ecrire sa propre logique de collecte multi-fichiers. —
  [NEEDS CLARIFICATION: aucun consommateur externe identifie]
- **Stakeholders** : le mainteneur du projet — arbitre la rupture de
  contrat du format `Vector-1.0` (tests, README, contrats CLI) et
  veille au principe IV de la constitution (Simplicite/YAGNI) pour
  toute option supplementaire. — [source: research.md]

## Goals

- Un run multi-entrees produit un jeu de resultats consommable en une
  seule operation, sans assemblage manuel par l'utilisateur.
- Le format de sortie est identique qu'il y ait une ou plusieurs
  question-vecteurs (transparence du nombre d'entrees pour le
  consommateur).
- L'utilisateur garde la maitrise du mode de livraison des resultats :
  il peut choisir entre un livrable unique et une sortie par entree.
- La tracabilite entre une entree et son enregistrement reste
  possible, quel que soit le mode de livraison (aujourd'hui assuree
  par le nommage des fichiers).

## Non-Goals

- Modifier le pipeline de vectorisation lui-meme (detection des
  entrees, reformulation, embeddings, retries) — seules la forme et
  la livraison de la sortie sont en cause.
- Ajouter de nouveaux types d'entrees ou de nouvelles cibles de
  sortie (base vectorielle, format binaire, compression).
- Mettre en place un service distant, une sync ou un stockage non
  local (principes II et III de la constitution).
- Resoudre les questions de performance a tres grande echelle
  (streaming, memoire) tant qu'aucun volume cible n'est etabli.

## Success Metrics

- Un run multi-entrees produit un jeu de donnees chargeable en une
  seule lecture par le consommateur, sans etape de fusion manuelle.
  (baseline: aujourd'hui N fichiers a ouvrir et a concatener pour N
  entrees)
- Nombre d'etapes manuelles entre la fin du run et l'utilisation des
  resultats en aval : 0 (baseline: >= 1 etape de fusion des que
  N > 1 — qualitatif, aucun consommateur mesure aujourd'hui).
- Format de sortie stable : une seule forme de document quel que
  soit le nombre d'entrees (baseline: objet unique par fichier,
  forme dependent du nombre d'entrees par la dispersion en fichiers).
- Les tests et contrats documentes restent coherents avec le format
  reel produit (baseline: 100 % des tests actuels assertent le
  format objet).

## Cost of Inaction

Chaque execution multi-entrees laisse a l'utilisateur une collection
de fichiers a reunifier manuellement, avec des scripts jetables non
partages ; le format objet `Vector-1.0` ne peut pas evoluer vers des
jeux multi-vecteurs sans rupture, donc le meme arbitrage se
reposerait plus tard, apres l'accumulation de sorties existantes
encore plus nombreuses a migrer. La friction reste limitee a
l'echelle d'usage actuelle (petits lots observes), ce qui rend le
cout supportable mais recurrent.

## Open Questions

- [NEEDS CLARIFICATION: quel consommateur aval charge les resultats
  et sous quelle forme (tableau JSON, JSONL, autre) ?]
- [NEEDS CLARIFICATION: nom et emplacement du livrable unique en mode
  groupe, et comportement si un fichier du meme nom existe deja]
- [NEEDS CLARIFICATION: comportement du livrable groupe en cas
  d'echec partiel (reussites seules ? code de sortie ?) et en cas
  d'entree unique (1 element ?)]
- [NEEDS CLARIFICATION: la version de schema (`Vector-1.0`) change-t-elle,
  et quelle transition pour les sorties et tests existants ?]
- [NEEDS CLARIFICATION: comment conserver la tracabilite
  entree → enregistrement dans le livrable unique (ordre ? champ
  identifiant ?)]
- [NEEDS CLARIFICATION: syntaxe du choix utilisateur
  (drapeau sans valeur vs option `on`/`no` coherente avec le contrat
  CLI existant)]
- [NEEDS CLARIFICATION: volumes cibles (nombre d'entrees par run)
  pour arbitrer tableau JSON vs JSONL]
