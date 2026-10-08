"""Tests d'integration multi-input, batching et modes de livraison
(US-2, US-3, quickstart scenarios 3, 4 et 6)."""

from __future__ import annotations

import json

from question2vector.cli import main
from tests.conftest import usine


def invoquer(client, *arguments):
    return main(list(arguments), usine_client=usine(client))


def creer_exemples(dossier) -> None:
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


def charger_livrable(chemin):
    charge = json.loads(chemin.read_text(encoding="utf-8"))
    assert isinstance(charge, list)
    return charge


def test_dossier_complet_regroupes_dans_sortie_json(
    tmp_path, fabrique_client, cle_test
):
    exemples = tmp_path / "exemples"
    exemples.mkdir()
    creer_exemples(exemples)
    (exemples / "brouillon.png").write_bytes(b"\x89PNG")
    sortie = tmp_path / "sortie"
    client = fabrique_client()
    code = invoquer(client, str(exemples), "--output-folder", str(sortie))
    assert code == 0
    assert [f.name for f in sortie.glob("*.json")] == ["sortie.json"]
    charge = charger_livrable(sortie / "sortie.json")
    assert len(charge) == 6
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


def test_ungroup_on_produit_un_fichier_par_entree(tmp_path, fabrique_client, cle_test):
    fichier_txt = tmp_path / "Corsen.txt"
    fichier_txt.write_text("contenu txt", encoding="utf-8")
    fichier_md = tmp_path / "Tocqueville2.md"
    fichier_md.write_text("contenu md", encoding="utf-8")
    sortie = tmp_path / "sortie"
    client = fabrique_client()
    code = invoquer(
        client,
        str(fichier_txt),
        str(fichier_md),
        "une question libre",
        "--ungroup",
        "on",
        "--output-folder",
        str(sortie),
    )
    assert code == 0
    noms = sorted(f.name for f in sortie.glob("*.json"))
    assert noms == ["Corsen.json", "Tocquev.json", "une_que.json"]
    for nom in noms:
        (element,) = charger_livrable(sortie / nom)
        assert element["schema_version"] == "Vector-2.0"
        assert "vecteur" in element


def test_conflit_de_titre_intra_execution_en_mode_degroupe(
    tmp_path, fabrique_client, cle_test
):
    dossier = tmp_path / "entrees"
    dossier.mkdir()
    (dossier / "Document1.txt").write_text("premier", encoding="utf-8")
    (dossier / "Document2.md").write_text("second", encoding="utf-8")
    sortie = tmp_path / "sortie"
    client = fabrique_client()
    code = invoquer(
        client,
        str(dossier),
        "--ungroup",
        "on",
        "--output-folder",
        str(sortie),
    )
    assert code == 0
    noms = sorted(f.name for f in sortie.glob("*.json"))
    assert noms == ["Documen-1.json", "Documen.json"]


def test_ungroup_valeur_invalide_refusee_avant_appel(
    tmp_path, fabrique_client, cle_test
):
    client = fabrique_client()
    code = invoquer(
        client,
        "question",
        "--ungroup",
        "peut-etre",
        "--output-folder",
        str(tmp_path / "sortie"),
    )
    assert code == 1
    assert client.appels_embedding == []


def test_echec_partiel_ordre_preserve(tmp_path, fabrique_client, cle_test):
    sortie = tmp_path / "sortie"
    client = fabrique_client()
    code = invoquer(
        client,
        "Question A",
        "chemin/inexistant.txt",
        "Question B",
        "--output-folder",
        str(sortie),
    )
    assert code == 2
    assert [f.name for f in sortie.glob("*.json")] == ["sortie.json"]
    premiere, echec, troisieme = charger_livrable(sortie / "sortie.json")
    assert premiere["entrée"] == "Question A"
    assert "vecteur" in premiere
    assert echec == {
        "schema_version": "Vector-2.0",
        "entrée": "chemin/inexistant.txt",
        "motif_echec": "chemin introuvable",
    }
    assert troisieme["entrée"] == "Question B"
    assert "vecteur" in troisieme


def test_reexecution_suffixe_le_conflit_livrable(tmp_path, fabrique_client, cle_test):
    sortie = tmp_path / "sortie"
    client = fabrique_client()
    arguments = [
        "premiere question",
        "seconde question",
        "--output-folder",
        str(sortie),
    ]
    assert invoquer(client, *arguments) == 0
    assert invoquer(client, *arguments) == 0
    noms = sorted(f.name for f in sortie.glob("*.json"))
    assert noms == ["sortie-1.json", "sortie.json"]


def test_lot_en_echec_livrable_d_echecs(tmp_path, fabrique_client, cle_test):
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
    charge = charger_livrable(sortie / "sortie.json")
    assert len(charge) == 4
    assert all("motif_echec" in element for element in charge)
    assert all("vecteur" not in element for element in charge)


def test_lot_en_panne_transient_reussi_apres_reprise(
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
    sortie = tmp_path / "sortie"
    code = invoquer(
        client,
        str(dossier),
        "--retry-time",
        "1",
        "--retry-occurences",
        "2",
        "--output-folder",
        str(sortie),
    )
    assert code == 0
    assert etat["n"] == 2
    (element,) = charger_livrable(sortie / "sortie.json")
    assert "vecteur" in element
