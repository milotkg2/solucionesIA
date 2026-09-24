"""Herramienta de tracking: consulta determinista de envios y calculo de hechos.

Este modulo NO usa el LLM ni el RAG. Lee los CSV con pandas, busca por codigo exacto
y calcula retraso, tramo y responsabilidad en codigo. Asi se evita que el modelo invente
fechas, dias de atraso o si corresponde compensacion.

Regla de diseno del proyecto: datos estructurados = consulta determinista;
conocimiento documental = RAG.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from functools import lru_cache

import pandas as pd

from src.config import CSV_ENVIOS, CSV_EVENTOS, FECHA_OPERACION

# Codigo de seguimiento del dataset simulado: LR-2026-004182
PATRON_CODIGO = re.compile(r"\bLR-\d{4}-\d{6}\b", re.IGNORECASE)

# Responsabilidad y efecto en SLA segun CAT-OPS-007. Se fija aqui porque es una regla
# dura del negocio: no debe depender de lo que el LLM "recuerde" del fragmento recuperado.
CATALOGO_MOTIVOS: dict[str, dict[str, str | bool]] = {
    "M01": {
        "nombre": "Congestion vial o sobrecarga de ruta",
        "responsable": "LogiRuta",
        "computa_sla": True,
        "compensacion_posible": True,
    },
    "M02": {
        "nombre": "Cliente ausente",
        "responsable": "Consumidor",
        "computa_sla": False,
        "compensacion_posible": False,
    },
    "M03": {
        "nombre": "Direccion incompleta o erronea",
        "responsable": "Consumidor / Retailer",
        "computa_sla": False,
        "compensacion_posible": False,
    },
    "M04": {
        "nombre": "Quiebre de capacidad del hub",
        "responsable": "LogiRuta",
        "computa_sla": True,
        "compensacion_posible": True,
    },
    "M05": {
        "nombre": "Rechazo del consumidor",
        "responsable": "Consumidor",
        "computa_sla": False,
        "compensacion_posible": False,
    },
    "M06": {
        "nombre": "Zona de riesgo o acceso restringido",
        "responsable": "Compartida",
        "computa_sla": False,
        "compensacion_posible": False,
    },
    "M07": {
        "nombre": "Paquete danado o perdido en red",
        "responsable": "LogiRuta",
        "computa_sla": True,
        "compensacion_posible": True,
    },
}

# Descripcion de servicios segun SLA-COM-002
SERVICIOS: dict[str, str] = {
    "SD": "Express same day (mismo dia)",
    "ND": "Express next day (1 dia habil)",
    "ST": "Estandar (3 dias habiles)",
    "SE": "Estandar extendido (5 dias habiles)",
}


@dataclass
class EventoTracking:
    fecha_hora: str
    estado_evento: str
    ubicacion: str
    detalle: str


@dataclass
class HechosEnvio:
    """Hechos verificados de un envio. El LLM los recibe ya calculados."""

    codigo_seguimiento: str
    encontrado: bool
    retailer: str = ""
    servicio: str = ""
    servicio_descripcion: str = ""
    hub_origen: str = ""
    comuna_destino: str = ""
    fecha_compra: str = ""
    fecha_promesa: str = ""
    fecha_entrega_real: str | None = None
    estado: str = ""
    intentos_entrega: int = 0
    motivo_falla: str | None = None
    motivo_nombre: str | None = None
    responsable: str | None = None
    computa_sla: bool | None = None
    compensacion_posible: bool | None = None
    temporada: str = ""
    plazo_extendido_informado: str = ""
    observacion: str = ""
    fecha_referencia: str = FECHA_OPERACION
    dias_retraso: int | None = None
    hay_retraso_confirmado: bool = False
    tramo_retraso: str | None = None
    eventos: list[EventoTracking] = field(default_factory=list)
    mensaje_error: str | None = None

    def a_dict(self) -> dict:
        return asdict(self)


def detectar_codigo(texto: str) -> str | None:
    """Extrae el primer codigo de seguimiento presente en un texto libre."""
    coincidencia = PATRON_CODIGO.search(texto or "")
    return coincidencia.group(0).upper() if coincidencia else None


@lru_cache(maxsize=1)
def _cargar_envios() -> pd.DataFrame:
    return pd.read_csv(CSV_ENVIOS, dtype=str).fillna("")


@lru_cache(maxsize=1)
def _cargar_eventos() -> pd.DataFrame:
    return pd.read_csv(CSV_EVENTOS, dtype=str).fillna("")


def _parsear_fecha(valor: str) -> date | None:
    if not valor or not str(valor).strip():
        return None
    return datetime.strptime(str(valor).strip()[:10], "%Y-%m-%d").date()


def _clasificar_tramo(dias: int) -> str:
    """Tramos alineados a POL-COM-003."""
    if dias <= 0:
        return "sin_retraso"
    if dias <= 1:
        return "hasta_24h"
    if dias <= 3:
        return "mas_de_24h_hasta_72h"
    if dias <= 5:
        return "mas_de_72h_hasta_5_dias"
    return "mas_de_5_dias"


def consultar_envio(
    codigo: str,
    fecha_referencia: str | None = None,
) -> HechosEnvio:
    """Busca un envio por codigo exacto y calcula los hechos operativos."""
    codigo = (codigo or "").strip().upper()
    fecha_ref = _parsear_fecha(fecha_referencia or FECHA_OPERACION)
    if fecha_ref is None:
        raise ValueError(f"Fecha de referencia invalida: {fecha_referencia or FECHA_OPERACION}")

    if not codigo:
        return HechosEnvio(
            codigo_seguimiento="",
            encontrado=False,
            mensaje_error="No se indico un codigo de seguimiento.",
        )

    envios = _cargar_envios()
    coincidencias = envios[envios["codigo_seguimiento"].str.upper() == codigo]
    if coincidencias.empty:
        return HechosEnvio(
            codigo_seguimiento=codigo,
            encontrado=False,
            fecha_referencia=fecha_ref.isoformat(),
            mensaje_error=f"No existe el envio {codigo} en el dataset simulado.",
        )

    fila = coincidencias.iloc[0]
    motivo = (fila.get("motivo_falla") or "").strip().upper() or None
    meta_motivo = CATALOGO_MOTIVOS.get(motivo or "", {})

    fecha_promesa = _parsear_fecha(fila.get("fecha_promesa", ""))
    fecha_entrega = _parsear_fecha(fila.get("fecha_entrega_real", ""))

    # Si ya se entrego, el retraso se mide contra la entrega real.
    # Si no, se mide contra la fecha de referencia de la operacion.
    fecha_comparacion = fecha_entrega or fecha_ref
    dias_retraso = None
    hay_retraso = False
    tramo = None
    if fecha_promesa is not None:
        dias_retraso = (fecha_comparacion - fecha_promesa).days
        hay_retraso = dias_retraso > 0
        tramo = _clasificar_tramo(dias_retraso)

    eventos_df = _cargar_eventos()
    eventos_envio = eventos_df[eventos_df["codigo_seguimiento"].str.upper() == codigo]
    eventos = [
        EventoTracking(
            fecha_hora=str(ev["fecha_hora"]),
            estado_evento=str(ev["estado_evento"]),
            ubicacion=str(ev["ubicacion"]),
            detalle=str(ev["detalle"]),
        )
        for _, ev in eventos_envio.sort_values("fecha_hora").iterrows()
    ]

    servicio = str(fila.get("servicio", "")).strip().upper()
    return HechosEnvio(
        codigo_seguimiento=codigo,
        encontrado=True,
        retailer=str(fila.get("retailer", "")),
        servicio=servicio,
        servicio_descripcion=SERVICIOS.get(servicio, servicio),
        hub_origen=str(fila.get("hub_origen", "")),
        comuna_destino=str(fila.get("comuna_destino", "")),
        fecha_compra=str(fila.get("fecha_compra", "")),
        fecha_promesa=str(fila.get("fecha_promesa", "")),
        fecha_entrega_real=str(fila.get("fecha_entrega_real", "")) or None,
        estado=str(fila.get("estado", "")),
        intentos_entrega=int(fila.get("intentos_entrega") or 0),
        motivo_falla=motivo,
        motivo_nombre=str(meta_motivo.get("nombre")) if meta_motivo else None,
        responsable=str(meta_motivo.get("responsable")) if meta_motivo else None,
        computa_sla=bool(meta_motivo.get("computa_sla")) if meta_motivo else None,
        compensacion_posible=bool(meta_motivo.get("compensacion_posible"))
        if meta_motivo
        else None,
        temporada=str(fila.get("temporada", "")),
        plazo_extendido_informado=str(fila.get("plazo_extendido_informado", "")),
        observacion=str(fila.get("observacion", "")),
        fecha_referencia=fecha_ref.isoformat(),
        dias_retraso=dias_retraso,
        hay_retraso_confirmado=hay_retraso,
        tramo_retraso=tramo,
        eventos=eventos,
    )


def formatear_hechos(hechos: HechosEnvio) -> str:
    """Bloque de texto listo para inyectar en el prompt del agente."""
    if not hechos.encontrado:
        return (
            f"HECHOS DEL ENVIO: no encontrados.\n"
            f"Codigo consultado: {hechos.codigo_seguimiento or '(ninguno)'}\n"
            f"Detalle: {hechos.mensaje_error}"
        )

    lineas = [
        "HECHOS VERIFICADOS DEL ENVIO (calculados en codigo, no por el LLM):",
        f"- Codigo: {hechos.codigo_seguimiento}",
        f"- Retailer: {hechos.retailer}",
        f"- Servicio: {hechos.servicio} ({hechos.servicio_descripcion})",
        f"- Hub origen: {hechos.hub_origen}",
        f"- Destino: {hechos.comuna_destino}",
        f"- Fecha compra: {hechos.fecha_compra}",
        f"- Fecha promesa: {hechos.fecha_promesa}",
        f"- Fecha entrega real: {hechos.fecha_entrega_real or 'pendiente'}",
        f"- Estado actual: {hechos.estado}",
        f"- Intentos de entrega: {hechos.intentos_entrega}",
        f"- Motivo de falla: {hechos.motivo_falla or 'sin motivo'} "
        f"({hechos.motivo_nombre or 'n/a'})",
        f"- Responsable segun catalogo: {hechos.responsable or 'n/a'}",
        f"- Computa para SLA: {hechos.computa_sla}",
        f"- Compensacion posible segun catalogo: {hechos.compensacion_posible}",
        f"- Temporada: {hechos.temporada}",
        f"- Plazo extendido informado al consumidor: {hechos.plazo_extendido_informado}",
        f"- Fecha de referencia operacional: {hechos.fecha_referencia}",
        f"- Dias de retraso: {hechos.dias_retraso}",
        f"- Retraso confirmado: {hechos.hay_retraso_confirmado}",
        f"- Tramo de retraso (POL-COM-003): {hechos.tramo_retraso}",
        f"- Observacion operativa: {hechos.observacion}",
    ]

    if hechos.eventos:
        lineas.append("- Historial de tracking:")
        for evento in hechos.eventos:
            lineas.append(
                f"  * {evento.fecha_hora} | {evento.estado_evento} | "
                f"{evento.ubicacion} | {evento.detalle}"
            )
    else:
        lineas.append("- Historial de tracking: sin eventos registrados")

    return "\n".join(lineas)


if __name__ == "__main__":
    import sys

    texto = " ".join(sys.argv[1:]) or "Consulta el envio LR-2026-004182"
    codigo = detectar_codigo(texto) or texto.strip()
    hechos = consultar_envio(codigo)
    print(formatear_hechos(hechos))
