"""Ligne de commande `vector` (contracts/cli.md)."""

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
from question2vector.inputs import Entree, resoudre_arguments
from question2vector.mistral_client import ClientMistral
from question2vector.output import (
    OutputRecord,
    deriver_titre,
    ecrire_sortie,
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
    return parseur


def executer(
    entrees: list[Entree],
    options: VectorizationOptions,
    client,
) -> list[RapportElement]:
    """Traite chaque element independamment (FR-003) et retourne le
    bilan complet.

    Seule l'etape d'embedding est regroupee en lots (FR-004) ; la
    reformulation reste element par element.
    """
    modele = EMBED_MODELS[options.embed_model]
    rapports: list[RapportElement] = []

    # Phase 1 : reformulation, element par element
    a_vectoriser: list[tuple[Entree, str, str]] = []
    for entree in entrees:
        if options.reformule and est_eligible(entree.texte):
            try:
                reformulation = reformuler(client, entree.texte, options)
            except ErreurReformulation as err:
                rapports.append(
                    RapportElement(entree.titre_source, False, motif=str(err))
                )
                continue
            a_vectoriser.append((entree, reformulation, reformulation))
        else:
            a_vectoriser.append((entree, "", entree.texte))

    # Phase 2 : embedding regroupe en lots, avec reprise par lot
    vecteurs: dict[int, list[float]] = {}
    echecs_lot: set[int] = set()
    lots = decouper_en_lots(list(range(len(a_vectoriser))), options.batch_size)
    for lot in lots:
        indexes = lot
        textes = [a_vectoriser[i][2] for i in indexes]
        try:
            appel = partial(client.embedder, modele.nom_api, textes)
            resultats = avec_retry(
                appel,
                options.retry_occurrences,
                options.retry_time,
            )
        except Exception as err:  # noqa: BLE001 - echec de lot, on
            # poursuit les autres lots (cas limites de la spec)
            echecs_lot.update(indexes)
            for i in indexes:
                rapports.append(
                    RapportElement(
                        a_vectoriser[i][0].titre_source,
                        False,
                        motif=f"echec d'embedding : {err}",
                    )
                )
            continue
        for i, vecteur in zip(indexes, resultats, strict=True):
            vecteurs[i] = vecteur

    # Phase 3 : ecriture, element par element
    pris: set[str] = set()
    for i, (entree, reformulation, _) in enumerate(a_vectoriser):
        if i in echecs_lot:
            continue
        vecteur = vecteurs.get(i)
        if vecteur is None:
            rapports.append(
                RapportElement(
                    entree.titre_source,
                    False,
                    motif="vecteur manquant pour cet element",
                )
            )
            continue
        try:
            record = OutputRecord(
                entree=entree.texte,
                reformulation=reformulation,
                vecteur=vecteur,
                dimension_vecteur=modele.dimension,
                nature_vecteur=modele.nature,
            )
            titre = deriver_titre(entree.titre_source)
            chemin = resoudre_nom(titre, options.output_folder, pris)
            ecrire_sortie(record, chemin)
        except ValueError as err:
            rapports.append(RapportElement(entree.titre_source, False, motif=str(err)))
            continue
        rapports.append(RapportElement(entree.titre_source, True, fichier=str(chemin)))
    return rapports


def _afficher_bilan(
    rapports: list[RapportElement], echecs_arguments: list[str]
) -> None:
    for motif in echecs_arguments:
        print(f"Echec d'entree : {motif}", file=sys.stderr)
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
        f"{len(echecs_arguments)} entree(s) non resolue(s)"
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
        )
        cle_api = charger_cle_api()
    except ErreurConfiguration as err:
        print(f"Erreur de configuration : {err}", file=sys.stderr)
        return 1

    entrees, echecs_arguments = resoudre_arguments(args.entrees)
    if not entrees:
        for motif in echecs_arguments:
            print(f"Echec d'entree : {motif}", file=sys.stderr)
        print("Aucune entree exploitable.", file=sys.stderr)
        return 1

    client = (usine_client or ClientMistral)(cle_api)
    rapports = executer(entrees, options, client)
    _afficher_bilan(rapports, echecs_arguments)

    if any(not r.ok for r in rapports) or echecs_arguments:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
