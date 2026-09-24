"""Recuperacion hibrida: busqueda densa (embeddings) + busqueda lexica (BM25) con fusion RRF.

Justificacion de la estrategia hibrida:

- El corpus contiene muchos identificadores literales (codigos de motivo como `M02`, de
  documento como `SOP-OPS-014` o de servicio como `ND`). La busqueda densa tiende a diluir
  estos tokens; BM25 los recupera de forma exacta.
- A la inversa, las consultas de los operadores rara vez usan el vocabulario del manual
  ("me devuelven la plata del despacho" frente a "reembolso del costo de despacho"), caso
  en que la busqueda densa supera a la lexica.

La fusion se implementa de forma explicita con Reciprocal Rank Fusion en lugar de delegarla
a un componente cerrado, para poder mostrar en la interfaz el aporte de cada recuperador y
para que el modulo no dependa del LLM.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import Stemmer
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore
from llama_index.retrievers.bm25 import BM25Retriever

from src.config import PARAMETROS_RAG
from src.ingest import cargar_indice

# Constante de amortiguacion de Reciprocal Rank Fusion. El valor 60 es el propuesto en la
# formulacion original y evita que el primer resultado de un recuperador domine la fusion.
K_RRF = 60


@dataclass
class FragmentoRecuperado:
    """Fragmento recuperado con su trazabilidad completa, usada como evidencia."""

    documento: str
    titulo: str
    seccion: str
    tipo_fuente: str
    texto: str
    score_rrf: float
    rank_vectorial: int | None = None
    rank_lexico: int | None = None
    score_vectorial: float | None = None
    score_lexico: float | None = None

    @property
    def referencia(self) -> str:
        """Etiqueta de citacion que el LLM debe reproducir en su respuesta."""
        return f"{self.documento} — {self.seccion}"

    @property
    def recuperado_por(self) -> str:
        """Indica cual de los dos recuperadores encontro el fragmento."""
        if self.rank_vectorial is not None and self.rank_lexico is not None:
            return "ambos"
        if self.rank_vectorial is not None:
            return "vectorial"
        return "lexico"


class RecuperadorHibrido:
    """Combina un recuperador vectorial y uno lexico sobre el mismo conjunto de fragmentos."""

    def __init__(self, indice: VectorStoreIndex | None = None) -> None:
        self._indice = indice or cargar_indice()
        self._vectorial = self._indice.as_retriever(
            similarity_top_k=PARAMETROS_RAG.top_k_vectorial
        )
        self._lexico = BM25Retriever.from_defaults(
            docstore=self._indice.docstore,
            similarity_top_k=PARAMETROS_RAG.top_k_lexico,
            stemmer=Stemmer.Stemmer("spanish"),
            language="spanish",
        )

    def recuperar(
        self,
        consulta: str,
        top_k: int | None = None,
        tipo_fuente: str | None = None,
    ) -> list[FragmentoRecuperado]:
        """Recupera fragmentos relevantes y los devuelve ordenados por score fusionado.

        `tipo_fuente` permite restringir la busqueda a fuentes 'interna' o 'externa'.
        """
        top_k = top_k or PARAMETROS_RAG.top_k_final

        resultados_vectoriales = self._vectorial.retrieve(consulta)
        resultados_lexicos = self._lexico.retrieve(consulta)

        fragmentos = self._fusionar(resultados_vectoriales, resultados_lexicos)

        if tipo_fuente:
            fragmentos = [f for f in fragmentos if f.tipo_fuente == tipo_fuente]

        return fragmentos[:top_k]

    def _fusionar(
        self,
        vectoriales: list[NodeWithScore],
        lexicos: list[NodeWithScore],
    ) -> list[FragmentoRecuperado]:
        """Aplica Reciprocal Rank Fusion: score(d) = suma de 1 / (K + rank(d)) por recuperador."""
        acumulado: dict[str, FragmentoRecuperado] = {}

        for origen, resultados in (("vectorial", vectoriales), ("lexico", lexicos)):
            for posicion, resultado in enumerate(resultados, start=1):
                clave = resultado.node.node_id
                fragmento = acumulado.get(clave)
                if fragmento is None:
                    metadatos = resultado.node.metadata
                    fragmento = FragmentoRecuperado(
                        documento=metadatos.get("documento", "desconocido"),
                        titulo=metadatos.get("titulo", ""),
                        seccion=metadatos.get("seccion", ""),
                        tipo_fuente=metadatos.get("tipo_fuente", ""),
                        texto=resultado.node.get_content(),
                        score_rrf=0.0,
                    )
                    acumulado[clave] = fragmento

                fragmento.score_rrf += 1.0 / (K_RRF + posicion)
                if origen == "vectorial":
                    fragmento.rank_vectorial = posicion
                    fragmento.score_vectorial = resultado.score
                else:
                    fragmento.rank_lexico = posicion
                    fragmento.score_lexico = resultado.score

        return sorted(acumulado.values(), key=lambda f: f.score_rrf, reverse=True)


def formatear_contexto(fragmentos: list[FragmentoRecuperado]) -> str:
    """Arma el bloque de contexto que se inyecta en el prompt, con etiquetas citables."""
    if not fragmentos:
        return "(sin fragmentos recuperados)"

    bloques = []
    for indice, fragmento in enumerate(fragmentos, start=1):
        bloques.append(
            f"[F{indice}] Fuente {fragmento.tipo_fuente} | {fragmento.referencia}\n"
            f"{fragmento.texto.strip()}"
        )
    return "\n\n".join(bloques)


@lru_cache(maxsize=1)
def obtener_recuperador() -> RecuperadorHibrido:
    """Devuelve una instancia reutilizable; construirla implica cargar el indice."""
    return RecuperadorHibrido()


if __name__ == "__main__":
    import sys

    consulta_cli = " ".join(sys.argv[1:]) or "cuantos reintentos permite el motivo M02"
    recuperador = obtener_recuperador()
    for numero, item in enumerate(recuperador.recuperar(consulta_cli), start=1):
        print(
            f"{numero}. [{item.recuperado_por}] rrf={item.score_rrf:.4f} "
            f"vec={item.rank_vectorial} bm25={item.rank_lexico} | {item.referencia}"
        )
