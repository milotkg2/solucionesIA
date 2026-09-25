# ESC-02 — Cliente ausente con dos intentos fallidos (M02)

- **Fecha de ejecucion:** 2026-09-24 23:56
- **Motor LLM:** groq `openai/gpt-oss-120b`
- **Tipo de flujo:** diagnostico
- **Latencia:** recuperacion 2.85 s · LLM 5.99 s
- **Resultado esperado:** Causa atribuible al consumidor: sin compensacion, queda un intento.

## 1. Consulta del usuario

> El cliente del envio LR-2026-005271 reclama que no le ha llegado y pide compensacion. Que hago?

## 2. Hechos calculados por la herramienta de tracking (sin LLM)

| Campo | Valor |
|---|---|
| Retailer / servicio | MegaHogar / ST |
| Fecha promesa / entrega real | 2026-09-16 / pendiente |
| Estado / intentos | INTENTO_FALLIDO / 2 |
| Motivo | M02 — Cliente ausente |
| Responsable / computa SLA | Consumidor / False |
| Dias de retraso / tramo | 7 / mas_de_5_dias |
| Temporada / plazo extendido informado | ALTA / SI |

## 3. Consultas de recuperacion generadas por el agente

| Aspecto | Consulta |
|---|---|
| motivo | M02 Cliente ausente responsabilidad computa SLA compensacion |
| intentos | regla de intentos de entrega intentos maximos plazo entre intentos Cliente ausente devolucion al origen |
| accion | matriz de decision accion operativa retraso mas de 5 dias causa atribuible |
| sla | exclusiones de responsabilidad no se computan como incumplimiento de SLA Cliente ausente |
| temporada | protocolo de peaks temporada alta extension de plazo informado al consumidor condiciones ofrecidas fecha promesa exigible |
| normativa | plazo de entrega informado al consumidor condiciones ofrecidas deben respetarse modificacion unilateral reclamo SERNAC |

## 4. Fragmentos recuperados (RAG hibrido)

| Etiqueta | Aspecto | Documento — seccion | Fuente | Rank denso | Rank BM25 | RRF |
|---|---|---|---|---|---|---|
| F1 | motivo | SLA-COM-002 — 5. Exclusiones de responsabilidad | interna | 1 | 3 | 0.0323 |
| F2 | intentos | SOP-OPS-014 — 4. Regla de intentos de entrega | interna | 1 | 1 | 0.0328 |
| F3 | accion | SOP-OPS-014 — 6. Matriz de decision de accion operativa | interna | 1 | 1 | 0.0328 |
| F4 | temporada | SLA-COM-002 — 6. Protocolo de peaks de demanda | interna | 1 | 1 | 0.0328 |
| F5 | normativa | EXT-NORM-002 — 2. Modificaciones relevantes para comercio electronico | externa | 2 | 2 | 0.0323 |
| F6 | motivo | CAT-OPS-007 — M02 — Cliente ausente | interna | 5 | 1 | 0.0318 |
| F7 | intentos | SOP-OPS-014 — 3. Definiciones operativas | interna | 2 | 3 | 0.0320 |
| F8 | sla | SLA-COM-002 — 1. Proposito | interna | 3 | 5 | 0.0313 |

## 5. Respuesta del agente

### 1. Diagnóstico
- **Causa probable del retraso:** ausencia del consumidor en la dirección indicada (motivo **M02**). Evidenciado por los dos intentos fallidos con observación “domicilio sin moradores” en el historial de tracking. **[F6]**  
- **Responsable:** Consumidor (según catálogo de motivos). **[F6]**  
- **¿Computa para SLA?:** No computa para SLA (campo “Computa para SLA: False”). **[hechos]**  
- **Intentos de entrega restantes:** La regla de intentos para M02 permite **3 intentos**; se han realizado **2**, por lo que queda **1 intento** disponible. **[F2]**

### 2. Acción operativa
1. **Contactar al consumidor** a través del canal de atención para acordar una nueva ventana horaria de entrega (o ofrecer retiro en punto de conveniencia). **[F6]**  
2. **Programar el tercer intento** de entrega dentro del rango de **24 a 48 horas hábiles** a partir de la confirmación del cliente. **[F2]**  
3. **Actualizar el tracking** con el estado “PENDIENTE_REPROGRAMACION” y registrar la coordinación realizada.  
4. **Monitorear** la ejecución del tercer intento; si falla, proceder según SOP‑OPS‑014 a “DEVUELTO_ORIGEN” y notificar al retailer dentro de 24 h. **[F2]**  

- **Nivel de escalamiento:** No se requiere escalamiento en esta fase; solo se escalará a Jefe de Operaciones si el tercer intento también falla (regla de tres intentos). **[F2]**  
- **Compensación:** No corresponde compensación porque la causa es atribuible al consumidor (motivo M02). **[F3]**, **[F6]**  
- **Aprobación de compensación:** No aplica.

### 3. Mensaje sugerido para el cliente
> Estimado cliente, le informamos que hemos intentado entregar su pedido en dos oportunidades y no hemos podido localizarlo en su domicilio. Para poder concretar la entrega, le solicitamos coordinar una nueva ventana horaria o, si lo prefiere, retirar su pedido en el punto de conveniencia más cercano. Por favor, contáctenos a través del [canal de atención] para confirmar la fecha y hora que le resulte más conveniente. Agradecemos su comprensión.

### 4. Alertas
- **Riesgos contractuales / SERNAC:** No hay incumplimiento de SLA porque el retraso no computa para SLA y la causa es atribuible al consumidor. Sin embargo, se recomienda mantener una comunicación clara para evitar reclamos por falta de información.  
- **Temporada alta:** La extensión de plazo está **válida**, ya que el retailer informó al consumidor del plazo extendido (campo “Plazo extendido informado al consumidor: SI”). **[F4]**  
- **Sin alertas adicionales.**

### 5. Fuentes utilizadas
- **[F2]** SOP‑OPS‑014 – 4. Regla de intentos de entrega (tabla de intentos y responsable).  
- **[F3]** SOP‑OPS‑014 – 6. Matriz de decisión de acción operativa (fila “Causa atribuible al consumidor”).  
- **[F4]** SLA‑COM‑002 – 6. Protocolo de peaks de demanda (validación de extensión de plazo).  
- **[F6]** CAT‑OPS‑007 – M02 — Cliente ausente (descripción, responsabilidad, compensación y acción correctiva).  
- **Hechos verificados** del envío (código, motivo, intentos, etc.).

## 6. Verificacion de coherencia (5/5)

| Verificacion | Resultado |
|---|---|
| Incluye citas [F#] (objetivo O2) | Cumple |
| Incluye mensaje sugerido para el cliente | Cumple |
| Indica que no corresponde compensacion | Cumple |
| Indica el intento restante | Cumple |
| Recupera la regla de intentos (SOP-OPS-014 §4) | Cumple |
