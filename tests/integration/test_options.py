"""Tests d'integration des options (US-4, quickstart scenario 5)."""

from __future__ import annotations

import json

from question2vector.cli import main
from tests.conftest import usine


def invoquer(client, *arguments):
    return main(list(arguments), usine_client=usine(client))


def test_modele_256_dimensions(tmp_path, fabrique_client, cle_test):
    client = fabrique_client(dimension=256)
    sortie = tmp_path / "sortie"
    code = invoquer(
        client,
        "question",
        "--choix-techno-embed",
        "256",
        "--output-folder",
        str(sortie),
    )
    assert code == 0
    charge = json.loads((sortie / "questio.json").read_text(encoding="utf-8"))
    assert charge["dimension_vecteur"] == 256
    assert len(charge["vecteur"]) == 256
    [(nom_modele, _)] = client.appels_embedding
    assert nom_modele == "mistral-embed-dim256-2510"


def test_modele_128_dimensions(tmp_path, fabrique_client, cle_test):
    client = fabrique_client(dimension=128)
    code = invoquer(
        client,
        "question",
        "--choix-techno-embed",
        "128",
        "--output-folder",
        str(tmp_path / "sortie"),
    )
    assert code == 0
    charge = json.loads(
        (tmp_path / "sortie" / "questio.json").read_text(encoding="utf-8")
    )
    assert charge["dimension_vecteur"] == 128


def test_valeur_hors_bornes_refusee_avant_appel(tmp_path, fabrique_client, cle_test):
    client = fabrique_client()
    code = invoquer(
        client,
        "question",
        "--taille-batch",
        "150",
        "--output-folder",
        str(tmp_path / "sortie"),
    )
    assert code == 1
    assert client.appels_embedding == []
    assert not (tmp_path / "sortie").exists()


def test_alias_llm_inconnu_refuse(tmp_path, fabrique_client, cle_test):
    client = fabrique_client()
    code = invoquer(
        client,
        "question",
        "--choix-modele-llm",
        "geant",
        "--output-folder",
        str(tmp_path / "sortie"),
    )
    assert code == 1


def test_dossier_de_sortie_personnalise_cree(tmp_path, fabrique_client, cle_test):
    sortie = tmp_path / "perso" / "resultats"
    client = fabrique_client()
    code = invoquer(client, "question", "--output-folder", str(sortie))
    assert code == 0
    assert (sortie / "questio.json").exists()


def test_temperature_transmise_au_llm(tmp_path, fabrique_client, cle_test):
    client = fabrique_client(
        reponse_llm='{"ambiguous": false, "reformulation": "ok ?"}'
    )
    code = invoquer(
        client,
        "question",
        "--reformule",
        "on",
        "--temperature-llm",
        "0.5",
        "--output-folder",
        str(tmp_path / "sortie"),
    )
    assert code == 0
    [(_, _, temperature)] = client.appels_chat
    assert temperature == 0.5


def test_dimension_inattendue_fait_echouer_l_element(
    tmp_path, fabrique_client, cle_test
):
    # le client fictif annonce 512 alors que le modele en promet 1024
    client = fabrique_client(dimension=512)
    code = invoquer(client, "question", "--output-folder", str(tmp_path / "sortie"))
    assert code == 2
    assert list((tmp_path / "sortie").glob("*.json")) == []
