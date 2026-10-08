"""Tests unitaires du schema Vector-2.0 et du nommage (US-1, FR-001,
FR-002, FR-006, FR-007, FR-010)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from question2vector.output import (
    SCHEMA_VERSION,
    EnregistrementEchec,
    OutputRecord,
    deriver_titre,
    ecrire_tableau,
    resoudre_nom,
)

CHAMPS_REUSSITE = {
    "schema_version",
    "entrée",
    "reformulation",
    "vecteur",
    "dimension_vecteur",
    "nature_vecteur",
}


def test_titre_chaine_longue_coupee_a_7():
    assert deriver_titre("Comment fonctionne le depot git ?") == "Comment"


def test_titre_espaces_remplacees_par_underscores():
    assert deriver_titre("Cour comptes") == "Cour_co"


def test_titre_accents_simplifies():
    assert deriver_titre("Cafe creme") == "Cafe_cr"
    assert deriver_titre("Élève à Paris") == "Eleve_a"


def test_titre_symboles_ignores_repli_si_vide():
    assert deriver_titre("***") == "sans_titre"
    assert deriver_titre("??") == "sans_titre"


def test_titre_court_conserve():
    assert deriver_titre("Corsen") == "Corsen"
    assert deriver_titre("Ça marche ?") == "Ca_marc"


def test_conflit_suffixe_numerique(tmp_path: Path):
    pris: set[str] = set()
    premier = resoudre_nom("sortie", tmp_path, pris)
    assert premier.name == "sortie.json"
    deuxieme = resoudre_nom("sortie", tmp_path, pris)
    assert deuxieme.name == "sortie-1.json"
    troisieme = resoudre_nom("sortie", tmp_path, pris)
    assert troisieme.name == "sortie-2.json"


def test_conflit_avec_fichier_existant_sur_disque(tmp_path: Path):
    (tmp_path / "sortie.json").write_text("[]", encoding="utf-8")
    chemin = resoudre_nom("sortie", tmp_path, set())
    assert chemin.name == "sortie-1.json"


def record_de_test(entree: str = "Le texte d'entrée.") -> OutputRecord:
    return OutputRecord(
        entree=entree,
        reformulation="",
        vecteur=[0.5, -0.25],
        dimension_vecteur=2,
        nature_vecteur="float32",
    )


def test_ecriture_toujours_un_tableau(tmp_path: Path):
    chemin = tmp_path / "Sortie.json"
    ecrire_tableau([record_de_test()], chemin)
    charge = json.loads(chemin.read_text(encoding="utf-8"))
    assert isinstance(charge, list)
    assert len(charge) == 1
    (element,) = charge
    assert element["schema_version"] == SCHEMA_VERSION == "Vector-2.0"
    assert element["entrée"] == "Le texte d'entrée."
    assert element["reformulation"] == ""
    assert element["vecteur"] == [0.5, -0.25]
    assert element["dimension_vecteur"] == 2
    assert element["nature_vecteur"] == "float32"
    assert element.keys() == CHAMPS_REUSSITE


def test_ecriture_tableau_conserve_l_ordre(tmp_path: Path):
    chemin = tmp_path / "sortie.json"
    ecrire_tableau(
        [record_de_test("première question"), record_de_test("seconde")],
        chemin,
    )
    charge = json.loads(chemin.read_text(encoding="utf-8"))
    assert [element["entrée"] for element in charge] == [
        "première question",
        "seconde",
    ]


def test_enregistrement_echec_trois_champs_exactement(tmp_path: Path):
    echec = EnregistrementEchec(
        entree="chemin/inexistant.txt",
        motif_echec="chemin introuvable",
    )
    chemin = tmp_path / "Echec.json"
    ecrire_tableau([echec], chemin)
    (element,) = json.loads(chemin.read_text(encoding="utf-8"))
    assert element == {
        "schema_version": "Vector-2.0",
        "entrée": "chemin/inexistant.txt",
        "motif_echec": "chemin introuvable",
    }


def test_enregistrement_echec_motif_vide_refuse():
    with pytest.raises(ValueError, match="motif"):
        EnregistrementEchec(entree="texte", motif_echec="   ")


def test_invariant_dimension_vecteur():
    with pytest.raises(ValueError, match="dimension"):
        OutputRecord(
            entree="texte",
            reformulation="",
            vecteur=[0.1, 0.2],
            dimension_vecteur=3,
            nature_vecteur="float32",
        )
