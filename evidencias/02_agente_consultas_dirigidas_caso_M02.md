# Evidencia 02 — Agente con consultas dirigidas por aspecto (caso M02)

- **Fecha:** 2026-09-24
- **Motor:** Groq `openai/gpt-oss-120b` · recuperación 4,8 s · LLM 7,3 s
- **Envío:** `LR-2026-005271` (cliente ausente, 2 intentos)
- **Cambio respecto a la evidencia 01:** el agente ya no usa una sola consulta de
  recuperación, sino una por aspecto del caso (motivo, intentos, acción, SLA, escalamiento,
  temporada), y el prompt está en versión 2.

## Fragmentos recuperados y aspecto que los trajo

| Etiqueta | Aspecto | Documento — sección |
|---|---|---|
| F1 | motivo | SLA-COM-002 — 5. Exclusiones de responsabilidad |
| F2 | intentos | **SOP-OPS-014 — 4. Regla de intentos de entrega** (faltaba en la evidencia 01) |
| F3 | accion | SOP-OPS-014 — 6. Matriz de decision de accion operativa |
| F4 | sla | SLA-COM-002 — 4. Umbrales de incidente de SLA |
| F5 | escalamiento | SOP-OPS-014 — 7. Escalamiento |
| F6 | temporada | SLA-COM-002 — 6. Protocolo de peaks de demanda |
| F7 | motivo | CAT-OPS-007 — M02 — Cliente ausente |

## Lo que mejoró

| Defecto de la v1 | Resultado ahora |
|---|---|
| No indicaba intentos restantes | "Intentos realizados: 2 ... máximo 3 ... **queda 1 intento pendiente** [F2]" |
| Inventaba un teléfono | "contáctenos a través del **[canal de atención]**" |
| Listaba fuentes no citadas | Solo lista fuentes citadas |

## Hallazgo: inconsistencia en la documentación fuente

La respuesta afirmó a la vez que el caso **no computa para SLA** [F7] y que es un
**"incidente grave"** que debe **escalarse a N3** [F4][F5].

Revisando las fuentes, el modelo no inventó: `SOP-OPS-014 §7` decía "N3: retraso mayor a
72 horas" **sin distinguir quién causó el retraso**, y `SLA-COM-002 §4` clasifica por días
sin remitir a las exclusiones de la §5. El RAG expuso una **ambigüedad real del procedimiento**.

## Correcciones aplicadas (en tres capas)

| Capa | Cambio |
|---|---|
| Fuente | SOP-OPS-014 §6 y §7 aclaran que los tramos y el escalamiento N2/N3 aplican a retrasos atribuibles a LogiRuta; los atribuibles al consumidor se gestionan en N1 con la regla de intentos |
| Prompt | Regla 2: si un fragmento contradice los hechos verificados, prevalecen los hechos (ejemplo explícito con "Computa para SLA = False") |
| Agente | Si el motivo no computa para SLA, se buscan las exclusiones en vez de los umbrales de incidente, y no se consulta el escalamiento por tramo |

**Lección para el informe:** un sistema RAG es tan consistente como sus fuentes. Además de
responder, sirve para detectar contradicciones en la documentación interna.
