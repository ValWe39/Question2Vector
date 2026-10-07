"""Nommage des sorties et ecriture du JSON Vector-1.0 (FR-005, FR-007,
FR-008)."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

SCHEMA_VERSION = "Vector-1.0"
TITRE_REPLI = "sans_titre"


@dataclass(frozen=True)
class OutputRecord:
    """Enregistrement de sortie (data-model.md, schema Vector-1.0)."""

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


def deriver_titre(titre_source: str) -> str:
    """Derive le nom de sortie (FR-007).

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
    attribue dans la meme execution (FR-008).
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


def ecrire_sortie(record: OutputRecord, chemin: Path) -> None:
    """Ecrit le JSON de sortie, dossier cree si absent (FR-006)."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    contenu = json.dumps(record.vers_dict(), ensure_ascii=False, indent=2)
    chemin.write_text(contenu + "\n", encoding="utf-8")
