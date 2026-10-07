"""Options CLI normalisees et chargement de la cle API."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from question2vector.embedding import EMBED_MODELS, LLM_MODELS


class ErreurConfiguration(ValueError):
    """Erreur de configuration : valeur hors bornes ou cle absente."""


@dataclass(frozen=True)
class VectorizationOptions:
    """Options validees de la commande `vector` (contracts/cli.md)."""

    embed_model: str
    batch_size: int
    reformule: bool
    llm_model_alias: str
    retry_occurrences: int
    retry_time: int
    output_folder: Path
    temperature_llm: float


def _entier(nom: str, valeur: str, minimum: int, maximum: int) -> int:
    try:
        nombre = int(str(valeur).strip())
    except ValueError as err:
        raise ErreurConfiguration(f"{nom} : {valeur!r} n'est pas un entier") from err
    if not minimum <= nombre <= maximum:
        raise ErreurConfiguration(
            f"{nom} : {nombre} hors bornes ({minimum} a {maximum})"
        )
    return nombre


def _decimal(nom: str, valeur: str, minimum: float, maximum: float) -> float:
    normalisee = str(valeur).strip().replace(",", ".")
    try:
        nombre = float(normalisee)
    except ValueError as err:
        raise ErreurConfiguration(f"{nom} : {valeur!r} n'est pas un nombre") from err
    if not minimum <= nombre <= maximum:
        raise ErreurConfiguration(
            f"{nom} : {nombre} hors bornes ({minimum} a {maximum})"
        )
    return nombre


def construire_options(
    embed_model: str,
    taille_batch: str,
    reformule: str,
    llm_model_alias: str,
    retry_occurrences: str,
    retry_time: str,
    output_folder: str,
    temperature_llm: str,
) -> VectorizationOptions:
    """Valide toutes les bornes avant tout appel API (FR-011).

    Les valeurs arrivent brutes (chaines) : toute valeur inconnue ou
    hors bornes leve ErreurConfiguration avec un message clair.
    """
    if embed_model not in EMBED_MODELS:
        admis = ", ".join(EMBED_MODELS)
        raise ErreurConfiguration(
            f"--choix-techno-embed : {embed_model!r} inconnu "
            f"(valeurs admises : {admis})"
        )
    if reformule not in ("on", "no"):
        raise ErreurConfiguration(
            f"--reformule : {reformule!r} inconnu (valeurs admises : on, no)"
        )
    if llm_model_alias not in LLM_MODELS:
        admis = ", ".join(LLM_MODELS)
        raise ErreurConfiguration(
            f"--choix-modele-llm : {llm_model_alias!r} inconnu "
            f"(valeurs admises : {admis})"
        )
    return VectorizationOptions(
        embed_model=embed_model,
        batch_size=_entier("--taille-batch", taille_batch, 0, 100),
        reformule=(reformule == "on"),
        llm_model_alias=llm_model_alias,
        retry_occurrences=_entier("--retry-occurences", retry_occurrences, 0, 10),
        retry_time=_entier("--retry-time", retry_time, 1, 10),
        output_folder=Path(output_folder),
        temperature_llm=_decimal("--temperature-llm", temperature_llm, 0.0, 1.0),
    )


def charger_cle_api(chemin_env: str | None = None) -> str:
    """Charge MISTRAL_API_KEY depuis l'environnement ou le `.env`.

    Leve ErreurConfiguration si absente ou vide (FR-017). La cle ne
    doit jamais etre affichee ni journalisee (FR-016).
    """
    load_dotenv(chemin_env)
    cle = os.environ.get("MISTRAL_API_KEY", "")
    if not cle:
        raise ErreurConfiguration(
            "MISTRAL_API_KEY absente : renseignez-la dans un fichier "
            ".env a la racine du projet (cf. .env.example)"
        )
    return cle
