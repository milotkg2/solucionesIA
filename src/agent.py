"""Agente orquestador de la Mesa de Control.

Flujo (sigue el orden del SOP-OPS-014 §5: identificar, clasificar, verificar SLA, decidir,
comunicar):

1. Detecta si la consulta menciona un codigo de envio.
2. Si lo hay, invoca la herramienta de tracking y obtiene hechos calculados en codigo.
   Si el envio no existe, responde sin llamar al LLM: no hay nada que diagnosticar y
   cualquier respuesta generada seria inventada.
3. Construye consultas de recuperacion dirigidas, una por aspecto del caso (motivo,
   intentos, accion, compensacion, SLA, escalamiento, temporada), y fusiona los resultados.
   Una sola consulta con la pregunta del usuario no trae todas las reglas necesarias
   (ver evidencias/01: faltaba la regla de intentos).
4. Ensambla el prompt (sistema + plantilla) y llama al LLM.
5. Devuelve la respuesta con toda la trazabilidad para la interfaz y las evidencias.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

from llama_index.core.llms import ChatMessage

from src.config import CONFIG_MODELOS, construir_llm
from src.prompts import prompt_diagnostico, prompt_politicas, prompt_sistema
from src.retrieval import FragmentoRecuperado, formatear_contexto, obtener_recuperador
from src.tracking import HechosEnvio, consultar_envio, detectar_codigo, formatear_hechos

MAX_FRAGMENTOS = 8
FRAGMENTOS_POR_ASPECTO = 3

# Aspectos que se buscan solo en fuentes externas, para garantizar que la normativa llegue
# al contexto aunque las fuentes internas obtengan mejor puntaje.
ASPECTOS_EXTERNOS = {"normativa"}

# Algunos modelos citan con corchetes de ancho completo; se normalizan a [F#].
PATRON_CITA_ANCHA = re.compile(r"【\s*(F\d+)\s*】")
REINTENTOS_LLM = 2
ESPERA_REINTENTO_S = 30

TRAMOS_LEGIBLES = {
    "sin_retraso": "sin retraso",
    "hasta_24h": "retraso hasta 24 horas",
    "mas_de_24h_hasta_72h": "retraso mas de 24 horas y hasta 72 horas",
    "mas_de_72h_hasta_5_dias": "retraso mas de 72 horas y hasta 5 dias",
    "mas_de_5_dias": "retraso mas de 5 dias",
}

# Motivos en que el numero de intentos determina la accion (CAT-OPS-007 / SOP-OPS-014 §4).
MOTIVOS_CON_REINTENTOS = {"M02", "M03", "M05", "M06"}


@dataclass
class ResultadoAgente:
    consulta: str
    tipo: str  # diagnostico | politicas | envio_no_encontrado | error
    respuesta: str = ""
    hechos: HechosEnvio | None = None
    consultas_rag: dict[str, str] = field(default_factory=dict)
    fragmentos: list[FragmentoRecuperado] = field(default_factory=list)
    prompt_usuario: str = ""
    proveedor: str = CONFIG_MODELOS.proveedor_llm
    latencia_recuperacion_s: float = 0.0
    latencia_llm_s: float = 0.0
    error: str | None = None


def construir_consultas_dirigidas(hechos: HechosEnvio) -> dict[str, str]:
    """Traduce los hechos del envio a consultas de recuperacion, una por aspecto."""
    tramo = TRAMOS_LEGIBLES.get(hechos.tramo_retraso or "", "retraso")
    motivo = hechos.motivo_falla or ""
    consultas: dict[str, str] = {}

    if motivo:
        consultas["motivo"] = (
            f"{motivo} {hechos.motivo_nombre} responsabilidad computa SLA compensacion"
        )
    if motivo in MOTIVOS_CON_REINTENTOS or hechos.intentos_entrega > 0:
        consultas["intentos"] = (
            f"regla de intentos de entrega intentos maximos plazo entre intentos "
            f"{hechos.motivo_nombre or ''} devolucion al origen"
        )
    consultas["accion"] = f"matriz de decision accion operativa {tramo} causa atribuible"
    if hechos.hay_retraso_confirmado and hechos.compensacion_posible:
        consultas["compensacion"] = (
            f"tabla de compensaciones al consumidor {tramo} causa atribuible a LogiRuta aprobacion"
        )
    if hechos.computa_sla is False:
        # Evita traer umbrales de incidente que no aplican y que confunden al modelo.
        consultas["sla"] = (
            f"exclusiones de responsabilidad no se computan como incumplimiento de SLA "
            f"{hechos.motivo_nombre or ''}"
        )
    else:
        consultas["sla"] = (
            f"matriz contractual {hechos.retailer} servicio {hechos.servicio} plazo de "
            f"respuesta penalizacion incidente de SLA"
        )
    if (hechos.dias_retraso or 0) > 2 and hechos.computa_sla is not False:
        consultas["escalamiento"] = (
            "escalamiento nivel jefe de hub jefe de operaciones retraso mayor a 72 horas "
            "atribuible a LogiRuta"
        )
    if hechos.temporada.upper() == "ALTA":
        consultas["temporada"] = (
            "protocolo de peaks temporada alta extension de plazo informado al consumidor "
            "condiciones ofrecidas fecha promesa exigible"
        )
    if motivo == "M07":
        consultas["siniestro"] = "paquete perdido danado cobertura valor declarado 15 UF siniestro"
    if hechos.temporada.upper() == "ALTA" or (hechos.dias_retraso or 0) > 3:
        consultas["normativa"] = (
            "plazo de entrega informado al consumidor condiciones ofrecidas deben respetarse "
            "modificacion unilateral reclamo SERNAC"
        )
    return consultas


def _recuperar_por_aspectos(consultas: dict[str, str]) -> list[FragmentoRecuperado]:
    """Recupera por aspecto y fusiona sin duplicados, respetando el orden de los aspectos."""
    recuperador = obtener_recuperador()
    candidatos = {
        aspecto: recuperador.recuperar(
            consulta,
            top_k=FRAGMENTOS_POR_ASPECTO,
            tipo_fuente="externa" if aspecto in ASPECTOS_EXTERNOS else None,
        )
        for aspecto, consulta in consultas.items()
    }

    vistos: set[str] = set()
    seleccion: list[FragmentoRecuperado] = []

    # Primera pasada: el mejor fragmento nuevo de cada aspecto, para que todos los aspectos
    # queden representados. Pasadas siguientes: completar el cupo con los restantes.
    for posicion in range(FRAGMENTOS_POR_ASPECTO):
        for aspecto, fragmentos in candidatos.items():
            if posicion >= len(fragmentos):
                continue
            fragmento = fragmentos[posicion]
            clave = fragmento.texto.strip()[:200]
            if clave in vistos:
                continue
            vistos.add(clave)
            fragmento.aspecto = aspecto
            seleccion.append(fragmento)
            if len(seleccion) >= MAX_FRAGMENTOS:
                return seleccion
    return seleccion


def _llamar_llm(prompt_usuario: str) -> str:
    """Llama al LLM con reintento ante limites de cuota de la capa gratuita."""
    mensajes = [
        ChatMessage(role="system", content=prompt_sistema()),
        ChatMessage(role="user", content=prompt_usuario),
    ]
    llm = construir_llm()
    for intento in range(REINTENTOS_LLM + 1):
        try:
            texto = llm.chat(mensajes).message.content.strip()
            return PATRON_CITA_ANCHA.sub(r"[\1]", texto)
        except Exception as error:  # noqa: BLE001 - se reintenta solo por cuota
            limite_cuota = "429" in str(error) or "rate" in str(error).lower()
            if not limite_cuota or intento == REINTENTOS_LLM:
                raise
            time.sleep(ESPERA_REINTENTO_S)
    raise RuntimeError("No se obtuvo respuesta del LLM")


def responder(consulta: str) -> ResultadoAgente:
    """Punto de entrada del agente."""
    consulta = (consulta or "").strip()
    codigo = detectar_codigo(consulta)
    resultado = ResultadoAgente(consulta=consulta, tipo="politicas")

    inicio = time.perf_counter()
    if codigo:
        hechos = consultar_envio(codigo)
        resultado.hechos = hechos
        if not hechos.encontrado:
            resultado.tipo = "envio_no_encontrado"
            resultado.respuesta = (
                f"No encontre el envio **{codigo}** en los registros de tracking. "
                "Verifica el codigo con el cliente o el retailer antes de continuar. "
                "No se genero diagnostico para evitar una respuesta sin respaldo en datos."
            )
            return resultado

        resultado.tipo = "diagnostico"
        resultado.consultas_rag = construir_consultas_dirigidas(hechos)
        resultado.fragmentos = _recuperar_por_aspectos(resultado.consultas_rag)
        resultado.prompt_usuario = prompt_diagnostico(
            consulta, formatear_hechos(hechos), formatear_contexto(resultado.fragmentos)
        )
    else:
        resultado.consultas_rag = {"consulta": consulta}
        resultado.fragmentos = obtener_recuperador().recuperar(consulta)
        for fragmento in resultado.fragmentos:
            fragmento.aspecto = "consulta"
        resultado.prompt_usuario = prompt_politicas(
            consulta, formatear_contexto(resultado.fragmentos)
        )
    resultado.latencia_recuperacion_s = round(time.perf_counter() - inicio, 2)

    inicio_llm = time.perf_counter()
    try:
        resultado.respuesta = _llamar_llm(resultado.prompt_usuario)
    except Exception as error:  # noqa: BLE001 - se informa al usuario sin romper la UI
        resultado.tipo = "error"
        resultado.error = f"{type(error).__name__}: {error}"
        resultado.respuesta = (
            "No fue posible generar la respuesta con el modelo de lenguaje. "
            f"Detalle tecnico: {resultado.error}"
        )
    resultado.latencia_llm_s = round(time.perf_counter() - inicio_llm, 2)
    return resultado


if __name__ == "__main__":
    import sys

    texto = " ".join(sys.argv[1:]) or "El cliente del envio LR-2026-004182 reclama. Que hago?"
    salida = responder(texto)
    print(f"Tipo: {salida.tipo} | recuperacion {salida.latencia_recuperacion_s}s "
          f"| LLM {salida.latencia_llm_s}s")
    for numero, frag in enumerate(salida.fragmentos, start=1):
        print(f"[F{numero}] ({frag.aspecto}) {frag.referencia}")
    print()
    print(salida.respuesta)
