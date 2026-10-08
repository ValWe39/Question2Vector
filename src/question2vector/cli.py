"""Ligne de commande `vector` (contracts/cli.md de la spec 002)."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

from question2vector.config import (
    ErreurConfiguration,
    VectorizationOptions,
    charger_cle_api,
    construire_options,
)
from question2vector.embedding import (
    EMBED_MODELS,
    avec_retry,
    decouper_en_lots,
)
from question2vector.inputs import Entree, ErreurEntree, resoudre_argument
from question2vector.mistral_client import ClientMistral
from question2vector.output import (
    EnregistrementEchec,
    OutputRecord,
    deriver_titre,
    ecrire_tableau,
    resoudre_nom,
)
from question2vector.reformulation import (
    ErreurReformulation,
    est_eligible,
    reformuler,
)


@dataclass
class RapportElement:
    """Bilan d'un element traite (data-model.md, ProcessingReport)."""

    titre: str
    ok: bool
    fichier: str | None = None
    motif: str | None = None


def _motif_court(message: str) -> str:
    """Garde la cause d'un message d'erreur, sans le detail."""
    return message.split(" : ", 1)[0]


def construire_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(
        prog="vector",
        description=(
            "Vectorise une chaine, un fichier .txt/.md, un dossier ou "
            "un melange, via les embeddings Mistral."
        ),
    )
    parseur.add_argument(
        "entrees",
        nargs="+",
        metavar="ENTREE",
        help="chaine de caracteres, fichier .txt/.md ou dossier",
    )
    parseur.add_argument(
        "--choix-techno-embed",
        default="1024",
        help="modele d'embedding : 1024, 256 ou 128 (defaut : 1024)",
    )
    parseur.add_argument(
        "--taille-batch",
        default="25",
        help="taille des lots d'embedding, 0 a 100 (defaut : 25 ; 0 = pas de lot)",
    )
    parseur.add_argument(
        "--reformule",
        default="no",
        help="reformulation LLM des questions courtes : on ou no (defaut : no)",
    )
    parseur.add_argument(
        "--choix-modele-llm",
        default="small",
        help="modele LLM de reformulation (defaut : small)",
    )
    parseur.add_argument(
        "--retry-occurences",
        default="3",
        help="nombre de reprises par echec, 0 a 10 (defaut : 3)",
    )
    parseur.add_argument(
        "--retry-time",
        default="3",
        help="delai en secondes de la premiere reprise, 1 a 10 "
        "(defaut : 3, double a chaque reprise)",
    )
    parseur.add_argument(
        "--output-folder",
        default="output",
        help="dossier de sortie (defaut : output)",
    )
    parseur.add_argument(
        "--temperature-llm",
        default="0.2",
        help="temperature du LLM de reformulation, 0 a 1 (defaut : 0,2)",
    )
    parseur.add_argument(
        "--ungroup",
        default="no",
        help="une sortie par entree au lieu d'un livrable unique : "
        "on ou no (defaut : no)",
    )
    return parseur


def _planifier(
    arguments: list[str],
) -> tuple[list[tuple[str, object]], list[Entree]]:
    """Construit le plan ordonne du run (FR-005).

    Chaque argument aboutit a une ou plusieurs entrees, ou a un
    echec de detection, dans l'ordre des arguments d'appel. Le plan
    est une liste de couples ("entree", index) et
    ("echec", (identifiant, motif)).
    """
    plan: list[tuple[str, object]] = []
    entrees: list[Entree] = []
    for argument in arguments:
        try:
            sous_entrees, sous_echecs = resoudre_argument(argument)
        except ErreurEntree as err:
            plan.append(("echec", (argument, str(err))))
            continue
        for entree in sous_entrees:
            plan.append(("entree", len(entrees)))
            entrees.append(entree)
        for identifiant, motif in sous_echecs:
            plan.append(("echec", (identifiant, motif)))
    return plan, entrees


def executer(
    entrees: list[Entree],
    options: VectorizationOptions,
    client,
) -> tuple[list[OutputRecord | EnregistrementEchec], list[RapportElement]]:
    """Traite chaque entree et retourne les enregistrements alignes
    sur `entrees`, plus le bilan aligne sur le meme ordre (FR-007).

    Seule l'etape d'embedding est regroupee en lots ; la
    reformulation reste element par element. Une entree en echec
    produit un EnregistrementEchec.
    """
    modele = EMBED_MODELS[options.embed_model]
    rapports: list[RapportElement | None] = [None] * len(entrees)
    resultats: list[OutputRecord | EnregistrementEchec | None] = [None] * len(entrees)

    # Phase 1 : reformulation, element par element
    a_vectoriser: list[tuple[int, str, str]] = []
    for i, entree in enumerate(entrees):
        if options.reformule and est_eligible(entree.texte):
            try:
                reformulation = reformuler(client, entree.texte, options)
            except ErreurReformulation as err:
                motif = str(err)
                resultats[i] = EnregistrementEchec(entree.texte, motif)
                rapports[i] = RapportElement(entree.titre_source, False, motif=motif)
                continue
            a_vectoriser.append((i, reformulation, reformulation))
        else:
            a_vectoriser.append((i, "", entree.texte))

    # Phase 2 : embedding regroupe en lots, avec reprise par lot
    vecteurs: dict[int, list[float]] = {}
    echecs_lot: set[int] = set()
    texte_par_index = {i: texte for i, _, texte in a_vectoriser}
    lots = decouper_en_lots(list(texte_par_index), options.batch_size)
    for lot in lots:
        indexes = lot
        textes = [texte_par_index[i] for i in indexes]
        try:
            appel = partial(client.embedder, modele.nom_api, textes)
            vecteurs_lot = avec_retry(
                appel,
                options.retry_occurrences,
                options.retry_time,
            )
        except Exception as err:  # noqa: BLE001 - echec de lot, on
            # poursuit les autres lots (cas limites de la spec)
            echecs_lot.update(indexes)
            for i in indexes:
                motif = f"echec d'embedding : {err}"
                resultats[i] = EnregistrementEchec(entrees[i].texte, motif)
                rapports[i] = RapportElement(
                    entrees[i].titre_source, False, motif=motif
                )
            continue
        for i, vecteur in zip(indexes, vecteurs_lot, strict=True):
            vecteurs[i] = vecteur

    # Phase 3 : enregistrements, dans l'ordre des entrees
    for i, reformulation, _ in a_vectoriser:
        if i in echecs_lot:
            continue
        vecteur = vecteurs.get(i)
        if vecteur is None:
            motif = "vecteur manquant pour cet element"
            resultats[i] = EnregistrementEchec(entrees[i].texte, motif)
            rapports[i] = RapportElement(entrees[i].titre_source, False, motif=motif)
            continue
        try:
            record = OutputRecord(
                entree=entrees[i].texte,
                reformulation=reformulation,
                vecteur=vecteur,
                dimension_vecteur=modele.dimension,
                nature_vecteur=modele.nature,
            )
        except ValueError as err:
            motif = str(err)
            resultats[i] = EnregistrementEchec(entrees[i].texte, motif)
            rapports[i] = RapportElement(entrees[i].titre_source, False, motif=motif)
            continue
        resultats[i] = record
        rapports[i] = RapportElement(entrees[i].titre_source, True)
    assert all(r is not None for r in rapports)
    assert all(res is not None for res in resultats)
    return resultats, rapports  # type: ignore[return-value]


def _afficher_bilan(
    rapports: list[RapportElement],
    echecs_detection: list[tuple[str, str]],
) -> None:
    for identifiant, motif in echecs_detection:
        print(f"Echec d'entree : {identifiant} : {motif}", file=sys.stderr)
    for rapport in rapports:
        if rapport.ok:
            print(f"OK   {rapport.fichier}")
        else:
            print(
                f"Echec {rapport.titre} : {rapport.motif}",
                file=sys.stderr,
            )
    reussis = sum(1 for r in rapports if r.ok)
    print(
        f"Bilan : {reussis} element(s) vectorise(s), "
        f"{len(rapports) - reussis} en echec, "
        f"{len(echecs_detection)} entree(s) non resolue(s)"
    )


def main(
    argv: list[str] | None = None,
    usine_client: Callable[[str], ClientMistral] | None = None,
) -> int:
    """Point d'entree : retourne le code de sortie (contracts/cli.md).

    0 : tous les elements traites ; 1 : erreur de configuration ou
    aucune entree exploitable ; 2 : au moins un element en echec.
    """
    args = construire_parseur().parse_args(argv)
    try:
        options = construire_options(
            embed_model=args.choix_techno_embed,
            taille_batch=args.taille_batch,
            reformule=args.reformule,
            llm_model_alias=args.choix_modele_llm,
            retry_occurrences=args.retry_occurences,
            retry_time=args.retry_time,
            output_folder=args.output_folder,
            temperature_llm=args.temperature_llm,
            ungroup=args.ungroup,
        )
        cle_api = charger_cle_api()
    except ErreurConfiguration as err:
        print(f"Erreur de configuration : {err}", file=sys.stderr)
        return 1

    plan, entrees = _planifier(args.entrees)
    echecs_detection = [charge for genre, charge in plan if genre == "echec"]
    if not entrees:
        for identifiant, motif in echecs_detection:
            print(f"Echec d'entree : {identifiant} : {motif}", file=sys.stderr)
        print("Aucune entree exploitable.", file=sys.stderr)
        return 1

    client = (usine_client or ClientMistral)(cle_api)
    resultats, rapports = executer(entrees, options, client)

    pris: set[str] = set()
    if options.ungroup:
        for genre, charge in plan:
            if genre == "entree":
                i = charge
                record = resultats[i]
                titre = deriver_titre(entrees[i].titre_source)
            else:
                identifiant, motif = charge
                record = EnregistrementEchec(identifiant, _motif_court(motif))
                titre = deriver_titre(identifiant)
            chemin = resoudre_nom(titre, options.output_folder, pris)
            ecrire_tableau([record], chemin)
            if genre == "entree":
                rapports[i].fichier = str(chemin)
    else:
        enregistrements: list[OutputRecord | EnregistrementEchec] = []
        for genre, charge in plan:
            if genre == "entree":
                enregistrements.append(resultats[charge])
            else:
                identifiant, motif = charge
                enregistrements.append(
                    EnregistrementEchec(identifiant, _motif_court(motif))
                )
        chemin = resoudre_nom("sortie", options.output_folder, pris)
        ecrire_tableau(enregistrements, chemin)
        for rapport in rapports:
            if rapport.ok:
                rapport.fichier = str(chemin)

    _afficher_bilan(rapports, echecs_detection)

    if echecs_detection or any(not r.ok for r in rapports):
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
