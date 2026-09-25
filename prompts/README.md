# Prompts del agente y justificación de su diseño

## Archivos

| Archivo | Tipo | Cuándo se usa |
|---|---|---|
| `sistema_agente.md` | Prompt de sistema | En todas las llamadas. Define rol y reglas. |
| `diagnostico_envio.md` | Plantilla de usuario | Cuando la consulta contiene un código de envío `LR-AAAA-NNNNNN`. |
| `consulta_politicas.md` | Plantilla de usuario | Cuando la consulta es general (sin envío), por ejemplo "¿cuántos reintentos permite M02?". |

Las plantillas tienen marcadores `{{consulta}}`, `{{hechos}}` y `{{contexto}}` que
`src/prompts.py` reemplaza en tiempo de ejecución.

## Estructura común: rol → contexto → tarea → formato → restricciones

| Componente | Dónde está | Qué resuelve del caso |
|---|---|---|
| **Rol** | Sistema, primer párrafo | El modelo actúa como apoyo a un analista de Mesa de Control, no como agente de atención directa al público. Fija el tono y el nivel técnico. |
| **Contexto verificado** | `{{hechos}}` | Datos del envío calculados en código (`src/tracking.py`). El modelo no los deduce. |
| **Contexto recuperado** | `{{contexto}}` | Fragmentos `[F1]..[F5]` del RAG, con documento y sección. |
| **Tarea** | Plantilla | Lo que debe producir. |
| **Formato de salida** | Plantilla, secciones fijas | Hace la respuesta comparable entre escenarios y fácil de revisar. |
| **Restricciones** | Sistema, 8 reglas | Controlan alucinación, cumplimiento de políticas y tono. |

## Justificación de cada regla del prompt de sistema

| Regla | Requerimiento del caso que atiende | Riesgo que evita |
|---|---|---|
| 1. Usar solo hechos y fragmentos | Objetivo O2: 100% de respuestas con referencia a fuente | Que el modelo invente plazos o políticas desde su entrenamiento general |
| 2. No recalcular hechos | Coherencia datos → respuesta | Errores aritméticos con fechas. Lo observamos: un modelo local de 3B inventó una compensación que el catálogo prohíbe |
| 3. Citar `[F#]` en cada regla | Restricción de transparencia de la propuesta; auditoría interna del SOP-OPS-014 §9 | Afirmaciones imposibles de verificar |
| 4. "Sin respaldo documental: escalar" | SOP-OPS-014 §8 prohíbe informar sin confirmación | Que el modelo rellene vacíos con suposiciones |
| 5. Solo compensaciones de POL-COM-003 | POL-COM-003 §4 prohíbe compensaciones no contempladas | Compromisos comerciales no autorizados |
| 6. Sin calificaciones jurídicas | EXT-NORM-002 §4 limita el uso de la normativa | Que el sistema aparente dar asesoría legal |
| 7. Mensaje al cliente sin detalles internos | POL-COM-003 §5 (cómo comunicar) | Exponer rutas/hubs o culpar a terceros públicamente |
| 8. Español | Usuarios y clientes en Chile | Respuestas mezcladas de idioma |

## Decisiones de diseño

**Una sola llamada al LLM en vez de tres prompts encadenados** (diagnóstico → acción →
mensaje). Se evaluó separar en tres pasos, pero:

- el mensaje al cliente depende del diagnóstico y la acción; en una sola llamada el modelo
  mantiene coherencia interna entre las tres partes;
- triplicar las llamadas triplica latencia y consumo de cuota gratuita;
- la estructura de secciones fijas ya separa las tres salidas de forma verificable.

**Hechos antes que fragmentos.** En la plantilla, los hechos del envío aparecen antes que
los fragmentos. El modelo primero fija "qué pasó" y luego busca "qué regla aplica", que es el
mismo orden del flujo obligatorio del SOP-OPS-014 §5 (identificar → clasificar → verificar
SLA → decidir → comunicar).

**Temperatura 0.1.** Se busca consistencia entre ejecuciones, no creatividad.

**Sección "Alertas" explícita.** Obliga al modelo a revisar el caso de temporada alta y la
extensión de plazo no informada (ejemplo `LR-2026-008455`), donde la fuente externa cambia
la conclusión.

**Dos plantillas según intención.** Si no hay código de envío no hay hechos que inyectar;
usar la misma plantilla dejaría secciones vacías e invitaría al modelo a inventarlas.

## Iteraciones

| Versión | Problema observado | Cambio |
|---|---|---|
| v1 → v2 | En el caso M02 el modelo inventó un teléfono de contacto en el mensaje al cliente | Regla 7: prohibido inventar teléfonos/correos/enlaces; usar `[canal de atencion]` |
| v1 → v2 | Listó como "fuente utilizada" un fragmento que no citó | Sección 5: listar solo fuentes efectivamente citadas |
| v1 → v2 | No indicó intentos restantes | Plantilla pide intentos restantes si hay fragmento; el agente hace consultas de recuperación dirigidas para traer SOP-OPS-014 §4 |

Detalle y salida completa: [`evidencias/01_prueba_prompt_v1_caso_M02.md`](../evidencias/01_prueba_prompt_v1_caso_M02.md).
