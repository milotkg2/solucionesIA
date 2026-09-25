"""Ejecucion de escenarios de prueba y generacion de evidencias.

Cada escenario define la consulta y las verificaciones que la respuesta debe cumplir segun
las politicas (SOP-OPS-014, SLA-COM-002, POL-COM-003, CAT-OPS-007, EXT-NORM-002). Las
verificaciones son automaticas por patrones de texto y por fragmentos recuperados; son un
apoyo a la revision humana, no un reemplazo.

Uso:
    python -m src.evaluar                 # todos los escenarios
    python -m src.evaluar --escenario ESC-02
"""

from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from src.agent import ResultadoAgente, responder
from src.config import CONFIG_MODELOS, DIR_EVIDENCIAS

DIR_SALIDA = DIR_EVIDENCIAS / "escenarios"
PAUSA_ENTRE_ESCENARIOS_S = 15


def normalizar(texto: str) -> str:
    """Minusculas y sin tildes, para que los patrones no dependan de la redaccion."""
    sin_tildes = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return sin_tildes.lower()


@dataclass
class Verificacion:
    descripcion: str
    evaluar: Callable[[ResultadoAgente], bool]


def en_respuesta(patron: str) -> Callable[[ResultadoAgente], bool]:
    return lambda r: re.search(patron, normalizar(r.respuesta)) is not None


def fragmento_recuperado(documento: str, seccion_contiene: str = "") -> Callable[[ResultadoAgente], bool]:
    return lambda r: any(
        f.documento == documento and seccion_contiene.lower() in f.seccion.lower()
        for f in r.fragmentos
    )


def tiene_citas(r: ResultadoAgente) -> bool:
    return re.search(r"\[F\d+\]", r.respuesta) is not None


NO_COMPENSACION = r"no corresponde (ninguna )?compensacion|sin compensacion|no procede (la )?compensacion|no aplica compensacion"

VERIFICACIONES_DIAGNOSTICO = [
    Verificacion("Incluye citas [F#] (objetivo O2)", tiene_citas),
    Verificacion("Incluye mensaje sugerido para el cliente", en_respuesta(r"mensaje sugerido")),
]


@dataclass
class Escenario:
    id: str
    titulo: str
    consulta: str
    objetivo: str
    verificaciones: list[Verificacion] = field(default_factory=list)


ESCENARIOS: list[Escenario] = [
    Escenario(
        id="ESC-01",
        titulo="Retraso por congestion en temporada alta (M01)",
        consulta="El cliente del envio LR-2026-004182 reclama que su pedido no ha llegado. Que le respondo y que corresponde hacer?",
        objetivo="Causa atribuible a LogiRuta con mas de 5 dias: escalamiento y compensacion mayor.",
        verificaciones=VERIFICACIONES_DIAGNOSTICO + [
            Verificacion("Atribuye la responsabilidad a LogiRuta", en_respuesta(r"logiruta")),
            Verificacion("Escala a Jefe de Operaciones o Gerencia", en_respuesta(r"jefe de operaciones|\bn3\b|gerencia comercial|\bn4\b")),
            Verificacion("Aplica compensacion del tramo (reembolso o reposicion)", en_respuesta(r"reembolso|reposicion")),
            Verificacion("Recupera la politica de compensaciones POL-COM-003", fragmento_recuperado("POL-COM-003")),
        ],
    ),
    Escenario(
        id="ESC-02",
        titulo="Cliente ausente con dos intentos fallidos (M02)",
        consulta="El cliente del envio LR-2026-005271 reclama que no le ha llegado y pide compensacion. Que hago?",
        objetivo="Causa atribuible al consumidor: sin compensacion, queda un intento.",
        verificaciones=VERIFICACIONES_DIAGNOSTICO + [
            Verificacion("Indica que no corresponde compensacion", en_respuesta(NO_COMPENSACION)),
            Verificacion("Indica el intento restante", en_respuesta(r"1 intento|un intento|tercer intento|queda")),
            Verificacion("Recupera la regla de intentos (SOP-OPS-014 §4)", fragmento_recuperado("SOP-OPS-014", "Regla de intentos")),
        ],
    ),
    Escenario(
        id="ESC-03",
        titulo="Direccion incompleta (M03)",
        consulta="Que hacemos con el envio LR-2026-006123? El transportista dice que no encuentra la direccion.",
        objetivo="Validar direccion con el cliente en 48 horas, sin compensacion, RTO si no responde.",
        verificaciones=VERIFICACIONES_DIAGNOSTICO + [
            Verificacion("Pide validar la direccion con el cliente", en_respuesta(r"(validar|confirmar|verificar)[^.]{0,40}direccion")),
            Verificacion("Menciona el plazo de 48 horas", en_respuesta(r"48")),
            Verificacion("Menciona devolucion al origen si no responde", en_respuesta(r"devolucion|\brto\b")),
            Verificacion("Indica que no corresponde compensacion", en_respuesta(NO_COMPENSACION)),
        ],
    ),
    Escenario(
        id="ESC-04",
        titulo="Quiebre de capacidad del hub, retailer Tier 1 same day (M04)",
        consulta="ElectroMax nos pregunta por el envio LR-2026-007334, era same day y sigue en el hub. Que corresponde?",
        objetivo="Causa LogiRuta, SLA Tier 1 con penalizacion, escalamiento y compensacion.",
        verificaciones=VERIFICACIONES_DIAGNOSTICO + [
            Verificacion("Atribuye la responsabilidad a LogiRuta", en_respuesta(r"logiruta")),
            Verificacion("Escala a Jefe de Operaciones o Gerencia", en_respuesta(r"jefe de operaciones|\bn3\b|gerencia comercial|\bn4\b")),
            Verificacion("Aplica compensacion", en_respuesta(r"reembolso|reposicion|cupon")),
            Verificacion("Advierte riesgo de penalizacion contractual", en_respuesta(r"penalizacion")),
        ],
    ),
    Escenario(
        id="ESC-05",
        titulo="Temporada alta sin plazo extendido informado (fuente externa decisiva)",
        consulta="DecoCasa dice que el envio LR-2026-008455 llego un dia tarde pero que en temporada alta el plazo se extiende. Tienen razon?",
        objetivo="La extension no es valida porque no se informo al consumidor: rige la fecha promesa original.",
        verificaciones=VERIFICACIONES_DIAGNOSTICO + [
            Verificacion(
                "Concluye que la extension no aplica por no haberse informado",
                en_respuesta(r"no (fue|se) informad|no se informo|no es valida|no aplica[^.]{0,30}extension|fecha promesa original|no informad"),
            ),
            Verificacion("Recupera el protocolo de peaks (SLA-COM-002 §6)", fragmento_recuperado("SLA-COM-002", "peaks")),
            Verificacion("Recupera al menos una fuente externa (normativa)", lambda r: any(f.tipo_fuente == "externa" for f in r.fragmentos)),
            Verificacion("Tramo hasta 24 h: disculpa sin compensacion economica", en_respuesta(r"disculpa|sin compensacion economica")),
        ],
    ),
    Escenario(
        id="ESC-06",
        titulo="Consulta general de politicas (sin envio)",
        consulta="Cuantos intentos de entrega permite el procedimiento cuando el cliente esta ausente y corresponde compensacion?",
        objetivo="Responder con RAG puro: 3 intentos, sin compensacion.",
        verificaciones=[
            Verificacion("Incluye citas [F#] (objetivo O2)", tiene_citas),
            Verificacion("Indica 3 intentos", en_respuesta(r"\b3 intentos|tres intentos|3\)|maximo de 3|hasta 3")),
            Verificacion("Indica que no corresponde compensacion", en_respuesta(NO_COMPENSACION + r"|compensacion: no")),
        ],
    ),
    Escenario(
        id="ESC-07",
        titulo="Codigo de envio inexistente (control de alucinacion)",
        consulta="El cliente del envio LR-2026-999999 esta molesto porque no le llega. Que le digo?",
        objetivo="No inventar un diagnostico: el agente responde sin llamar al LLM.",
        verificaciones=[
            Verificacion("Detecta que el envio no existe", lambda r: r.tipo == "envio_no_encontrado"),
            Verificacion("No llama al LLM", lambda r: r.latencia_llm_s == 0.0),
        ],
    ),
]


def _fila_fragmento(indice: int, f) -> str:
    return (
        f"| F{indice} | {f.aspecto or '-'} | {f.documento} — {f.seccion} | {f.tipo_fuente} | "
        f"{f.rank_vectorial or '-'} | {f.rank_lexico or '-'} | {f.score_rrf:.4f} |"
    )


def escribir_evidencia(escenario: Escenario, resultado: ResultadoAgente, checks: list[tuple[str, bool]]) -> str:
    nombre = f"{escenario.id}.md"
    lineas = [
        f"# {escenario.id} — {escenario.titulo}",
        "",
        f"- **Fecha de ejecucion:** {datetime.now():%Y-%m-%d %H:%M}",
        f"- **Motor LLM:** {CONFIG_MODELOS.proveedor_llm} `{CONFIG_MODELOS.modelo_groq if CONFIG_MODELOS.proveedor_llm == 'groq' else ''}`",
        f"- **Tipo de flujo:** {resultado.tipo}",
        f"- **Latencia:** recuperacion {resultado.latencia_recuperacion_s} s · LLM {resultado.latencia_llm_s} s",
        f"- **Resultado esperado:** {escenario.objetivo}",
        "",
        "## 1. Consulta del usuario",
        "",
        f"> {escenario.consulta}",
        "",
    ]

    if resultado.hechos is not None and resultado.hechos.encontrado:
        h = resultado.hechos
        lineas += [
            "## 2. Hechos calculados por la herramienta de tracking (sin LLM)",
            "",
            "| Campo | Valor |",
            "|---|---|",
            f"| Retailer / servicio | {h.retailer} / {h.servicio} |",
            f"| Fecha promesa / entrega real | {h.fecha_promesa} / {h.fecha_entrega_real or 'pendiente'} |",
            f"| Estado / intentos | {h.estado} / {h.intentos_entrega} |",
            f"| Motivo | {h.motivo_falla} — {h.motivo_nombre} |",
            f"| Responsable / computa SLA | {h.responsable} / {h.computa_sla} |",
            f"| Dias de retraso / tramo | {h.dias_retraso} / {h.tramo_retraso} |",
            f"| Temporada / plazo extendido informado | {h.temporada} / {h.plazo_extendido_informado} |",
            "",
        ]
    else:
        lineas += ["## 2. Hechos del envio", "", "No aplica o envio no encontrado.", ""]

    if resultado.consultas_rag:
        lineas += ["## 3. Consultas de recuperacion generadas por el agente", "", "| Aspecto | Consulta |", "|---|---|"]
        lineas += [f"| {a} | {c} |" for a, c in resultado.consultas_rag.items()]
        lineas.append("")

    if resultado.fragmentos:
        lineas += [
            "## 4. Fragmentos recuperados (RAG hibrido)",
            "",
            "| Etiqueta | Aspecto | Documento — seccion | Fuente | Rank denso | Rank BM25 | RRF |",
            "|---|---|---|---|---|---|---|",
        ]
        lineas += [_fila_fragmento(i, f) for i, f in enumerate(resultado.fragmentos, start=1)]
        lineas.append("")

    lineas += ["## 5. Respuesta del agente", "", resultado.respuesta, ""]

    aprobadas = sum(ok for _, ok in checks)
    lineas += [
        f"## 6. Verificacion de coherencia ({aprobadas}/{len(checks)})",
        "",
        "| Verificacion | Resultado |",
        "|---|---|",
    ]
    lineas += [f"| {d} | {'Cumple' if ok else 'No cumple'} |" for d, ok in checks]
    lineas.append("")

    (DIR_SALIDA / nombre).write_text("\n".join(lineas), encoding="utf-8")
    return nombre


def escribir_resumen(filas: list[dict]) -> None:
    total_checks = sum(f["checks_total"] for f in filas)
    total_ok = sum(f["checks_ok"] for f in filas)
    con_llm = [f for f in filas if f["latencia_llm_s"] > 0]
    latencia_media = sum(f["latencia_total_s"] for f in con_llm) / len(con_llm) if con_llm else 0
    con_citas = [f for f in con_llm if f["tiene_citas"]]

    lineas = [
        "# Resumen de escenarios de prueba",
        "",
        f"- **Fecha:** {datetime.now():%Y-%m-%d %H:%M}",
        f"- **Motor:** {CONFIG_MODELOS.proveedor_llm} `{CONFIG_MODELOS.modelo_groq}`",
        f"- **Verificaciones cumplidas:** {total_ok}/{total_checks} ({100 * total_ok / max(total_checks, 1):.0f}%)",
        f"- **Respuestas generadas con citas [F#]:** {len(con_citas)}/{len(con_llm)}",
        f"- **Latencia media extremo a extremo (escenarios con LLM):** {latencia_media:.1f} s",
        "",
        "| Escenario | Titulo | Verificaciones | Latencia total (s) | Evidencia |",
        "|---|---|---|---|---|",
    ]
    for f in filas:
        lineas.append(
            f"| {f['id']} | {f['titulo']} | {f['checks_ok']}/{f['checks_total']} | "
            f"{f['latencia_total_s']:.1f} | [{f['archivo']}]({f['archivo']}) |"
        )
    lineas += [
        "",
        "Las verificaciones son automaticas (patrones de texto y fragmentos recuperados) y se",
        "complementan con revision humana de cada respuesta.",
    ]
    (DIR_SALIDA / "RESUMEN.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


def ejecutar(ids: list[str] | None = None, pausa: int = PAUSA_ENTRE_ESCENARIOS_S) -> None:
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    seleccion = [e for e in ESCENARIOS if not ids or e.id in ids]
    filas: list[dict] = []

    for posicion, escenario in enumerate(seleccion):
        if posicion > 0 and pausa:
            time.sleep(pausa)
        print(f"Ejecutando {escenario.id}: {escenario.titulo}")
        resultado = responder(escenario.consulta)
        checks = [(v.descripcion, bool(v.evaluar(resultado))) for v in escenario.verificaciones]
        archivo = escribir_evidencia(escenario, resultado, checks)
        ok = sum(c for _, c in checks)
        print(f"  -> {ok}/{len(checks)} verificaciones | {resultado.tipo} | "
              f"{resultado.latencia_recuperacion_s + resultado.latencia_llm_s:.1f} s")
        filas.append({
            "id": escenario.id,
            "titulo": escenario.titulo,
            "consulta": escenario.consulta,
            "tipo": resultado.tipo,
            "checks_ok": ok,
            "checks_total": len(checks),
            "checks": [{"verificacion": d, "cumple": c} for d, c in checks],
            "latencia_recuperacion_s": resultado.latencia_recuperacion_s,
            "latencia_llm_s": resultado.latencia_llm_s,
            "latencia_total_s": resultado.latencia_recuperacion_s + resultado.latencia_llm_s,
            "tiene_citas": tiene_citas(resultado),
            "fragmentos": [f"{f.documento} — {f.seccion}" for f in resultado.fragmentos],
            "respuesta": resultado.respuesta,
            "error": resultado.error,
            "archivo": archivo,
        })

    if not ids:
        escribir_resumen(filas)
    (DIR_SALIDA / ("resultados.json" if not ids else f"resultados_{'_'.join(ids)}.json")).write_text(
        json.dumps(filas, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description="Ejecuta los escenarios de prueba del agente.")
    analizador.add_argument("--escenario", action="append", help="ID de escenario, ej. ESC-02")
    analizador.add_argument("--pausa", type=int, default=PAUSA_ENTRE_ESCENARIOS_S,
                            help="Segundos entre escenarios (cuota gratuita del LLM)")
    argumentos = analizador.parse_args()
    ejecutar(argumentos.escenario, argumentos.pausa)
