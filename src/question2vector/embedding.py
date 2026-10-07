"""Referentiels de modeles, decoupage en lots et retry exponentiel."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class EmbeddingModelRef:
    """Reference d'un modele d'embedding.

    Le nom_api sert dans la requete, la dimension et la nature
    alimentent le JSON de sortie (FR-009).
    """

    nom_api: str
    dimension: int
    nature: str


EMBED_MODELS: dict[str, EmbeddingModelRef] = {
    "1024": EmbeddingModelRef("mistral-embed", 1024, "float32"),
    "256": EmbeddingModelRef("mistral-embed-dim256-2510", 256, "float32"),
    "128": EmbeddingModelRef("mistral-embed-dim128-2510", 128, "float32"),
}

LLM_MODELS: dict[str, str] = {
    "large4": "mistral-large-4",
    "large": "mistral-large-latest",
    "medium": "mistral-medium-latest",
    "small": "mistral-small-latest",
    "14b": "ministral-14b-latest",
    "8b": "ministral-8b-latest",
    "3b": "ministral-3b-latest",
    "zai": "zai-glm-5-3",
}


def decouper_en_lots(textes: list[str], taille: int) -> list[list[str]]:
    """Decoupe en lots d'au plus `taille` elements (FR-004).

    Taille 0 : pas de regroupement, un lot d'un element par texte.
    """
    if taille <= 0:
        return [[texte] for texte in textes]
    return [textes[i : i + taille] for i in range(0, len(textes), taille)]


def avec_retry(
    appel: Callable[[], T],
    occurrences: int,
    delai_initial: int,
    veilleuse: Callable[[int], None] = time.sleep,
) -> T:
    """Execute `appel` avec reprise a delai exponentiel (FR-015).

    `occurrences` reprises apres l'essai initial ; le delai double a
    chaque reprise : delai_initial, puis 2x, puis 4x (3 s, 6 s, 12 s
    par defaut). La derniere exception est relancee apres epuisement.
    """
    for essai in range(occurrences + 1):
        try:
            return appel()
        except Exception:
            if essai == occurrences:
                raise
            veilleuse(delai_initial * (2**essai))
    raise RuntimeError("boucle de reprise inatteignable")
