---
documento: SOP-OPS-014
titulo: Procedimiento de gestion de excepciones y reintentos de entrega
version: 3.2
vigencia: 2026-01-15
area_responsable: Mesa de Control / Operaciones Ultima Milla
clasificacion: Interno
---

# SOP-OPS-014 — Gestion de excepciones y reintentos de entrega

> Documento interno simulado de LogiRuta SpA, elaborado con fines academicos para la asignatura ISY0101.

## 1. Proposito

Establecer el procedimiento obligatorio que debe seguir la Mesa de Control cuando un envio
presenta una excepcion de entrega, es decir, cuando el envio no pudo ser entregado en la
fecha comprometida o presenta un evento que impide completar la entrega en el primer intento.

## 2. Alcance

Aplica a todos los envios B2C gestionados desde los hubs Quilicura, Pudahuel y San Bernardo,
tanto con flota propia como con transportistas freelance de la red de apoyo.

## 3. Definiciones operativas

- **Fecha promesa**: fecha maxima de entrega informada al consumidor al momento de la compra.
- **Excepcion de entrega**: evento que interrumpe el ciclo normal de entrega y requiere decision humana o automatizada.
- **Reintento**: nuevo intento de entrega programado luego de una excepcion.
- **Retraso confirmado**: envio cuya fecha real de entrega supera la fecha promesa, o que a la fecha de consulta ya supero la fecha promesa sin entregar.
- **Devolucion al origen (RTO)**: retorno del paquete al retailer tras agotar los intentos permitidos.

## 4. Regla de intentos de entrega

| Situacion | Intentos maximos | Plazo entre intentos | Responsable |
|---|---|---|---|
| Cliente ausente (motivo M02) | 3 intentos | 24 a 48 horas habiles | Hub de origen |
| Direccion incompleta o erronea (motivo M03) | 2 intentos, previa validacion de direccion | 48 horas habiles | Mesa de Control |
| Rechazo del cliente (motivo M05) | 1 intento, no se reprograma | No aplica | Hub de origen |
| Zona de riesgo o acceso restringido (motivo M06) | 2 intentos en horario diurno | 48 horas habiles | Jefe de Hub |
| Congestion vial o sobrecarga de ruta (motivo M01) | Reprogramacion automatica al dia habil siguiente | 24 horas | Planificacion |
| Quiebre de capacidad del hub (motivo M04) | Reprogramacion con priorizacion por SLA | 24 a 72 horas | Jefe de Hub |

**Regla critica:** agotados los intentos permitidos sin entrega efectiva, el envio pasa a estado
`DEVUELTO_ORIGEN` dentro de las 24 horas siguientes y se notifica al retailer el mismo dia habil.

## 5. Flujo obligatorio de atencion de una excepcion

1. **Identificar el envio** por codigo de seguimiento y verificar estado y numero de intentos.
2. **Clasificar el motivo** segun el catalogo de motivos de falla (documento CAT-OPS-007).
3. **Verificar el SLA aplicable** al retailer en la matriz SLA-COM-002, porque el plazo de
   respuesta y la prioridad de reprogramacion dependen del contrato.
4. **Determinar si existe retraso confirmado** comparando fecha promesa con fecha real o fecha actual.
5. **Decidir la accion operativa** segun la seccion 4 y la seccion 6.
6. **Comunicar al cliente y al retailer** dentro del plazo de respuesta contractual.
7. **Registrar la gestion** en la bitacora del envio, indicando motivo, accion y responsable.

Ninguna respuesta al cliente puede emitirse sin haber ejecutado los pasos 1 a 4.

## 6. Matriz de decision de accion operativa

| Condicion detectada | Accion operativa obligatoria |
|---|---|
| Retraso menor o igual a 24 horas, causa externa (congestion, clima) | Reprogramar entrega e informar nueva fecha al cliente. No corresponde compensacion automatica. |
| Retraso mayor a 24 horas y menor o igual a 72 horas | Reprogramar con prioridad alta, informar al retailer y evaluar compensacion segun POL-COM-003. |
| Retraso mayor a 72 horas | Escalamiento obligatorio a Jefe de Operaciones y aplicacion de compensacion segun POL-COM-003. |
| Causa atribuible a LogiRuta (motivos M01, M04) con incumplimiento de SLA | Compensacion obligatoria y registro de incidente de SLA. |
| Causa atribuible al consumidor (motivos M02, M03, M05) | Reintento segun seccion 4. No corresponde compensacion. |
| Direccion incompleta | Contactar al cliente para validar direccion antes de reprogramar. Si no hay respuesta en 48 horas, RTO. |
| Tres o mas intentos fallidos | Devolucion al origen y notificacion al retailer el mismo dia habil. |

## 7. Escalamiento

| Nivel | Cuando se activa | Responsable | Plazo maximo |
|---|---|---|---|
| N1 — Mesa de Control | Toda excepcion registrada | Analista de turno | 4 horas habiles |
| N2 — Jefe de Hub | Retraso mayor a 48 horas o quiebre de capacidad | Jefe de Hub | 8 horas habiles |
| N3 — Jefe de Operaciones | Retraso mayor a 72 horas o riesgo de penalizacion contractual | Jefe de Operaciones | 24 horas habiles |
| N4 — Gerencia Comercial | Reclamo formal ante SERNAC o riesgo de perdida de contrato | Gerente Comercial | 48 horas habiles |

## 8. Prohibiciones

- Prohibido informar al cliente una nueva fecha de entrega sin confirmacion de Planificacion.
- Prohibido cerrar una excepcion sin registrar el motivo de falla codificado.
- Prohibido ofrecer compensaciones no contempladas en POL-COM-003.
- Prohibido declarar "entregado" un envio sin evidencia de recepcion.

## 9. Trazabilidad

Toda respuesta emitida por la Mesa de Control debe poder justificarse indicando el documento
y la seccion que respalda la decision. Las respuestas sin respaldo documental se consideran
no conformes en la auditoria interna trimestral.
