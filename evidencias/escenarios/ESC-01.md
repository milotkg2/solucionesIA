# ESC-01 — Retraso por congestion en temporada alta (M01)

- **Fecha de ejecucion:** 2026-09-24 23:56
- **Motor LLM:** groq `openai/gpt-oss-120b`
- **Tipo de flujo:** diagnostico
- **Latencia:** recuperacion 4.93 s · LLM 6.47 s
- **Resultado esperado:** Causa atribuible a LogiRuta con mas de 5 dias: escalamiento y compensacion mayor.

## 1. Consulta del usuario

> El cliente del envio LR-2026-004182 reclama que su pedido no ha llegado. Que le respondo y que corresponde hacer?

## 2. Hechos calculados por la herramienta de tracking (sin LLM)

| Campo | Valor |
|---|---|
| Retailer / servicio | TiendaNova / ND |
| Fecha promesa / entrega real | 2026-09-16 / pendiente |
| Estado / intentos | EN_RUTA / 0 |
| Motivo | M01 — Congestion vial o sobrecarga de ruta |
| Responsable / computa SLA | LogiRuta / True |
| Dias de retraso / tramo | 7 / mas_de_5_dias |
| Temporada / plazo extendido informado | ALTA / NO |

## 3. Consultas de recuperacion generadas por el agente

| Aspecto | Consulta |
|---|---|
| motivo | M01 Congestion vial o sobrecarga de ruta responsabilidad computa SLA compensacion |
| accion | matriz de decision accion operativa retraso mas de 5 dias causa atribuible |
| compensacion | tabla de compensaciones al consumidor retraso mas de 5 dias causa atribuible a LogiRuta aprobacion |
| sla | matriz contractual TiendaNova servicio ND plazo de respuesta penalizacion incidente de SLA |
| escalamiento | escalamiento nivel jefe de hub jefe de operaciones retraso mayor a 72 horas atribuible a LogiRuta |
| temporada | protocolo de peaks temporada alta extension de plazo informado al consumidor condiciones ofrecidas fecha promesa exigible |
| normativa | plazo de entrega informado al consumidor condiciones ofrecidas deben respetarse modificacion unilateral reclamo SERNAC |

## 4. Fragmentos recuperados (RAG hibrido)

| Etiqueta | Aspecto | Documento — seccion | Fuente | Rank denso | Rank BM25 | RRF |
|---|---|---|---|---|---|---|
| F1 | motivo | CAT-OPS-007 — M01 — Congestion vial o sobrecarga de ruta | interna | 1 | 1 | 0.0328 |
| F2 | accion | SOP-OPS-014 — 6. Matriz de decision de accion operativa | interna | 1 | 1 | 0.0328 |
| F3 | compensacion | POL-COM-003 — 2. Tabla de compensaciones al consumidor final | interna | 2 | 1 | 0.0325 |
| F4 | sla | SLA-COM-002 — 4. Umbrales de incidente de SLA | interna | 1 | 2 | 0.0325 |
| F5 | escalamiento | SOP-OPS-014 — 7. Escalamiento | interna | 1 | 1 | 0.0328 |
| F6 | temporada | SLA-COM-002 — 6. Protocolo de peaks de demanda | interna | 1 | 1 | 0.0328 |
| F7 | normativa | EXT-NORM-002 — 2. Modificaciones relevantes para comercio electronico | externa | 2 | 2 | 0.0323 |
| F8 | motivo | CAT-OPS-007 — Tabla resumen de responsabilidad | interna | 2 | 2 | 0.0323 |

## 5. Respuesta del agente

### 1. Diagnóstico
- **Causa probable:** Congestión vial o sobrecarga de ruta (motivo M01) que provocó el retorno del vehículo al hub sin intento de entrega, debido al cierre de la Avenida Pajaritos [F1].  
- **Responsable:** LogiRuta, según el catálogo de responsabilidad para M01 [F8].  
- **Computa para SLA:** Sí (el hecho verifica “Computa para SLA: True”) [F1].  
- **Intentos de entrega:** No se registraron intentos (campo “Intentos de entrega: 0”). No existe fragmento que indique cuántos intentos quedan, por lo que no se menciona.

### 2. Acción operativa
1. **Reprogramar la entrega** con prioridad alta y generar una nueva fecha estimada de entrega.  
2. **Informar al cliente** la nueva fecha y ofrecer una disculpa formal.  
3. **Registrar incidente de SLA** por incumplimiento grave (> 72 h) [F4].  
4. **Escalar a N3 – Jefe de Operaciones** dentro de las 24 horas hábiles siguientes [F5].  
5. **Gestionar la compensación** correspondiente al tramo “más de 5 días” : reposición o reembolso del producto con el retailer y reembolso del despacho [F3]; la aprobación debe ser firmada por la Gerencia Comercial [F3].

- **Nivel de escalamiento:** N3 – Jefe de Operaciones, plazo máximo 24 h [F5].  
- **Compensación que corresponde:** reposición o reembolso del producto + reembolso del despacho, aprobada por Gerencia Comercial [F3].

### 3. Mensaje sugerido para el cliente
> Estimado/a cliente, le pedimos disculpas por el retraso en la entrega de su pedido LR‑2026‑004182. Debido a una incidencia en la ruta, su envío será reprogramado y estimamos que podrá recibirlo el **[nueva fecha estimada]**. Agradecemos su comprensión y quedamos a su disposición por el canal de atención [canal de atencion] para cualquier consulta.

### 4. Alertas
- **Riesgo contractual:** El retraso de 7 días supera las 72 h, lo que genera un incidente grave de SLA con posible penalización económica y riesgo de reclamo ante SERNAC [F4].  
- **Temporada alta:** El servicio ND no admite extensión de plazo en temporada alta y el retailer no informó una extensión al consumidor; por lo tanto, la fecha promesa original sigue vigente y el incumplimiento afecta el SLA [F6].  

### 5. Fuentes utilizadas
- **[F1]** CAT-OPS-007 – M01 – Congestión vial o sobrecarga de ruta.  
- **[F2]** SOP-OPS-014 – Matriz de decisión de acción operativa.  
- **[F3]** POL-COM-003 – Tabla de compensaciones al consumidor final.  
- **[F4]** SLA-COM-002 – Umbrales de incidente de SLA.  
- **[F5]** SOP-OPS-014 – Escalamiento.  
- **[F6]** SLA-COM-002 – Protocolo de peaks de demanda (temporada alta).  
- **[F8]** CAT-OPS-007 – Tabla resumen de responsabilidad.

## 6. Verificacion de coherencia (6/6)

| Verificacion | Resultado |
|---|---|
| Incluye citas [F#] (objetivo O2) | Cumple |
| Incluye mensaje sugerido para el cliente | Cumple |
| Atribuye la responsabilidad a LogiRuta | Cumple |
| Escala a Jefe de Operaciones o Gerencia | Cumple |
| Aplica compensacion del tramo (reembolso o reposicion) | Cumple |
| Recupera la politica de compensaciones POL-COM-003 | Cumple |
