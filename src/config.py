"""Configuracion central del agente: rutas, parametros y fabricas de LLM y embeddings.

La capa de abstraccion del proveedor de LLM permite intercambiar el motor de generacion
sin tocar el resto del pipeline. Esto responde a una restriccion real del proyecto: el
equipo de desarrollo no dispone de GPU, por lo que un modelo local de 3B tarda del orden
de minutos por consulta, mientras que un modelo en la nube responde en segundos.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")

DIR_DATOS = RAIZ / "data"
DIR_INTERNOS = DIR_DATOS / "internos"
DIR_EXTERNOS = DIR_DATOS / "externos"
DIR_INDICE = DIR_DATOS / "vectorstore"
DIR_PROMPTS = RAIZ / "prompts"
DIR_EVIDENCIAS = RAIZ / "evidencias"

CSV_ENVIOS = DIR_INTERNOS / "envios.csv"
CSV_EVENTOS = DIR_INTERNOS / "eventos_tracking.csv"

# Fecha de referencia de la operacion simulada. Se fija para que las evidencias sean
# reproducibles: el calculo de retraso de un envio no entregado depende de "hoy".
FECHA_OPERACION = os.getenv("FECHA_OPERACION", "2026-09-23")


@dataclass(frozen=True)
class ParametrosRAG:
    """Parametros del pipeline de recuperacion."""

    tamano_chunk: int = int(os.getenv("RAG_TAMANO_CHUNK", "600"))
    solape_chunk: int = int(os.getenv("RAG_SOLAPE_CHUNK", "120"))
    top_k_vectorial: int = int(os.getenv("RAG_TOP_K_VECTORIAL", "6"))
    top_k_lexico: int = int(os.getenv("RAG_TOP_K_LEXICO", "6"))
    top_k_final: int = int(os.getenv("RAG_TOP_K_FINAL", "5"))


@dataclass(frozen=True)
class ConfigModelos:
    """Proveedores y modelos configurados por variables de entorno."""

    # groq = principal (capa gratuita, rapido). gemini y ollama quedan como respaldo.
    proveedor_llm: str = os.getenv("LLM_PROVEEDOR", "groq").lower()
    modelo_groq: str = os.getenv("GROQ_MODELO", "openai/gpt-oss-120b")
    modelo_gemini: str = os.getenv("GEMINI_MODELO", "gemini-3.6-flash")
    modelo_ollama: str = os.getenv("OLLAMA_MODELO", "llama3.2:3b")
    proveedor_embeddings: str = os.getenv("EMBEDDINGS_PROVEEDOR", "ollama").lower()
    modelo_embeddings_ollama: str = os.getenv("EMBEDDINGS_MODELO", "nomic-embed-text")
    url_ollama: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    temperatura: float = float(os.getenv("LLM_TEMPERATURA", "0.1"))
    timeout_segundos: float = float(os.getenv("LLM_TIMEOUT", "900"))
    clave_groq: str | None = field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    clave_gemini: str | None = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))


PARAMETROS_RAG = ParametrosRAG()
CONFIG_MODELOS = ConfigModelos()


class ConfiguracionInvalida(RuntimeError):
    """Error de configuracion recuperable, con mensaje orientado al usuario."""


def construir_llm(proveedor: str | None = None):
    """Devuelve el LLM segun el proveedor configurado.

    Proveedores soportados:
    - groq: nube, capa gratuita (motor principal tras el bloqueo de Gemini en la cuenta)
    - gemini: nube, capa gratuita (respaldo; puede fallar por permisos de cuenta/region)
    - ollama: local, sin red (respaldo offline; lento en equipos sin GPU)
    """
    proveedor = (proveedor or CONFIG_MODELOS.proveedor_llm).lower()

    if proveedor == "groq":
        if not CONFIG_MODELOS.clave_groq:
            raise ConfiguracionInvalida(
                "Falta GROQ_API_KEY en el archivo .env. Obten una clave gratuita en "
                "https://console.groq.com/keys (sin tarjeta de credito)."
            )
        from llama_index.llms.groq import Groq

        return Groq(
            model=CONFIG_MODELOS.modelo_groq,
            api_key=CONFIG_MODELOS.clave_groq,
            temperature=CONFIG_MODELOS.temperatura,
        )

    if proveedor == "gemini":
        if not CONFIG_MODELOS.clave_gemini:
            raise ConfiguracionInvalida(
                "Falta GOOGLE_API_KEY en el archivo .env. Obten una clave gratuita en "
                "https://aistudio.google.com/apikey o cambia a LLM_PROVEEDOR=groq."
            )
        from llama_index.llms.google_genai import GoogleGenAI

        return GoogleGenAI(
            model=CONFIG_MODELOS.modelo_gemini,
            api_key=CONFIG_MODELOS.clave_gemini,
            temperature=CONFIG_MODELOS.temperatura,
        )

    if proveedor == "ollama":
        from llama_index.llms.ollama import Ollama

        return Ollama(
            model=CONFIG_MODELOS.modelo_ollama,
            base_url=CONFIG_MODELOS.url_ollama,
            request_timeout=CONFIG_MODELOS.timeout_segundos,
            temperature=CONFIG_MODELOS.temperatura,
        )

    raise ConfiguracionInvalida(
        f"Proveedor de LLM no soportado: '{proveedor}'. Usa 'groq', 'gemini' u 'ollama'."
    )


def construir_embeddings():
    """Devuelve el modelo de embeddings.

    Por defecto se usa un modelo local via Ollama: la indexacion ocurre una sola vez y
    embeber una consulta toma alrededor de un segundo, por lo que la limitacion de
    hardware no afecta la experiencia de uso y el pipeline de recuperacion funciona sin
    conexion a internet.
    """
    if CONFIG_MODELOS.proveedor_embeddings == "ollama":
        from llama_index.embeddings.ollama import OllamaEmbedding

        return OllamaEmbedding(
            model_name=CONFIG_MODELOS.modelo_embeddings_ollama,
            base_url=CONFIG_MODELOS.url_ollama,
        )

    raise ConfiguracionInvalida(
        "Proveedor de embeddings no soportado: "
        f"'{CONFIG_MODELOS.proveedor_embeddings}'. Usa 'ollama'."
    )


def aplicar_settings_globales(cargar_llm: bool = True) -> None:
    """Registra LLM y embeddings en los Settings globales de LlamaIndex."""
    from llama_index.core import Settings

    Settings.embed_model = construir_embeddings()
    Settings.chunk_size = PARAMETROS_RAG.tamano_chunk
    Settings.chunk_overlap = PARAMETROS_RAG.solape_chunk
    if cargar_llm:
        Settings.llm = construir_llm()
