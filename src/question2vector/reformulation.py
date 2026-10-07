"""Reformulation LLM optionnelle (FR-012 a FR-014)."""

from __future__ import annotations

import json

from question2vector.config import VectorizationOptions
from question2vector.embedding import LLM_MODELS, avec_retry

SEUIL_ELIGIBILITE = 500

PROMPT_REFORMULATION = """Tu es un reformulateur de questions. Ta seule tache est de reformuler
la question de l'utilisateur pour qu'elle soit plus claire et precise.

## Processus
1. Identifie le sujet, le verbe d'action, le contexte manquant et le
   format de reponse attendu.
2. Repere les pronoms vagues, termes polysemiques et hypotheses
   implicites.
3. Appuie-toi sur le contexte disponible de la conversation pour ne
   pas reformuler ce qui est deja evident.

## Regles
- Ne reponds JAMAIS a la question. Ta sortie est la reformulation,
  rien d'autre.
- Reste fidele a l'intention : n'ajoute aucune contrainte non exprimee.
- Reformule en 1 a 3 phrases maximum.

## Format de sortie
Reponds TOUJOURS avec un objet JSON valide, sans texte autour,
sans balise markdown, en respectant exactement ce schema :

- Cas nominal (question reformulable) :
  {"ambiguous": false, "reformulation": "<question reformulee>"}

- Cas ambigu (ambiguite bloquante qui empeche toute reformulation
  fiable) :
  {"ambiguous": true, "reformulation": null,
   "options": ["<interpretation 1>", "<interpretation 2>",
               "<interpretation 3>"]}

Le JSON doit etre la seule et unique sortie, directement parsable.

## Exemples
Entree : "Ca marche comment ?"
Sortie :
{"ambiguous": false, "reformulation": "Comment fonctionne le deploiement du connecteur mentionne plus haut ?"}

Entree : "Comment l'importer ?"
Sortie :
{"ambiguous": true, "reformulation": null, "options": ["Comment importer le fichier CSV dans la base de donnees ?", "Comment importer le fichier CSV dans Excel ?", "Comment importer le module Python dans mon script ?"]}

## question utilisateur :

"""


class ErreurReformulation(RuntimeError):
    """Reformulation impossible : ambiguite bloquante ou reponse
    malformee."""


def est_eligible(texte: str) -> bool:
    """Une reformulation ne s'applique qu'aux questions courtes."""
    return len(texte.strip()) <= SEUIL_ELIGIBILITE


def reformuler(client, texte: str, options: VectorizationOptions) -> str:
    """Reformule `texte` via le LLM choisi ; retourne la reformulation.

    Leve ErreurReformulation si la question est ambiguement bloquante
    ou si la reponse reste malformee apres les reprises (FR-014).
    """
    nom_modele = LLM_MODELS[options.llm_model_alias]
    prompt = PROMPT_REFORMULATION + texte

    def appel() -> str:
        return client.discuter(nom_modele, prompt, options.temperature_llm)

    reponse = avec_retry(appel, options.retry_occurrences, options.retry_time)
    try:
        charge = json.loads(reponse)
    except (json.JSONDecodeError, TypeError) as err:
        raise ErreurReformulation("reponse LLM malformee (JSON invalide)") from err
    if not isinstance(charge, dict) or not isinstance(charge.get("ambiguous"), bool):
        raise ErreurReformulation("reponse LLM malformee (schema inattendu)")
    if charge["ambiguous"]:
        raise ErreurReformulation(
            "question ambigue : reformulation bloquante, aucune interpretation fiable"
        )
    reformulation = charge.get("reformulation")
    if not isinstance(reformulation, str) or not reformulation.strip():
        raise ErreurReformulation("reponse LLM malformee (reformulation absente)")
    return reformulation.strip()
