---
documento: SLA-COM-002
titulo: Matriz de niveles de servicio (SLA) por retailer
version: 2.4
vigencia: 2026-02-01
area_responsable: Gerencia Comercial
clasificacion: Interno / Confidencial comercial
---

# SLA-COM-002 — Matriz de niveles de servicio por retailer

> Documento interno simulado de LogiRuta SpA para la asignatura ISY0101.

## 1. Proposito

Definir los plazos de entrega comprometidos, los umbrales de cumplimiento y las penalizaciones
acordadas con cada retailer cliente de LogiRuta SpA.

## 2. Plazos comprometidos por tipo de servicio

| Servicio | Codigo | Plazo comprometido (dias habiles) | Cobertura |
|---|---|---|---|
| Express same day | SD | Mismo dia, compra antes de 12:00 | Santiago urbano |
| Express next day | ND | 1 dia habil | Region Metropolitana |
| Estandar | ST | 3 dias habiles | Region Metropolitana |
| Estandar extendido | SE | 5 dias habiles | Comunas periurbanas |

## 3. Matriz contractual por retailer

| Retailer | Tier | Servicio contratado | Cumplimiento minimo (OTD) | Plazo de respuesta a consultas | Penalizacion por incumplimiento |
|---|---|---|---|---|---|
| TiendaNova | Tier 1 | ND / ST | 96% | 2 horas habiles | 3% del valor del flete mensual por cada punto bajo 96% |
| MegaHogar | Tier 1 | ST / SE | 95% | 4 horas habiles | 2,5% del valor del flete mensual por cada punto bajo 95% |
| ZapatoExpress | Tier 2 | ND | 93% | 8 horas habiles | 1,5% del valor del flete mensual por cada punto bajo 93% |
| ElectroMax | Tier 1 | SD / ND | 97% | 2 horas habiles | 4% del valor del flete mensual por cada punto bajo 97%, mas nota de incidente |
| DecoCasa | Tier 3 | ST | 90% | 24 horas habiles | Sin penalizacion economica, solo plan de mejora |

**OTD (On Time Delivery)**: porcentaje de envios entregados en o antes de la fecha promesa,
medido mensualmente por retailer.

## 4. Umbrales de incidente de SLA

| Nivel de incidente | Condicion | Consecuencia contractual |
|---|---|---|
| Leve | Retraso de hasta 24 horas sobre la fecha promesa | Registro interno, sin penalizacion individual |
| Moderado | Retraso entre 24 y 72 horas | Informe al retailer dentro del plazo de respuesta contractual |
| Grave | Retraso superior a 72 horas, o perdida del paquete | Penalizacion economica y nota de incidente formal |
| Critico | Incumplimiento reiterado en retailer Tier 1 durante un mismo mes | Revision del contrato y plan de remediacion obligatorio |

## 5. Exclusiones de responsabilidad

No se computan como incumplimiento de SLA los retrasos originados por:

- Datos de direccion incorrectos o incompletos entregados por el retailer o el consumidor (motivo M03).
- Ausencia reiterada del consumidor en la direccion informada (motivo M02).
- Rechazo del producto por parte del consumidor (motivo M05).
- Eventos de fuerza mayor declarados formalmente: catastrofes naturales, cortes de ruta por
  autoridad, paros o manifestaciones que bloqueen el acceso.

Los retrasos por congestion vial ordinaria (motivo M01) y por quiebre de capacidad del hub
(motivo M04) **si** se computan como incumplimiento de SLA, porque son responsabilidad de
la planificacion de LogiRuta.

## 6. Protocolo de peaks de demanda

Durante los periodos declarados de alta demanda (CyberDay, Black Friday, Navidad), aplica el
anexo de temporada: los plazos comprometidos se extienden en 1 dia habil para los servicios
ST y SE, siempre que el retailer haya sido notificado con al menos 10 dias de anticipacion y
haya informado el nuevo plazo al consumidor en el momento de la compra.

Si el retailer no informo el plazo extendido al consumidor, la fecha promesa original se
mantiene vigente para efectos de SLA y de la respuesta al consumidor.

Los servicios SD y ND **no admiten extension de plazo** en ninguna temporada.
