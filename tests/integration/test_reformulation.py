"""Tests d'integration de la reformulation (US-3, quickstart scenario 4)."""

from __future__ import annotations

import json

from question2vector.cli import main
from tests.conftest import usine


def invoquer(client, *arguments):
    return main(list(arguments), usine_client=usine(client))


def test_question_courte_reformulee_puis_vectorisee(
    tmp_path, fabrique_client, cle_test
):
    client = fabrique_client(
        reponse_llm='{"ambiguous": false, "reformulation": '
        '"Comment fonctionne le deploiement du connecteur ?"}'
    )
    sortie = tmp_path / "sortie"
    code = invoquer(
        client,
        "Ca marche comment ?",
        "--reformule",
        "on",
        "--output-folder",
        str(sortie),
    )
    assert code == 0
    charge = json.loads((sortie / "Ca_marc.json").read_text(encoding="utf-8"))
    assert charge["entrée"] == "Ca marche comment ?"
    assert (
        charge["reformulation"] == "Comment fonctionne le deploiement du connecteur ?"
    )
    # le vecteur porte sur la reformulation, pas sur l'original
    [(_, textes)] = client.appels_embedding
    assert textes == ["Comment fonctionne le deploiement du connecteur ?"]


def test_question_ambigue_echoue_sans_fichier(tmp_path, fabrique_client, cle_test):
    client = fabrique_client(
        reponse_llm='{"ambiguous": true, "reformulation": null, '
        '"options": ["a", "b", "c"]}'
    )
    sortie = tmp_path / "sortie"
    code = invoquer(
        client,
        "Comment l'importer ?",
        "--reformule",
        "on",
        "--output-folder",
        str(sortie),
    )
    assert code == 2
    assert list(sortie.glob("*.json")) == []
    assert client.appels_embedding == []


def test_document_long_non_reformule(tmp_path, fabrique_client, cle_test):
    dossier = tmp_path / "entrees"
    dossier.mkdir()
    long_texte = "phrase de cours. " * 60  # > 500 caracteres
    (dossier / "Cours.txt").write_text(long_texte, encoding="utf-8")
    client = fabrique_client()
    sortie = tmp_path / "sortie"
    code = invoquer(
        client,
        str(dossier),
        "--reformule",
        "on",
        "--output-folder",
        str(sortie),
    )
    assert code == 0
    assert client.appels_chat == []
    charge = json.loads((sortie / "Cours.json").read_text(encoding="utf-8"))
    assert charge["reformulation"] == ""
    assert charge["entrée"] == long_texte
    [(_, textes)] = client.appels_embedding
    assert textes == [long_texte]


def test_reformule_desactive_par_defaut(tmp_path, fabrique_client, cle_test):
    client = fabrique_client()
    code = invoquer(
        client,
        "question courte",
        "--output-folder",
        str(tmp_path / "sortie"),
    )
    assert code == 0
    assert client.appels_chat == []


def test_modele_llm_choisi(tmp_path, fabrique_client, cle_test):
    client = fabrique_client(
        reponse_llm='{"ambiguous": false, "reformulation": "ok ?"}'
    )
    code = invoquer(
        client,
        "question",
        "--reformule",
        "on",
        "--choix-modele-llm",
        "large4",
        "--output-folder",
        str(tmp_path / "sortie"),
    )
    assert code == 0
    [(nom_modele, _, _)] = client.appels_chat
    assert nom_modele == "mistral-large-4"
