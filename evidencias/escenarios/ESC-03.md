# ESC-03 — Direccion incompleta (M03)

- **Fecha de ejecucion:** 2026-09-24 23:57
- **Motor LLM:** groq `openai/gpt-oss-120b`
- **Tipo de flujo:** diagnostico
- **Latencia:** recuperacion 2.87 s · LLM 4.92 s
- **Resultado esperado:** Validar direccion con el cliente en 48 horas, sin compensacion, RTO si no responde.

## 1. Consulta del usuario

> Que hacemos con el envio LR-2026-006123? El transportista dice que no encuentra la direccion.

## 2. Hechos calculados por la herramienta de tracking (sin LLM)

| Campo | Valor |
|---|---|
| Retailer / servicio | ZapatoExpress / ND |
| Fecha promesa / entrega real | 2026-09-18 / pendiente |
| Estado / intentos | DIRECCION_OBSERVADA / 1 |
| Motivo | M03 — Direccion incompleta o erronea |
| Responsable / computa SLA | Consumidor / Retailer / False |
| Dias de retraso / tramo | 5 / mas_de_72h_hasta_5_dias |
| Temporada / plazo extendido informado | ALTA / SI |

## 3. Consultas de recuperacion generadas por el agente

| Aspecto | Consulta |
|---|---|
| motivo | M03 Direccion incompleta o erronea responsabilidad computa SLA compensacion |
| intentos | regla de intentos de entrega intentos maximos plazo entre intentos Direccion incompleta o erronea devolucion al origen |
| accion | matriz de decision accion operativa retraso mas de 72 horas y hasta 5 dias causa atribuible |
| sla | exclusiones de responsabilidad no se computan como incumplimiento de SLA Direccion incompleta o erronea |
| temporada | protocolo de peaks temporada alta extension de plazo informado al consumidor condiciones ofrecidas fecha promesa exigible |
| normativa | plazo de entrega informado al consumidor condiciones ofrecidas deben respetarse modificacion unilateral reclamo SERNAC |

## 4. Fragmentos recuperados (RAG hibrido)

| Etiqueta | Aspecto | Documento — seccion | Fuente | Rank denso | Rank BM25 | RRF |
|---|---|---|---|---|---|---|
| F1 | motivo | CAT-OPS-007 — M03 — Direccion incompleta o erronea | interna | 1 | 1 | 0.0328 |
| F2 | intentos | SOP-OPS-014 — 4. Regla de intentos de entrega | interna | 1 | 1 | 0.0328 |
| F3 | accion | SOP-OPS-014 — 6. Matriz de decision de accion operativa | interna | 1 | 1 | 0.0328 |
| F4 | sla | SLA-COM-002 — 5. Exclusiones de responsabilidad | interna | 1 | 1 | 0.0328 |
| F5 | temporada | SLA-COM-002 — 6. Protocolo de peaks de demanda | interna | 1 | 1 | 0.0328 |
| F6 | normativa | EXT-NORM-002 — 2. Modificaciones relevantes para comercio electronico | externa | 2 | 2 | 0.0323 |
| F7 | accion | SOP-OPS-014 — 7. Escalamiento | interna | 3 | 3 | 0.0317 |
| F8 | temporada | EXT-NORM-002 — 4. Limite de uso en la solucion | externa | 2 | 3 | 0.0320 |

## 5. Respuesta del agente

### 1. Diagnóstico
- **Causa probable:** Dirección incompleta o errónea (motivo **M03**) – el tracking indica “Dirección sin número ni departamento, no es posible ubicar el domicilio” [F1].  
- **Responsable:** Consumidor / Retailer (origen del dato) [F1].  
- **Computa para SLA:** **No** (el envío está marcado como “Computa para SLA: False”) [F4].  
- **Intentos de entrega realizados:** 1 intento (registro de `DIRECCION_OBSERVADA`). Según la regla de intentos para M03, se permiten **2 intentos** previa validación de la dirección [F2]; por lo tanto **queda 1 intento** pendiente [F2].

### 2. Acción operativa
1. **Contactar al consumidor** para validar la dirección (solicitar número y departamento) [F1][F3].  
2. **Registrar la respuesta** y, si se corrige la dirección, **reprogramar la entrega** y ejecutar el **segundo intento** dentro de las 48 h hábiles posteriores a la validación [F2][F3].  
3. Si **no hay respuesta en 48 h**, proceder a **devolución al origen (RTO)** y notificar al retailer [F3].  
4. **Actualizar el tracking** con el nuevo estado y observaciones.  

- **Nivel de escalamiento:** N1 – Mesa de Control, con plazo máximo de 4 horas hábiles para registrar la excepción y ejecutar la acción [F7].  
- **Compensación:** No corresponde compensación alguna (motivo M03 no genera compensación) [F1][F3]; la aprobación la realiza el analista de Mesa de Control.

### 3. Mensaje sugerido para el cliente
> Estimado/a cliente, hemos intentado entregar su pedido pero la dirección registrada está incompleta (faltan número y/o departamento). Para poder reprogramar la entrega, le solicitamos amablemente que nos confirme los datos faltantes respondiendo a este mensaje o llamando al [canal de atención]. Agradecemos su colaboración y lamentamos cualquier inconveniente.

### 4. Alertas
- **Extensión de plazo:** El servicio ND **no admite extensión** de plazo en ninguna temporada, por lo que la información de “plazo extendido informado al consumidor: SI” no genera un plazo adicional válido [F5].  
- **Riesgo contractual / SERNAC:** No hay riesgo de incumplimiento de SLA (M03 excluye SLA) y no se ha generado reclamo formal; por lo tanto, no se activa escalamiento N2/N3/N4 [F4][F7].  

**Resultado:** Sin alertas adicionales.

### 5. Fuentes utilizadas
- **[F1]** CAT-OPS-007 – M03 – Dirección incompleta o errónea.  
- **[F2]** SOP-OPS-014 – 4. Regla de intentos de entrega.  
- **[F3]** SOP-OPS-014 – 6. Matriz de decisión de acción operativa.  
- **[F4]** SLA-COM-002 – 5. Exclusiones de responsabilidad.  
- **[F5]** SLA-COM-002 – 6. Protocolo de peaks de demanda.  
- **[F7]** SOP-OPS-014 – 7. Escalamiento.

## 6. Verificacion de coherencia (6/6)

| Verificacion | Resultado |
|---|---|
| Incluye citas [F#] (objetivo O2) | Cumple |
| Incluye mensaje sugerido para el cliente | Cumple |
| Pide validar la direccion con el cliente | Cumple |
| Menciona el plazo de 48 horas | Cumple |
| Menciona devolucion al origen si no responde | Cumple |
| Indica que no corresponde compensacion | Cumple |
