"""Tests unitaires de reformulation (US-3, FR-012 a FR-014)."""

from __future__ import annotations

from pathlib import Path

import pytest

from question2vector.config import VectorizationOptions
from question2vector.reformulation import (
    SEUIL_ELIGIBILITE,
    ErreurReformulation,
    est_eligible,
    reformuler,
)


def options() -> VectorizationOptions:
    return VectorizationOptions(
        embed_model="1024",
        batch_size=25,
        reformule=True,
        llm_model_alias="small",
        retry_occurrences=2,
        retry_time=1,
        output_folder=Path("sortie_test"),
        temperature_llm=0.2,
        ungroup=False,
    )


def test_eligibilite_au_seuil_exact():
    assert est_eligible("x" * SEUIL_ELIGIBILITE)
    assert not est_eligible("x" * (SEUIL_ELIGIBILITE + 1))


def test_document_long_non_eligible():
    assert not est_eligible("mot " * 200)


def test_reformulation_nominale(fabrique_client):
    client = fabrique_client(
        reponse_llm='{"ambiguous": false, "reformulation": '
        '"Comment fonctionne le deploiement ?"}'
    )
    resultat = reformuler(client, "Ca marche comment ?", options())
    assert resultat == "Comment fonctionne le deploiement ?"
    [(nom_modele, prompt, temperature)] = client.appels_chat
    assert nom_modele == "mistral-small-latest"
    assert "Ca marche comment ?" in prompt
    assert temperature == 0.2


def test_prompt_contient_la_question_et_les_regles(fabrique_client):
    client = fabrique_client(reponse_llm='{"ambiguous": false, "reformulation": "ok"}')
    reformuler(client, "Question de test ?", options())
    [(_, prompt, _)] = client.appels_chat
    assert "reformulateur de questions" in prompt
    assert prompt.rstrip().endswith("Question de test ?")


def test_reponse_ambigue_echoue_sans_sortie(fabrique_client):
    client = fabrique_client(
        reponse_llm='{"ambiguous": true, "reformulation": null, "options": ["a", "b"]}'
    )
    with pytest.raises(ErreurReformulation, match="ambigu"):
        reformuler(client, "Comment l'importer ?", options())


def test_reponse_json_invalide_echoue(fabrique_client):
    client = fabrique_client(reponse_llm="ceci n'est pas du json")
    with pytest.raises(ErreurReformulation, match="malform"):
        reformuler(client, "question ?", options())


def test_reponse_sans_champ_ambiguous_echoue(fabrique_client):
    client = fabrique_client(reponse_llm='{"reformulation": "ok"}')
    with pytest.raises(ErreurReformulation, match="malform"):
        reformuler(client, "question ?", options())


def test_reformulation_vide_echoue(fabrique_client):
    client = fabrique_client(reponse_llm='{"ambiguous": false, "reformulation": "  "}')
    with pytest.raises(ErreurReformulation, match="malform"):
        reformuler(client, "question ?", options())


def test_panne_llm_epuise_les_reprises(fabrique_client):
    def panne():
        raise RuntimeError("service indisponible")

    client = fabrique_client(echec_chat=panne)
    with pytest.raises(RuntimeError, match="indisponible"):
        reformuler(client, "question ?", options())
    assert len(client.appels_chat) == 3  # 1 essai + 2 reprises
