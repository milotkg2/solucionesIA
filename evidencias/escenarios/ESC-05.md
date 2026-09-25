# ESC-05 — Temporada alta sin plazo extendido informado (fuente externa decisiva)

- **Fecha de ejecucion:** 2026-09-24 23:58
- **Motor LLM:** groq `openai/gpt-oss-120b`
- **Tipo de flujo:** diagnostico
- **Latencia:** recuperacion 2.97 s · LLM 18.6 s
- **Resultado esperado:** La extension no es valida porque no se informo al consumidor: rige la fecha promesa original.

## 1. Consulta del usuario

> DecoCasa dice que el envio LR-2026-008455 llego un dia tarde pero que en temporada alta el plazo se extiende. Tienen razon?

## 2. Hechos calculados por la herramienta de tracking (sin LLM)

| Campo | Valor |
|---|---|
| Retailer / servicio | DecoCasa / ST |
| Fecha promesa / entrega real | 2026-09-17 / 2026-09-18 |
| Estado / intentos | ENTREGADO / 1 |
| Motivo | M01 — Congestion vial o sobrecarga de ruta |
| Responsable / computa SLA | LogiRuta / True |
| Dias de retraso / tramo | 1 / hasta_24h |
| Temporada / plazo extendido informado | ALTA / NO |

## 3. Consultas de recuperacion generadas por el agente

| Aspecto | Consulta |
|---|---|
| motivo | M01 Congestion vial o sobrecarga de ruta responsabilidad computa SLA compensacion |
| intentos | regla de intentos de entrega intentos maximos plazo entre intentos Congestion vial o sobrecarga de ruta devolucion al origen |
| accion | matriz de decision accion operativa retraso hasta 24 horas causa atribuible |
| compensacion | tabla de compensaciones al consumidor retraso hasta 24 horas causa atribuible a LogiRuta aprobacion |
| sla | matriz contractual DecoCasa servicio ST plazo de respuesta penalizacion incidente de SLA |
| temporada | protocolo de peaks temporada alta extension de plazo informado al consumidor condiciones ofrecidas fecha promesa exigible |
| normativa | plazo de entrega informado al consumidor condiciones ofrecidas deben respetarse modificacion unilateral reclamo SERNAC |

## 4. Fragmentos recuperados (RAG hibrido)

| Etiqueta | Aspecto | Documento — seccion | Fuente | Rank denso | Rank BM25 | RRF |
|---|---|---|---|---|---|---|
| F1 | motivo | CAT-OPS-007 — M01 — Congestion vial o sobrecarga de ruta | interna | 1 | 1 | 0.0328 |
| F2 | intentos | SOP-OPS-014 — 4. Regla de intentos de entrega | interna | 1 | 1 | 0.0328 |
| F3 | accion | SOP-OPS-014 — 6. Matriz de decision de accion operativa | interna | 1 | 1 | 0.0328 |
| F4 | compensacion | POL-COM-003 — 2. Tabla de compensaciones al consumidor final | interna | 1 | 1 | 0.0328 |
| F5 | sla | SLA-COM-002 — 4. Umbrales de incidente de SLA | interna | 1 | 2 | 0.0325 |
| F6 | temporada | SLA-COM-002 — 6. Protocolo de peaks de demanda | interna | 1 | 1 | 0.0328 |
| F7 | normativa | EXT-NORM-002 — 2. Modificaciones relevantes para comercio electronico | externa | 2 | 2 | 0.0323 |
| F8 | motivo | CAT-OPS-007 — Tabla resumen de responsabilidad | interna | 2 | 2 | 0.0323 |

## 5. Respuesta del agente

### 1. Diagnóstico
- **Causa probable:** Congestión vial o sobrecarga de ruta (motivo **M01**) que obligó al vehículo a retornar al hub y reprogramar la entrega al día siguiente [F1].  
- **Responsable:** LogiRuta, según el catálogo de responsabilidad para M01 [F8].  
- **Computa para SLA:** Sí, el envío está marcado como “Computa para SLA: True” en los hechos verificados [Hechos].  
- **Intentos de entrega:** Se registró **1 intento** (entrega exitosa el 18‑09). Para M01 la regla indica reprogramación automática al día hábil siguiente y no contempla intentos adicionales [F2].

### 2. Acción operativa
1. Registrar el incidente de SLA como **nivel Leve** (retraso ≤ 24 h) [F5].  
2. Generar y enviar al cliente una **disculpa formal** y confirmar la fecha de entrega ya realizada [F4].  
3. Actualizar el historial interno con la causa M01 y la compensación aplicada [F3].  
4. No se requiere re‑intento ni re‑programación adicional porque la entrega ya se completó [F2].  

- **Nivel de escalamiento:** No aplica escalamiento adicional (registro interno).  
- **Compensación correspondiente:** Disculpa formal y confirmación de la fecha de entrega (sin compensación económica). Aprobación requerida por el **Analista de Mesa de Control** [F4].

### 3. Mensaje sugerido para el cliente
> Estimado cliente, le pedimos disculpas por la entrega de su pedido **LR‑2026‑008455** con un día de retraso. Su paquete ya fue entregado el 18 de septiembre. Agradecemos su comprensión y quedamos a su disposición para cualquier consulta a través de nuestro [canal de atención].

### 4. Alertas
- **Riesgo contractual / SLA:** El retraso de 1 día computa para el SLA y genera un incidente leve, pero no implica penalización económica [F5].  
- **Temporada alta:** La extensión de plazo solo es válida si el retailer informó al consumidor con al menos 10 días de antelación. En este caso **no se informó** la extensión [Hechos] → la fecha promesa original se mantiene y el retraso es relevante para el SLA [F6].  
- **Riesgo de reclamo SERNAC:** Al no haber comunicado previamente la extensión, existe la posibilidad de reclamo; la respuesta proactiva y la disculpa formal mitigan el riesgo.

### 5. Fuentes utilizadas
- **[F1]** CAT-OPS-007 – Motivo M01 (Congestión vial)  
- **[F2]** SOP-OPS-014 – Regla de intentos de entrega para M01  
- **[F3]** SOP-OPS-014 – Matriz de decisión de acción operativa  
- **[F4]** POL-COM-003 – Tabla de compensaciones (tramo ≤ 24 h)  
- **[F5]** SLA-COM-002 – Umbrales de incidente de SLA (nivel Leve)  
- **[F6]** SLA-COM-002 – Protocolo de peaks de demanda (extensión de plazo)  
- **[F8]** CAT-OPS-007 – Tabla resumen de responsabilidad (M01)

## 6. Verificacion de coherencia (6/6)

| Verificacion | Resultado |
|---|---|
| Incluye citas [F#] (objetivo O2) | Cumple |
| Incluye mensaje sugerido para el cliente | Cumple |
| Concluye que la extension no aplica por no haberse informado | Cumple |
| Recupera el protocolo de peaks (SLA-COM-002 §6) | Cumple |
| Recupera al menos una fuente externa (normativa) | Cumple |
| Tramo hasta 24 h: disculpa sin compensacion economica | Cumple |
