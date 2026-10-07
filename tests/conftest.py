"""Fixtures communes aux tests de Question2Vector.

Aucun test n'accede au reseau : le client Mistral est toujours
remplace par un client fictif.
"""

from __future__ import annotations

import pytest


def usine(client):
    """Retourne une usine de client qui ignore la cle API."""

    def creer(_cle):
        return client

    return creer


class ClientFictif:
    """Client d'API fictif : enregistre les appels, ne sort jamais."""

    def __init__(
        self,
        dimension: int = 1024,
        reponse_llm: str | None = None,
        echec_embedding=None,
        echec_chat=None,
    ) -> None:
        self.dimension = dimension
        self.reponse_llm = reponse_llm
        self.echec_embedding = echec_embedding
        self.echec_chat = echec_chat
        self.appels_embedding: list[tuple[str, list[str]]] = []
        self.appels_chat: list[tuple[str, str, float]] = []

    def embedder(self, nom_modele: str, textes: list[str]) -> list[list[float]]:
        self.appels_embedding.append((nom_modele, list(textes)))
        if self.echec_embedding is not None:
            self.echec_embedding()
        return [[float(i) for i in range(self.dimension)] for _ in textes]

    def discuter(self, nom_modele: str, prompt: str, temperature: float) -> str:
        self.appels_chat.append((nom_modele, prompt, temperature))
        if self.echec_chat is not None:
            self.echec_chat()
        if self.reponse_llm is None:
            raise AssertionError("appel LLM inattendu dans ce test")
        return self.reponse_llm


@pytest.fixture
def fabrique_client():
    """Fabrique un ClientFictif configure par le test."""

    def creer(
        dimension: int = 1024,
        reponse_llm: str | None = None,
        echec_embedding=None,
        echec_chat=None,
    ) -> ClientFictif:
        return ClientFictif(
            dimension=dimension,
            reponse_llm=reponse_llm,
            echec_embedding=echec_embedding,
            echec_chat=echec_chat,
        )

    return creer


@pytest.fixture
def cle_test(monkeypatch):
    """Fournit une cle API fictive ; interdit toute fuite reelle."""
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test-sans-effet")
    return "cle-de-test-sans-effet"
