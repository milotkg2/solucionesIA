"""Carga y ensamblado de los prompts del agente.

Los textos viven en la carpeta `prompts/` para que puedan revisarse y justificarse sin leer
codigo. Este modulo solo los lee y reemplaza los marcadores `{{consulta}}`, `{{hechos}}` y
`{{contexto}}`.
"""

from __future__ import annotations

from functools import lru_cache

from src.config import DIR_PROMPTS

PLANTILLA_DIAGNOSTICO = "diagnostico_envio.md"
PLANTILLA_POLITICAS = "consulta_politicas.md"
PROMPT_SISTEMA = "sistema_agente.md"


@lru_cache(maxsize=None)
def cargar_prompt(nombre: str) -> str:
    ruta = DIR_PROMPTS / nombre
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el prompt {ruta}")
    return ruta.read_text(encoding="utf-8").strip()


def _rellenar(plantilla: str, valores: dict[str, str]) -> str:
    # Se usa reemplazo literal en vez de str.format porque los fragmentos recuperados
    # pueden contener llaves que romperian el formateo.
    texto = plantilla
    for clave, valor in valores.items():
        texto = texto.replace("{{" + clave + "}}", valor)
    return texto


def prompt_sistema() -> str:
    return cargar_prompt(PROMPT_SISTEMA)


def prompt_diagnostico(consulta: str, hechos: str, contexto: str) -> str:
    return _rellenar(
        cargar_prompt(PLANTILLA_DIAGNOSTICO),
        {"consulta": consulta.strip(), "hechos": hechos.strip(), "contexto": contexto.strip()},
    )


def prompt_politicas(consulta: str, contexto: str) -> str:
    return _rellenar(
        cargar_prompt(PLANTILLA_POLITICAS),
        {"consulta": consulta.strip(), "contexto": contexto.strip()},
    )
