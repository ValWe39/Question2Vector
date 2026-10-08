"""Nommage des sorties et ecriture du tableau JSON Vector-2.0
(FR-001, FR-002, FR-006, FR-007, FR-010)."""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

SCHEMA_VERSION = "Vector-2.0"
TITRE_REPLI = "sans_titre"
TITRE_LIVRABLE = "sortie"


@dataclass(frozen=True)
class OutputRecord:
    """Enregistrement de reussite (data-model.md, schema
    Vector-2.0)."""

    entree: str
    reformulation: str
    vecteur: list[float]
    dimension_vecteur: int
    nature_vecteur: str

    def __post_init__(self) -> None:
        if len(self.vecteur) != self.dimension_vecteur:
            raise ValueError(
                "dimension inattendue : le vecteur contient "
                f"{len(self.vecteur)} valeurs, {self.dimension_vecteur} "
                "attendues"
            )

    def vers_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "entrée": self.entree,
            "reformulation": self.reformulation,
            "vecteur": self.vecteur,
            "dimension_vecteur": self.dimension_vecteur,
            "nature_vecteur": self.nature_vecteur,
        }


@dataclass(frozen=True)
class EnregistrementEchec:
    """Enregistrement d'echec : exactement trois champs, jamais de
    vecteur (FR-007, clarification session 2026-10-08)."""

    entree: str
    motif_echec: str

    def __post_init__(self) -> None:
        if not self.motif_echec.strip():
            raise ValueError("motif_echec ne peut pas etre vide")

    def vers_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "entrée": self.entree,
            "motif_echec": self.motif_echec,
        }


def deriver_titre(titre_source: str) -> str:
    """Derive le nom de sortie (spec 001, FR-007).

    Simplifie les accents, ignore les symboles, remplace les espaces
    par `_`, puis garde les 7 premiers caracteres. Repli `sans_titre`
    si aucun caractere exploitable.
    """
    simplifie = (
        unicodedata.normalize("NFKD", titre_source)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    nettoye = re.sub(r"[^A-Za-z0-9_ ]", "", simplifie).replace(" ", "_")
    if not nettoye:
        return TITRE_REPLI
    return nettoye[:7]


def resoudre_nom(titre: str, dossier: Path, pris: set[str]) -> Path:
    """Retourne un chemin libre `<titre>.json`, suffixe -X si conflit.

    Un nom est pris s'il existe deja sur le disque ou s'il a ete
    attribue dans la meme execution (FR-008, FR-010).
    """
    nom = f"{titre}.json"
    if nom not in pris and not (dossier / nom).exists():
        pris.add(nom)
        return dossier / nom
    compteur = 1
    while True:
        nom = f"{titre}-{compteur}.json"
        if nom not in pris and not (dossier / nom).exists():
            pris.add(nom)
            return dossier / nom
        compteur += 1


def ecrire_tableau(
    enregistrements: Sequence[OutputRecord | EnregistrementEchec],
    chemin: Path,
) -> None:
    """Ecrit un tableau JSON d'enregistrements Vector-2.0, dossier
    cree si absent (FR-001, FR-006)."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    contenu = json.dumps(
        [record.vers_dict() for record in enregistrements],
        ensure_ascii=False,
        indent=2,
    )
    chemin.write_text(contenu + "\n", encoding="utf-8")
