"""Construccion del indice RAG: carga de fuentes, segmentacion, embeddings y persistencia.

Decision de diseno relevante: solo se indexan las fuentes *textuales* (procedimientos,
politicas, matriz de SLA, catalogo de motivos, normativa y evidencia publica). Los datos
estructurados de envios (`envios.csv` y `eventos_tracking.csv`) NO se indexan: se consultan
de forma determinista mediante la herramienta de tracking. Embeber filas de una tabla
degrada la recuperacion y expone el sistema a errores de calculo del LLM.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from llama_index.core import Document, StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.schema import BaseNode

from src.config import (
    DIR_EXTERNOS,
    DIR_INDICE,
    DIR_INTERNOS,
    PARAMETROS_RAG,
    aplicar_settings_globales,
)

PATRON_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _leer_frontmatter(texto: str) -> tuple[dict[str, str], str]:
    """Extrae los metadatos YAML simples de la cabecera y devuelve el cuerpo restante."""
    coincidencia = PATRON_FRONTMATTER.match(texto)
    if not coincidencia:
        return {}, texto

    metadatos: dict[str, str] = {}
    for linea in coincidencia.group(1).splitlines():
        if ":" not in linea:
            continue
        clave, valor = linea.split(":", 1)
        metadatos[clave.strip()] = valor.strip()
    return metadatos, texto[coincidencia.end() :]


def cargar_documentos() -> list[Document]:
    """Carga las fuentes internas y externas como documentos con metadatos de citacion."""
    documentos: list[Document] = []

    for directorio, tipo_fuente in ((DIR_INTERNOS, "interna"), (DIR_EXTERNOS, "externa")):
        for ruta in sorted(directorio.glob("*.md")):
            texto = ruta.read_text(encoding="utf-8")
            metadatos, cuerpo = _leer_frontmatter(texto)
            documentos.append(
                Document(
                    text=cuerpo,
                    metadata={
                        "documento": metadatos.get("documento", ruta.stem),
                        "titulo": metadatos.get("titulo", ruta.stem),
                        "tipo_fuente": tipo_fuente,
                        "entidad": metadatos.get("entidad", "LogiRuta SpA"),
                        "vigencia": metadatos.get("vigencia", metadatos.get("fecha_recopilacion", "")),
                        "archivo": ruta.name,
                    },
                )
            )

    if not documentos:
        raise FileNotFoundError(
            f"No se encontraron documentos .md en {DIR_INTERNOS} ni {DIR_EXTERNOS}."
        )
    return documentos


def segmentar(documentos: list[Document]) -> list[BaseNode]:
    """Segmenta en dos etapas: primero por estructura Markdown, luego por tamano.

    La primera etapa respeta los encabezados, de modo que cada fragmento pertenece a una
    seccion identificable y la respuesta puede citar 'documento + seccion'. La segunda
    etapa acota los fragmentos demasiado largos para que quepan varios en el contexto.
    """
    parser_markdown = MarkdownNodeParser()
    parser_tamano = SentenceSplitter(
        chunk_size=PARAMETROS_RAG.tamano_chunk,
        chunk_overlap=PARAMETROS_RAG.solape_chunk,
    )

    nodos_por_seccion = parser_markdown.get_nodes_from_documents(documentos)

    # La seccion se resuelve antes del corte por tamano para que los fragmentos de
    # continuacion hereden la seccion a la que pertenecen y la citacion siga siendo exacta.
    for nodo in nodos_por_seccion:
        nodo.metadata["seccion"] = _resolver_seccion(nodo)

    nodos = parser_tamano.get_nodes_from_documents(nodos_por_seccion)

    for nodo in nodos:
        nodo.metadata.pop("header_path", None)
        nodo.excluded_embed_metadata_keys = ["archivo", "vigencia", "entidad"]
        nodo.excluded_llm_metadata_keys = ["archivo"]
    return nodos


PATRON_ENCABEZADO = re.compile(r"^\s{0,3}#{1,6}\s+(?P<titulo>.+?)\s*$")


def _resolver_seccion(nodo: BaseNode) -> str:
    """Determina la seccion de un nodo a partir de su encabezado o de su ruta de encabezados."""
    for linea in nodo.get_content().splitlines():
        if not linea.strip():
            continue
        coincidencia = PATRON_ENCABEZADO.match(linea)
        return coincidencia.group("titulo") if coincidencia else _seccion_padre(nodo)
    return _seccion_padre(nodo)


def _seccion_padre(nodo: BaseNode) -> str:
    """Usa el ultimo nivel de `header_path` cuando el fragmento no inicia con encabezado."""
    ruta = nodo.metadata.get("header_path", "/").strip("/")
    return ruta.split("/")[-1].strip() if ruta else "Documento completo"


def construir_indice(reconstruir: bool = False) -> VectorStoreIndex:
    """Crea el indice vectorial y lo persiste en disco."""
    aplicar_settings_globales(cargar_llm=False)

    if reconstruir and DIR_INDICE.exists():
        shutil.rmtree(DIR_INDICE)

    documentos = cargar_documentos()
    nodos = segmentar(documentos)

    indice = VectorStoreIndex(nodos, show_progress=True)
    DIR_INDICE.mkdir(parents=True, exist_ok=True)
    indice.storage_context.persist(persist_dir=str(DIR_INDICE))

    _escribir_resumen(documentos, nodos, DIR_INDICE / "resumen_indice.md")
    return indice


def cargar_indice() -> VectorStoreIndex:
    """Carga el indice persistido; lo construye si aun no existe."""
    if not (DIR_INDICE / "docstore.json").exists():
        return construir_indice()

    aplicar_settings_globales(cargar_llm=False)
    contexto = StorageContext.from_defaults(persist_dir=str(DIR_INDICE))
    return load_index_from_storage(contexto)


def _escribir_resumen(documentos: list[Document], nodos: list[BaseNode], destino: Path) -> None:
    """Deja constancia de la composicion del indice, util como evidencia de la ingesta."""
    conteo: dict[str, int] = {}
    for nodo in nodos:
        conteo[nodo.metadata["documento"]] = conteo.get(nodo.metadata["documento"], 0) + 1

    lineas = [
        "# Composicion del indice RAG",
        "",
        f"- Documentos indexados: {len(documentos)}",
        f"- Fragmentos generados: {len(nodos)}",
        f"- Tamano de fragmento: {PARAMETROS_RAG.tamano_chunk} tokens",
        f"- Solape: {PARAMETROS_RAG.solape_chunk} tokens",
        "",
        "| Documento | Tipo de fuente | Fragmentos |",
        "|---|---|---|",
    ]
    for documento in documentos:
        clave = documento.metadata["documento"]
        lineas.append(
            f"| {clave} | {documento.metadata['tipo_fuente']} | {conteo.get(clave, 0)} |"
        )
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse

    analizador = argparse.ArgumentParser(description="Construye el indice RAG de LogiRuta.")
    analizador.add_argument(
        "--reconstruir",
        action="store_true",
        help="Elimina el indice existente antes de construirlo de nuevo.",
    )
    argumentos = analizador.parse_args()

    indice_creado = construir_indice(reconstruir=argumentos.reconstruir)
    total = len(indice_creado.docstore.docs)
    print(f"Indice construido con {total} fragmentos en {DIR_INDICE}")
