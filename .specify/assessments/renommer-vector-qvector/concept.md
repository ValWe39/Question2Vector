# Concept: Renommage complet de la commande « vector » en « qvector »

- **Slug**: renommer-vector-qvector
- **Created**: 2026-10-27
- **Recommended option**: A — Remplacement complet sans alias

## Options

### Option A — Remplacement complet, sans alias

- **Sketch**: la commande s'appelle désormais `qvector` partout : entry
  point du paquet, affichage d'aide, README, quickstart et contrats CLI.
  Aucun alias `vector` n'est conservé. L'utilisateur réinstalle le paquet
  dans son venv et n'utilise plus que `qvector`.
- **Appetite**: small (quelques heures : 2 points de code exécutable, de
  la documentation, une réinstallation, une vérification).
- **Trade-offs**: gagne — la collision disparaît définitivement, ce qui est
  le but premier ; un seul nom à retenir. Sacrifie — la compatibilité
  ascendante : toute habitude ou script invoquant `vector` casse (mais
  l'utilisateur est unique et le signale possible). Risque — l'ancien
  script `.venv\Scripts\vector` subsiste tant que le venv n'est pas
  réinstallé/nettoyé, laissant croire que le renommage n'a pas pris.
- **Rabbit holes**: la mise à jour exhaustive des specs historiques
  (Given/When/Then, tasks.md de 001 et 002) peut gonfler ; il faut borner
  au contrat d'interface et à la documentation courante.

### Option B — Remplacement avec alias de transition `vector`

- **Sketch**: `qvector` devient la commande principale et un alias
  `vector` est conservé temporairement (deux entry points), avec message
  de dépréciation, puis retiré plus tard.
- **Appetite**: small-medium (code identique à A, plus la gestion d'alias
  et une étape de retrait ultérieure).
- **Trade-offs**: gagne — transition douce pour d'éventuels usages
  existants. Sacrifie — la collision persiste pendant toute la période
  de transition, ce qui contredit directement le problème (l'autre
  outil expose aussi `vector`) ; deux scripts dans le venv entretiennent
  la confusion.
- **Rabbit holes**: calendrier de retrait de l'alias, version de
  dépréciation, double maintenance des docs.

### Option C — Ne pas renommer, documenter le contournement

- **Sketch**: le code ne change pas ; l'utilisateur appelle
  `python -m question2vector` ou se crée un alias shell personnel
  (`qv`), et le README mentionne la coexistence possible avec d'autres
  outils nommés `vector`.
- **Appetite**: small (une note de doc, rien d'autre).
- **Trade-offs**: gagne — zéro changement de code, zéro risque de
  régression. Sacrifice — les erreurs liées à la résolution du PATH
  persistent pour tout appel `vector` (elles sont déjà survenues) ; le
  README reste épineux ; le confort demandé n'est pas livré.
- **Rabbit holes**: aucun, c'est l'option minimale.

## Recommendation

Option A. Le problème est une collision de nom déjà génératrice d'erreurs ;
seul le remplacement complet l'élimine (l'option B la perpétuerait,
l'option C l'ignore). Le coût est faible : research.md établit que seuls
2 points du code exécutable portent le nom, que les tests importent `main`
sans invoquer le binaire, et que le CI n'appelle jamais la commande. Les
métriques de succès de problem.md (commande sans ambiguïté, suite de tests
verte, plus d'occurrence `vector` dans la doc courante) sont toutes
atteignables par A.

## Out of Scope (for the recommended option)

- Renommer le paquet `question2vector` ou les modules internes (non-goal
  hérité).
- Renommer le schéma de sortie `Vector-2.0` (non-goal hérité).
- Tout alias de compatibilité `vector` (décision de l'option A).
- Modifier l'autre outil en collision.
- Refonte des specs 001/002 au-delà du nom de commande dans le contrat
  d'interface et les exemples d'usage.

## Assumptions to Validate

- Aucun script ou raccourci externe n'invoque `vector` (à confirmer par
  l'utilisateur — open question de problem.md).
- La réinstallation `pip install -e .` suffit à faire apparaître `qvector`
  et l'utilisateur nettoiera l'ancien script `vector` du venv.
- `python -m question2vector` reste l'invocation secondaire documentée et
  n'entre pas en collision avec l'autre outil.
- Les specs historiques n'ont pas besoin d'une réécriture complète, seulement
  d'une mise à jour du nom de commande dans les contrats et exemples.
