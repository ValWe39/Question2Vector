"""Tests d'integration du flux unitaire (US-1, quickstart scenario 1 et 2)."""

from __future__ import annotations

import json

from question2vector.cli import main
from tests.conftest import usine


def invoquer(client, *arguments):
    return main(list(arguments), usine_client=usine(client))


def test_chaine_unique_produit_un_json_valide(tmp_path, fabrique_client, cle_test):
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
    assert [f.name for f in fichiers] == ["Comment.json"]
    charge = json.loads(fichiers[0].read_text(encoding="utf-8"))
    assert charge["schema_version"] == "Vector-1.0"
    assert charge["entrée"] == "Comment fonctionne le depot git ?"
    assert charge["reformulation"] == ""
    assert len(charge["vecteur"]) == 1024
    assert charge["dimension_vecteur"] == 1024
    assert charge["nature_vecteur"] == "float32"
    [(nom_modele, textes)] = client.appels_embedding
    assert nom_modele == "mistral-embed"
    assert textes == ["Comment fonctionne le depot git ?"]


def test_fichiers_txt_et_md(tmp_path, fabrique_client, cle_test):
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
    noms = sorted(f.name for f in sortie.glob("*.json"))
    assert noms == ["Corsen.json", "Tocquev.json"]
    charge = json.loads((sortie / "Corsen.json").read_text(encoding="utf-8"))
    assert charge["entrée"] == "contenu txt"


def test_reexecution_suffixe_le_conflit(tmp_path, fabrique_client, cle_test):
    sortie = tmp_path / "sortie"
    client = fabrique_client()
    arguments = ["une question", "--output-folder", str(sortie)]
    assert invoquer(client, *arguments) == 0
    assert invoquer(client, *arguments) == 0
    noms = sorted(f.name for f in sortie.glob("*.json"))
    assert noms == ["une_que-1.json", "une_que.json"]


def test_aucune_entree_exploitable_sort_1(tmp_path, fabrique_client, cle_test):
    client = fabrique_client()
    code = invoquer(
        client,
        "chemin/inexistant.txt",
        "--output-folder",
        str(tmp_path / "sortie"),
    )
    assert code == 1


def test_echec_partiel_sort_2_et_ecrit_les_valides(tmp_path, fabrique_client, cle_test):
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
    assert [f.name for f in sortie.glob("*.json")] == ["questio.json"]


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
