"""Enveloppe fine et injectable du SDK mistralai."""

from __future__ import annotations

from mistralai.client import Mistral


class ClientMistral:
    """Enveloppe du SDK officiel : aucune logique metier ici.

    Toute la logique (batching, retry, nommage) vit dans les autres
    modules ; les tests remplacent cette classe par un fictif.
    """

    def __init__(self, cle_api: str) -> None:
        self._client = Mistral(api_key=cle_api)

    def embedder(self, nom_modele: str, textes: list[str]) -> list[list[float]]:
        """Vectorise un lot de textes en une requete (FR-004)."""
        reponse = self._client.embeddings.create(
            model=nom_modele,
            inputs=textes,
        )
        return [element.embedding for element in reponse.data]

    def discuter(self, nom_modele: str, prompt: str, temperature: float) -> str:
        """Appelle le LLM en mode JSON strict et retourne le texte."""
        reponse = self._client.chat.complete(
            model=nom_modele,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        contenu = reponse.choices[0].message.content
        return contenu if contenu is not None else ""
