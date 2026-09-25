# Evidencia 01 — Prueba del prompt v1 sobre el caso M02 (cliente ausente)

- **Fecha:** 2026-09-24
- **Motor:** Groq `openai/gpt-oss-120b`, temperatura 0.1
- **Latencia:** 8,9 s
- **Envío:** `LR-2026-005271` (MegaHogar, ST, 2 intentos fallidos, motivo M02)
- **Por qué este caso:** en la medición inicial, el modelo local Llama 3.2 3B respondió que
  un caso M02 tenía "compensación obligatoria", contradiciendo el catálogo CAT-OPS-007.

## Consulta

> El cliente del envio LR-2026-005271 reclama que no le ha llegado y pide compensacion. Que hago?

## Fragmentos recuperados

| Etiqueta | Documento — sección |
|---|---|
| F1 | SOP-OPS-014 — 6. Matriz de decision de accion operativa |
| F2 | SLA-COM-002 — 3. Matriz contractual por retailer |
| F3 | CAT-OPS-007 — M02 — Cliente ausente |
| F4 | CAT-OPS-007 — Tabla resumen de responsabilidad |
| F5 | EXT-SERNAC-001 — 1. Magnitud del problema en periodos de alta demanda |

## Respuesta del modelo (extracto)

> **Responsable:** Consumidor [F4]. **¿Computa para el SLA?** No [F4].
>
> **Compensación:** No corresponde compensación por estar catalogado como "Compensación: no
> corresponde" para M02 [F3][F4].
>
> **Mensaje al cliente:** "...Por favor, responda a este mensaje o contáctenos al
> +56 9 XXXX XXXX para reprogramar la entrega..."

## Evaluación de coherencia

| Criterio | Resultado |
|---|---|
| Responsable y SLA coinciden con los hechos calculados | Correcto |
| No ofrece compensación (regla de POL-COM-003 y CAT-OPS-007) | Correcto — corrige el error del modelo local |
| Cita `[F#]` en cada regla | Correcto |
| Indica intentos restantes (2 de 3 usados) | **Falla**: no se recuperó SOP-OPS-014 §4 |
| No inventa datos de contacto | **Falla**: inventa un teléfono de relleno |
| Lista solo fuentes citadas | **Falla**: incluye F5 sin haberla citado |

## Cambios derivados (prompt v2 y agente)

1. Regla 7 del sistema: prohibido inventar teléfonos, correos o enlaces; usar `[canal de atencion]`.
2. Sección 5 de la plantilla: listar solo las fuentes efectivamente citadas.
3. Plantilla de diagnóstico: pedir intentos restantes cuando exista fragmento de la regla de intentos.
4. Agente: consultas de recuperación dirigidas por aspecto (motivo, intentos, compensación,
   SLA, escalamiento) en lugar de una sola consulta, para no perder SOP-OPS-014 §4.
