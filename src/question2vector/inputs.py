"""Detection et lecture des entrees (FR-001, FR-002)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

EXTENSIONS_ADMISES = {".txt", ".md"}


class ErreurEntree(ValueError):
    """Argument d'entree non exploitable."""


@dataclass(frozen=True)
class Entree:
    """Un element textuel a vectoriser (data-model.md, InputItem)."""

    type_source: str
    titre_source: str
    texte: str


_MOTIF_EXTENSION = re.compile(r"^[^/\\\s]+\.[A-Za-z0-9]{1,8}$")


def _a_syntaxe_de_chemin(argument: str) -> bool:
    """Vrai si l'argument ressemble a un chemin (FR-001).

    Separateur de chemin present, ou extension en fin d'un token
    unique. Un argument multi-mots sans separateur est une chaine.
    """
    if "/" in argument or "\\" in argument:
        return True
    return bool(_MOTIF_EXTENSION.match(argument))


def _lire_fichier(chemin: Path) -> Entree:
    if chemin.suffix.lower() not in EXTENSIONS_ADMISES:
        raise ErreurEntree(
            f"format non admis : {chemin.name} (seuls .txt et .md sont traites)"
        )
    try:
        texte = chemin.read_text(encoding="utf-8")
    except OSError as err:
        raise ErreurEntree(f"fichier illisible : {chemin.name}") from err
    if not texte.strip():
        raise ErreurEntree(f"entree vide : {chemin.name}")
    return Entree(
        type_source=chemin.suffix.lower().lstrip("."),
        titre_source=chemin.stem,
        texte=texte,
    )


def _lire_dossier(dossier: Path) -> tuple[list[Entree], list[tuple[str, str]]]:
    entrees: list[Entree] = []
    echecs: list[tuple[str, str]] = []
    for enfant in sorted(dossier.iterdir()):
        if not enfant.is_file():
            continue
        if enfant.suffix.lower() not in EXTENSIONS_ADMISES:
            continue
        try:
            entrees.append(_lire_fichier(enfant))
        except ErreurEntree as err:
            echecs.append((str(enfant), str(err)))
    return entrees, echecs


def resoudre_argument(argument: str) -> tuple[list[Entree], list[tuple[str, str]]]:
    """Resout un argument en entrees selon la regle FR-001.

    Retourne (entrees, echecs) : chaque echec est un couple
    (identifiant, motif) ou l'identifiant designe le fichier ou
    l'argument jamais exploite (FR-007 de la spec 002).
    """
    if not argument.strip():
        raise ErreurEntree("entree vide : argument blanc")
    chemin = Path(argument)
    if chemin.is_dir():
        entrees, echecs = _lire_dossier(chemin)
        if not entrees:
            raise ErreurEntree(
                f"le dossier {argument} ne contient aucun fichier "
                ".txt ou .md exploitable"
            )
        return entrees, echecs
    if chemin.is_file():
        return [_lire_fichier(chemin)], []
    if _a_syntaxe_de_chemin(argument):
        raise ErreurEntree(f"chemin introuvable : {argument}")
    return [Entree("chaine", argument, argument)], []


def resoudre_arguments(
    arguments: list[str],
) -> tuple[list[Entree], list[tuple[str, str]]]:
    """Resout tous les arguments ; agrege entrees et echecs.

    Chaque echec est un couple (identifiant, motif) ; l'ordre des
    arguments est perdu par l'agregation, le plan ordonne est
    construit par l'appelant.
    """
    entrees: list[Entree] = []
    echecs: list[tuple[str, str]] = []
    for argument in arguments:
        try:
            sous_entrees, sous_echecs = resoudre_argument(argument)
        except ErreurEntree as err:
            echecs.append((argument, str(err)))
            continue
        entrees.extend(sous_entrees)
        echecs.extend(sous_echecs)
    return entrees, echecs
