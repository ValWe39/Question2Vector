"""Tests unitaires de decoupage en lots et de retry (US-2, FR-015)."""

from __future__ import annotations

import pytest

from question2vector.embedding import avec_retry, decouper_en_lots


def test_decoupage_40_elements_en_lots_de_25():
    textes = [f"texte {i}" for i in range(40)]
    lots = decouper_en_lots(textes, 25)
    assert [len(lot) for lot in lots] == [25, 15]
    assert lots[0][0] == "texte 0"
    assert lots[1][-1] == "texte 39"


def test_decoupage_taille_0_sans_regroupement():
    textes = ["a", "b", "c"]
    lots = decouper_en_lots(textes, 0)
    assert lots == [["a"], ["b"], ["c"]]


def test_decoupage_liste_vide():
    assert decouper_en_lots([], 25) == []


def test_decoupage_taille_superieure_au_nombre():
    assert decouper_en_lots(["a", "b"], 100) == [["a", "b"]]


def test_reussite_des_le_premier_essai_sans_attente():
    delais: list[int] = []

    def appel():
        return "ok"

    resultat = avec_retry(
        appel,
        occurrences=3,
        delai_initial=3,
        veilleuse=delais.append,
    )
    assert resultat == "ok"
    assert delais == []


def test_reprise_avec_delais_doubles():
    tentatives = iter([Exception("echec"), Exception("echec"), "ok"])
    delais: list[int] = []

    def appel():
        resultat = next(tentatives)
        if isinstance(resultat, Exception):
            raise resultat
        return resultat

    resultat = avec_retry(
        appel, occurrences=3, delai_initial=3, veilleuse=delais.append
    )
    assert resultat == "ok"
    assert delais == [3, 6]


def test_epuisement_des_reprises_relance_la_derniere_erreur():
    delais: list[int] = []

    def appel():
        raise RuntimeError("panne persistante")

    with pytest.raises(RuntimeError, match="panne persistante"):
        avec_retry(appel, occurrences=3, delai_initial=3, veilleuse=delais.append)
    assert delais == [3, 6, 12]


def test_occurrences_0_tentative_unique():
    delais: list[int] = []
    compteur = {"n": 0}

    def appel():
        compteur["n"] += 1
        raise RuntimeError("echec")

    with pytest.raises(RuntimeError):
        avec_retry(appel, occurrences=0, delai_initial=3, veilleuse=delais.append)
    assert compteur["n"] == 1
    assert delais == []


def test_delais_configurables_1_puis_2():
    # cas explicite : reprise avec --retry-time 1 --retry-occurences 2
    delais: list[int] = []
    etat = {"n": 0}

    def appel():
        etat["n"] += 1
        if etat["n"] <= 2:
            raise RuntimeError("echec")
        return "ok"

    avec_retry(appel, occurrences=2, delai_initial=1, veilleuse=delais.append)
    assert delais == [1, 2]
