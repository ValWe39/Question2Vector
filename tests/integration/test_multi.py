"""Tests d'integration multi-input et batching (US-2, quickstart scenario 3)."""

from __future__ import annotations

from pathlib import Path

from question2vector.cli import main
from tests.conftest import usine


def invoquer(client, *arguments):
    return main(list(arguments), usine_client=usine(client))


def creer_exemples(dossier: Path) -> None:
    noms = [
        "Corsen.txt",
        "Corsen2.md",
        "CourCptes1.txt",
        "CourCptes2.md",
        "Tocqueville1.txt",
        "Tocqueville2.md",
    ]
    for nom in noms:
        (dossier / nom).write_text(f"contenu de {nom}", encoding="utf-8")


def test_dossier_complet_produit_6_json(tmp_path, fabrique_client, cle_test):
    exemples = tmp_path / "exemples"
    exemples.mkdir()
    creer_exemples(exemples)
    (exemples / "brouillon.png").write_bytes(b"\x89PNG")
    sortie = tmp_path / "sortie"
    client = fabrique_client()
    code = invoquer(client, str(exemples), "--output-folder", str(sortie))
    assert code == 0
    noms = sorted(f.name for f in sortie.glob("*.json"))
    assert len(noms) == 6
    assert "brouillon" not in " ".join(noms)
    # 6 textes regroupes en un seul lot de 25 par defaut
    [(nom_modele, textes)] = client.appels_embedding
    assert nom_modele == "mistral-embed"
    assert len(textes) == 6


def test_decoupage_en_lots_de_deux(tmp_path, fabrique_client, cle_test):
    exemples = tmp_path / "exemples"
    exemples.mkdir()
    creer_exemples(exemples)
    client = fabrique_client()
    code = invoquer(
        client,
        str(exemples),
        "--taille-batch",
        "2",
        "--output-folder",
        str(tmp_path / "sortie"),
    )
    assert code == 0
    tailles = [len(textes) for _, textes in client.appels_embedding]
    assert tailles == [2, 2, 2]


def test_taille_batch_zero_sans_regroupement(tmp_path, fabrique_client, cle_test):
    exemples = tmp_path / "exemples"
    exemples.mkdir()
    creer_exemples(exemples)
    client = fabrique_client()
    code = invoquer(
        client,
        str(exemples),
        "--taille-batch",
        "0",
        "--output-folder",
        str(tmp_path / "sortie"),
    )
    assert code == 0
    tailles = [len(textes) for _, textes in client.appels_embedding]
    assert tailles == [1] * 6


def test_conflit_de_titre_intra_execution(tmp_path, fabrique_client, cle_test):
    dossier = tmp_path / "entrees"
    dossier.mkdir()
    (dossier / "Document1.txt").write_text("premier", encoding="utf-8")
    (dossier / "Document2.md").write_text("second", encoding="utf-8")
    sortie = tmp_path / "sortie"
    client = fabrique_client()
    code = invoquer(client, str(dossier), "--output-folder", str(sortie))
    assert code == 0
    noms = sorted(f.name for f in sortie.glob("*.json"))
    assert noms == ["Documen-1.json", "Documen.json"]


def test_lot_en_echec_n_arrete_pas_les_autres(tmp_path, fabrique_client, cle_test):
    dossier = tmp_path / "entrees"
    dossier.mkdir()
    for i in range(4):
        (dossier / f"F{i}.txt").write_text(f"texte {i}", encoding="utf-8")

    def echec_sur_lot_complet():
        raise RuntimeError("panne du lot")

    client = fabrique_client(echec_embedding=echec_sur_lot_complet)
    sortie = tmp_path / "sortie"
    code = invoquer(
        client,
        str(dossier),
        "--taille-batch",
        "2",
        "--retry-occurences",
        "0",
        "--output-folder",
        str(sortie),
    )
    assert code == 2
    assert list(sortie.glob("*.json")) == []


def test_lot_en_panse_transient_reussi_apres_reprise(
    tmp_path, fabrique_client, cle_test
):
    dossier = tmp_path / "entrees"
    dossier.mkdir()
    (dossier / "Seul.txt").write_text("texte", encoding="utf-8")
    etat = {"n": 0}

    def panne_transient():
        etat["n"] += 1
        if etat["n"] == 1:
            raise RuntimeError("panne passagere")

    client = fabrique_client(echec_embedding=panne_transient)
    code = invoquer(
        client,
        str(dossier),
        "--retry-time",
        "1",
        "--retry-occurences",
        "2",
        "--output-folder",
        str(tmp_path / "sortie"),
    )
    assert code == 0
    assert etat["n"] == 2
