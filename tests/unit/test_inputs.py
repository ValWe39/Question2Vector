"""Tests unitaires de detection d'entree (US-1, FR-001, FR-002)."""

from __future__ import annotations

from pathlib import Path

import pytest

from question2vector.inputs import (
    Entree,
    ErreurEntree,
    resoudre_argument,
    resoudre_arguments,
)


def test_fichier_txt_existant(tmp_path: Path):
    fichier = tmp_path / "Corsen.txt"
    fichier.write_text("Le contenu du fichier.", encoding="utf-8")
    entrees, echecs = resoudre_argument(str(fichier))
    assert entrees == [
        Entree(type_source="txt", titre_source="Corsen", texte="Le contenu du fichier.")
    ]
    assert echecs == []


def test_fichier_md_existant(tmp_path: Path):
    fichier = tmp_path / "Tocqueville2.md"
    fichier.write_text("# Titre\n\ndu markdown", encoding="utf-8")
    entrees, _ = resoudre_argument(str(fichier))
    (entree,) = entrees
    assert entree.type_source == "md"
    assert entree.titre_source == "Tocqueville2"
    assert entree.texte == "# Titre\n\ndu markdown"


def test_chaine_litterale():
    entrees, _ = resoudre_argument("Comment fonctionne le depot git ?")
    (entree,) = entrees
    assert entree.type_source == "chaine"
    assert entree.titre_source == "Comment fonctionne le depot git ?"
    assert entree.texte == "Comment fonctionne le depot git ?"


def test_chemin_avec_separateur_inexistant():
    with pytest.raises(ErreurEntree, match="introuvable"):
        resoudre_argument("dossier_inconnu/fichier.txt")


def test_chemin_avec_extension_inexistante():
    with pytest.raises(ErreurEntree, match="introuvable"):
        resoudre_argument("inconnu.txt")


def test_fichier_autre_format_refuse(tmp_path: Path):
    fichier = tmp_path / "donnees.csv"
    fichier.write_text("a,b", encoding="utf-8")
    with pytest.raises(ErreurEntree, match="format non admis"):
        resoudre_argument(str(fichier))


def test_fichier_vide_non_traitable(tmp_path: Path):
    fichier = tmp_path / "vide.txt"
    fichier.write_text("   ", encoding="utf-8")
    with pytest.raises(ErreurEntree, match="vide"):
        resoudre_argument(str(fichier))


def test_chaine_vide_non_traitable():
    with pytest.raises(ErreurEntree, match="vide"):
        resoudre_argument("   ")


def test_dossier_nen_garde_que_txt_et_md(tmp_path: Path):
    for nom in ("Alpha.txt", "Beta.md", "Gamma.csv", "Delta.png"):
        (tmp_path / nom).write_text("contenu", encoding="utf-8")
    entrees, _ = resoudre_argument(str(tmp_path))
    assert [e.titre_source for e in entrees] == ["Alpha", "Beta"]


def test_dossier_avec_sous_dossier_non_recursif(tmp_path: Path):
    (tmp_path / "Seul.txt").write_text("haut", encoding="utf-8")
    sous = tmp_path / "sous_dossier"
    sous.mkdir()
    (sous / "Profond.txt").write_text("bas", encoding="utf-8")
    entrees, _ = resoudre_argument(str(tmp_path))
    assert [e.texte for e in entrees] == ["haut"]


def test_dossier_sans_fichier_eligible(tmp_path: Path):
    (tmp_path / "image.png").write_text("x", encoding="utf-8")
    with pytest.raises(ErreurEntree, match="aucun fichier"):
        resoudre_argument(str(tmp_path))


def test_dossier_fichier_vide_signale_sans_arret(tmp_path: Path):
    (tmp_path / "Bon.txt").write_text("ok", encoding="utf-8")
    (tmp_path / "Vide.txt").write_text("", encoding="utf-8")
    entrees, echecs = resoudre_arguments([str(tmp_path)])
    assert [e.titre_source for e in entrees] == ["Bon"]
    assert len(echecs) == 1
    assert "Vide.txt" in echecs[0]


def test_resoudre_arguments_agrege_les_echecs(tmp_path: Path):
    bon = tmp_path / "Bon.md"
    bon.write_text("contenu", encoding="utf-8")
    entrees, echecs = resoudre_arguments(
        [str(bon), "chemin/inconnu.txt", "une question libre"]
    )
    assert len(entrees) == 2
    assert len(echecs) == 1
    assert "introuvable" in echecs[0]
