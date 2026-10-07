"""Tests unitaires de nommage et d'ecriture (US-1, FR-007, FR-008)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from question2vector.output import (
    SCHEMA_VERSION,
    OutputRecord,
    deriver_titre,
    ecrire_sortie,
    resoudre_nom,
)


def test_titre_chaine_longue_coupee_a_7():
    assert deriver_titre("Comment fonctionne le depot git ?") == "Comment"


def test_titre_espaces_remplacees_par_underscores():
    assert deriver_titre("Cour comptes") == "Cour_co"


def test_titre_accents_simplifies():
    assert deriver_titre("Cafe creme") == "Cafe_cr"
    assert deriver_titre("Élève à Paris") == "Eleve_a"


def test_titre_symboles_ignores_repli_si_vide():
    assert deriver_titre("***") == "sans_titre"
    assert deriver_titre("???") == "sans_titre"


def test_titre_court_conserve():
    assert deriver_titre("Corsen") == "Corsen"
    assert deriver_titre("Ça marche ?") == "Ca_marc"


def test_conflit_suffixe_numerique(tmp_path: Path):
    pris: set[str] = set()
    premier = resoudre_nom("Corsen", tmp_path, pris)
    assert premier.name == "Corsen.json"
    deuxieme = resoudre_nom("Corsen", tmp_path, pris)
    assert deuxieme.name == "Corsen-1.json"
    troisieme = resoudre_nom("Corsen", tmp_path, pris)
    assert troisieme.name == "Corsen-2.json"


def test_conflit_avec_fichier_existant_sur_disque(tmp_path: Path):
    (tmp_path / "Titre.json").write_text("{}", encoding="utf-8")
    chemin = resoudre_nom("Titre", tmp_path, set())
    assert chemin.name == "Titre-1.json"


def test_ecriture_json_complet(tmp_path: Path):
    record = OutputRecord(
        entree="Le texte d'entrée.",
        reformulation="",
        vecteur=[0.5, -0.25],
        dimension_vecteur=2,
        nature_vecteur="float32",
    )
    chemin = tmp_path / "Sortie.json"
    ecrire_sortie(record, chemin)
    charge = json.loads(chemin.read_text(encoding="utf-8"))
    assert charge["schema_version"] == SCHEMA_VERSION
    assert charge["entrée"] == "Le texte d'entrée."
    assert charge["reformulation"] == ""
    assert charge["vecteur"] == [0.5, -0.25]
    assert charge["dimension_vecteur"] == 2
    assert charge["nature_vecteur"] == "float32"
    assert charge.keys() == {
        "schema_version",
        "entrée",
        "reformulation",
        "vecteur",
        "dimension_vecteur",
        "nature_vecteur",
    }


def test_invariant_dimension_vecteur():
    with pytest.raises(ValueError, match="dimension"):
        OutputRecord(
            entree="texte",
            reformulation="",
            vecteur=[0.1, 0.2],
            dimension_vecteur=3,
            nature_vecteur="float32",
        )
