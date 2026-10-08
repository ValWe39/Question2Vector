"""Tests d'integration du flux unitaire (US-1, quickstart scenarios
1, 2 et 6)."""

from __future__ import annotations

import json

from question2vector.cli import main
from tests.conftest import usine

CHAMPS_REUSSITE = {
    "schema_version",
    "entrée",
    "reformulation",
    "vecteur",
    "dimension_vecteur",
    "nature_vecteur",
}


def invoquer(client, *arguments):
    return main(list(arguments), usine_client=usine(client))


def charger_livrable(chemin):
    """Charge le tableau JSON produit et verifie le format (FR-001)."""
    charge = json.loads(chemin.read_text(encoding="utf-8"))
    assert isinstance(charge, list)
    return charge


def test_chaine_unique_produit_tableau_un_element(tmp_path, fabrique_client, cle_test):
    client = fabrique_client()
    sortie = tmp_path / "sortie"
    code = invoquer(
        client,
        "Comment fonctionne le depot git ?",
        "--output-folder",
        str(sortie),
    )
    assert code == 0
    fichiers = list(sortie.glob("*.json"))
    assert [f.name for f in fichiers] == ["sortie.json"]
    (element,) = charger_livrable(sortie / "sortie.json")
    assert element["schema_version"] == "Vector-2.0"
    assert element["entrée"] == "Comment fonctionne le depot git ?"
    assert element["reformulation"] == ""
    assert len(element["vecteur"]) == 1024
    assert element["dimension_vecteur"] == 1024
    assert element["nature_vecteur"] == "float32"
    assert element.keys() == CHAMPS_REUSSITE
    [(nom_modele, textes)] = client.appels_embedding
    assert nom_modele == "mistral-embed"
    assert textes == ["Comment fonctionne le depot git ?"]


def test_fichiers_txt_et_md_regroupes(tmp_path, fabrique_client, cle_test):
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
        "--output-folder",
        str(sortie),
    )
    assert code == 0
    assert [f.name for f in sortie.glob("*.json")] == ["sortie.json"]
    charge = charger_livrable(sortie / "sortie.json")
    assert [element["entrée"] for element in charge] == [
        "contenu txt",
        "contenu md",
    ]


def test_reexecution_suffixe_le_conflit(tmp_path, fabrique_client, cle_test):
    sortie = tmp_path / "sortie"
    client = fabrique_client()
    arguments = ["une question", "--output-folder", str(sortie)]
    assert invoquer(client, *arguments) == 0
    assert invoquer(client, *arguments) == 0
    noms = sorted(f.name for f in sortie.glob("*.json"))
    assert noms == ["sortie-1.json", "sortie.json"]


def test_aucune_entree_exploitable_sort_1(tmp_path, fabrique_client, cle_test):
    client = fabrique_client()
    code = invoquer(
        client,
        "chemin/inexistant.txt",
        "--output-folder",
        str(tmp_path / "sortie"),
    )
    assert code == 1


def test_echec_partiel_livrable_exhaustif(tmp_path, fabrique_client, cle_test):
    sortie = tmp_path / "sortie"
    client = fabrique_client()
    code = invoquer(
        client,
        "question valide",
        "chemin/inexistant.txt",
        "--output-folder",
        str(sortie),
    )
    assert code == 2
    assert [f.name for f in sortie.glob("*.json")] == ["sortie.json"]
    reussite, echec = charger_livrable(sortie / "sortie.json")
    assert reussite["entrée"] == "question valide"
    assert "vecteur" in reussite
    assert echec == {
        "schema_version": "Vector-2.0",
        "entrée": "chemin/inexistant.txt",
        "motif_echec": "chemin introuvable",
    }


def test_cle_absente_echoue_avant_tout_appel(tmp_path, fabrique_client, monkeypatch):
    import question2vector.config as module_config

    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    def ne_rien_faire(*args, **kwargs):
        return None

    monkeypatch.setattr(module_config, "load_dotenv", ne_rien_faire)
    client = fabrique_client()
    code = invoquer(client, "question", "--output-folder", str(tmp_path / "sortie"))
    assert code == 1
    assert client.appels_embedding == []
    assert not (tmp_path / "sortie").exists()
