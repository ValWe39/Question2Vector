"""Tests unitaires de bornes des options (US-4, FR-011)."""

from __future__ import annotations

from pathlib import Path

import pytest

from question2vector.config import (
    ErreurConfiguration,
    VectorizationOptions,
    charger_cle_api,
    construire_options,
)


def options_valides(**surcharges) -> dict:
    valeurs = {
        "embed_model": "1024",
        "taille_batch": "25",
        "reformule": "no",
        "llm_model_alias": "small",
        "retry_occurrences": "3",
        "retry_time": "3",
        "output_folder": "sortie_test",
        "temperature_llm": "0.2",
    }
    valeurs.update(surcharges)
    return valeurs


def test_valeurs_par_defaut_valides():
    resultat = construire_options(**options_valides())
    assert isinstance(resultat, VectorizationOptions)
    assert resultat.embed_model == "1024"
    assert resultat.batch_size == 25
    assert resultat.reformule is False
    assert resultat.llm_model_alias == "small"
    assert resultat.retry_occurrences == 3
    assert resultat.retry_time == 3
    assert resultat.output_folder == Path("sortie_test")
    assert resultat.temperature_llm == pytest.approx(0.2)


@pytest.mark.parametrize(
    ("champ", "motif"),
    [
        ("taille_batch", "taille-batch"),
        ("retry_occurrences", "retry-occurences"),
        ("retry_time", "retry-time"),
        ("temperature_llm", "temperature-llm"),
    ],
)
def test_valeur_non_numerique_refusee(champ, motif):
    with pytest.raises(ErreurConfiguration, match=motif):
        construire_options(**options_valides(**{champ: "abc"}))


def test_taille_batch_hors_bornes_refusee():
    with pytest.raises(ErreurConfiguration, match="taille-batch"):
        construire_options(**options_valides(taille_batch="150"))
    with pytest.raises(ErreurConfiguration, match="taille-batch"):
        construire_options(**options_valides(taille_batch="-1"))


def test_retry_occurences_hors_bornes_refusee():
    with pytest.raises(ErreurConfiguration, match="retry-occurences"):
        construire_options(**options_valides(retry_occurrences="11"))


def test_retry_time_hors_bornes_refusee():
    with pytest.raises(ErreurConfiguration, match="retry-time"):
        construire_options(**options_valides(retry_time="0"))
    with pytest.raises(ErreurConfiguration, match="retry-time"):
        construire_options(**options_valides(retry_time="11"))


def test_temperature_hors_bornes_refusee():
    with pytest.raises(ErreurConfiguration, match="temperature"):
        construire_options(**options_valides(temperature_llm="1.5"))
    with pytest.raises(ErreurConfiguration, match="temperature"):
        construire_options(**options_valides(temperature_llm="-0.1"))


def test_temperature_virgule_decimale_admise():
    resultat = construire_options(**options_valides(temperature_llm="0,2"))
    assert resultat.temperature_llm == pytest.approx(0.2)


def test_modele_embed_inconnu_refuse():
    with pytest.raises(ErreurConfiguration, match="choix-techno-embed"):
        construire_options(**options_valides(embed_model="512"))


def test_modele_llm_inconnu_refuse():
    with pytest.raises(ErreurConfiguration, match="choix-modele-llm"):
        construire_options(**options_valides(llm_model_alias="geant"))


def test_reformule_valeur_inconnue_refusee():
    with pytest.raises(ErreurConfiguration, match="reformule"):
        construire_options(**options_valides(reformule="peut-etre"))


def test_cle_absente_avant_tout_appel(tmp_path, monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    with pytest.raises(ErreurConfiguration, match="MISTRAL_API_KEY"):
        charger_cle_api(chemin_env=str(tmp_path / "absent.env"))


def test_cle_chargee_depuis_environnement(monkeypatch):
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-valide")
    assert charger_cle_api(chemin_env=None) == "cle-valide"
