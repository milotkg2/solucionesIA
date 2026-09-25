# ESC-06 — Consulta general de politicas (sin envio)

- **Fecha de ejecucion:** 2026-09-24 23:59
- **Motor LLM:** groq `openai/gpt-oss-120b`
- **Tipo de flujo:** politicas
- **Latencia:** recuperacion 2.18 s · LLM 10.25 s
- **Resultado esperado:** Responder con RAG puro: 3 intentos, sin compensacion.

## 1. Consulta del usuario

> Cuantos intentos de entrega permite el procedimiento cuando el cliente esta ausente y corresponde compensacion?

## 2. Hechos del envio

No aplica o envio no encontrado.

## 3. Consultas de recuperacion generadas por el agente

| Aspecto | Consulta |
|---|---|
| consulta | Cuantos intentos de entrega permite el procedimiento cuando el cliente esta ausente y corresponde compensacion? |

## 4. Fragmentos recuperados (RAG hibrido)

| Etiqueta | Aspecto | Documento — seccion | Fuente | Rank denso | Rank BM25 | RRF |
|---|---|---|---|---|---|---|
| F1 | consulta | SOP-OPS-014 — 4. Regla de intentos de entrega | interna | 1 | 2 | 0.0325 |
| F2 | consulta | CAT-OPS-007 — M02 — Cliente ausente | interna | 2 | 1 | 0.0325 |
| F3 | consulta | SOP-OPS-014 — 8. Prohibiciones | interna | 3 | - | 0.0159 |
| F4 | consulta | SOP-OPS-014 — 6. Matriz de decision de accion operativa | interna | - | 3 | 0.0159 |
| F5 | consulta | SOP-OPS-014 — 5. Flujo obligatorio de atencion de una excepcion | interna | 4 | - | 0.0156 |

## 5. Respuesta del agente

### Respuesta
- El procedimiento permite **hasta 3 intentos de entrega** cuando el cliente está ausente (motivo M02) [F1].  
- **No corresponde compensación** en este caso [F2].

### Detalle aplicable
- Los intentos deben espaciarse entre **24 y 48 horas hábiles** y son gestionados por el **Hub de origen** [F1].  
- El motivo M02 se clasifica como **responsabilidad del consumidor**, por lo que no genera compensación automática [F2].  
- Según la matriz de decisión, los motivos atribuibles al consumidor (M02, M03, M05) **no generan compensación** y se siguen los reintentos establecidos [F4].

### Fuentes utilizadas
- **[F1]** SOP-OPS-014 — 4. Regla de intentos de entrega.  
- **[F2]** CAT-OPS-007 — M02 — Cliente ausente.  
- **[F4]** SOP-OPS-014 — 6. Matriz de decisión de acción operativa.

## 6. Verificacion de coherencia (3/3)

| Verificacion | Resultado |
|---|---|
| Incluye citas [F#] (objetivo O2) | Cumple |
| Indica 3 intentos | Cumple |
| Indica que no corresponde compensacion | Cumple |
