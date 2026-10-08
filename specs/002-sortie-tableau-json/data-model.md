# Data Model: feature 002-sortie-tableau-json

**Date**: 2026-10-08

**Spec**: [spec.md](spec.md)

**Plan**: [plan.md](plan.md)

## Entites

### EnregistrementReussite (schema `Vector-2.0`)

Une entree traitee avec succes (FR-002, FR-007).

- **Champs** :
  - `schema_version` : chaine, toujours `"Vector-2.0"` (FR-008)
  - `entree` : texte original complet (chaine ou contenu de
    fichier)
  - `reformulation` : chaine (vide si option desactivee ou entree
    non eligible)
  - `vecteur` : liste de floats de longueur exactement
    `dimension_vecteur`
  - `dimension_vecteur` : 1024 | 256 | 128
  - `nature_vecteur` : `"float32"`
- **Invariant** : `len(vecteur) == dimension_vecteur` ; si l'API
  renvoie une autre dimension que le referentiel du modele,
  l'element devient un EnregistrementEchec.
- **Origine** : herite de l'actuel `OutputRecord` ; seul
  `schema_version` change.

### EnregistrementEchec

Une entree en echec, quelle que soit l'etape (detection,
reformulation, embedding, ecriture) (FR-007).

- **Champs exacts (3)** :
  - `schema_version` : chaine, toujours `"Vector-2.0"` (FR-008)
  - `entree` : argument brut fourni pour une entree jamais lue
    (ex. chemin inexistant) ; texte original pour une entree lue
    puis echouee
  - `motif_echec` : chaine non vide ; valeur standardisee
    « chemin introuvable » pour un echec de detection
- **Invariant** : exactement 3 champs ; jamais de champ `vecteur`,
  `reformulation`, `dimension_vecteur` ni `nature_vecteur`
  (clarification session 2026-10-08).

### LivrableUnique (mode regroupe, defaut)

Le fichier JSON produit par defaut pour un run (FR-003, FR-006).

- **Contenu** : liste ordonnee d'EnregistrementReussite et
  d'EnregistrementEchec, dans l'ordre des entrees fournies
  (FR-005) — un enregistrement par entree du run (FR-007).
- **Nom** : `sortie.json` dans le dossier de sortie ; suffixe `-X`
  (X demarrant a 1) si le nom est deja pris sur le disque ou dans
  la meme execution (regle `resoudre_nom` de la spec 001).
- **Ecriture** : une seule operation en fin de run, dossier cree si
  absent ; jamais d'ecrasement (FR-010).
- **Cas limite** : toutes les entrees en echec → livrable ecrit,
  compose uniquement d'EnregistrementEchec ; aucune entree
  exploitable → aucun livrable, erreur de configuration.

### SortiesDegroupees (mode `--ungroup on`)

Une sortie par entree (FR-004).

- **Contenu** : un fichier par entree du run, chacun un tableau a
  exactement un enregistrement (reussite ou echec).
- **Nom** : regle actuelle inchangee — `deriver_titre(titre_source)`
  puis `resoudre_nom` avec suffixe de conflit (spec 001, FR-007 et
  FR-008).
- **Echec de detection** : le fichier d'un echec de detection est
  nomme depuis l'argument brut (repli `sans_titre` si aucun
  caractere exploitable).

### ModeLivraison (option CLI normalisee)

Extension de `VectorizationOptions` (spec 001).

| Champ | Type | Bornes | Defaut |
| ------- | ----- | -------- | -------- |
| `ungroup` | `on` \| `no` | — | `no` |

Valeur hors bornes → refus immediat avec message clair, code de
sortie d'erreur de configuration (FR-011 de la spec 001, reprise).

### RapportElement (bilan d'execution, evolue)

- **Champs** : `titre`, `ok`, `fichier` (unique ou par entree),
  `motif` le cas echeant — jamais de vecteur ni de cle d'API
  (FR-009).
- **Usage** : resume console en fin d'execution ; les echecs sont
  listes avec leur motif ; codes de sortie inchanges (0 / 1 / 2).

## Relations

```text
VectorizationOptions ──ajout ungroup──> ModeLivraison
Entree ──reussite──> EnregistrementReussite
Entree/argument ──echec──> EnregistrementEchec
N enregistrements ──ordre des entrees──> LivrableUnique (defaut)
N enregistrements ──un par fichier──> SortiesDegroupees (--ungroup on)
Enregistrement* ──serialise──> tableau JSON `Vector-2.0`
```

## Regles de validation (tests)

- Le document produit est toujours une liste JSON, jamais un objet
  isole (FR-001).
- Un enregistrement de reussite expose exactement 6 champs ; un
  enregistrement d'echec exactement 3 (FR-002, FR-007).
- `motif_echec` est non vide ; « chemin introuvable » pour un
  echec de detection.
- L'ordre du livrable regroupe reflete l'ordre des arguments
  d'appel (FR-005).
- Aucun fichier existant n'est ecrase (FR-010).
