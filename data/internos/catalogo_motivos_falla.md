---
documento: CAT-OPS-007
titulo: Catalogo de motivos de falla de entrega
version: 4.1
vigencia: 2026-01-15
area_responsable: Operaciones Ultima Milla
clasificacion: Interno
---

# CAT-OPS-007 — Catalogo de motivos de falla de entrega

> Documento interno simulado de LogiRuta SpA para la asignatura ISY0101.

Cada excepcion de entrega debe clasificarse con uno de los codigos de este catalogo. El codigo
determina la responsabilidad, el numero de reintentos permitidos y si corresponde compensacion.

## M01 — Congestion vial o sobrecarga de ruta

- **Descripcion**: la ruta no alcanzo a completar las entregas planificadas por congestion, cierre de vias o exceso de paradas asignadas.
- **Responsabilidad**: LogiRuta (planificacion de ruta).
- **Computa para SLA**: Si.
- **Reintentos**: reprogramacion automatica al dia habil siguiente.
- **Compensacion**: segun tramo de retraso en POL-COM-003.
- **Senales tipicas en tracking**: estado `EN_RUTA` con retorno a hub sin intento registrado, multiples envios de la misma ruta afectados el mismo dia.
- **Accion correctiva recomendada**: rebalancear la ruta y revisar la densidad de paradas por vehiculo.

## M02 — Cliente ausente

- **Descripcion**: el transportista llego a la direccion informada y no encontro receptor.
- **Responsabilidad**: Consumidor.
- **Computa para SLA**: No.
- **Reintentos**: hasta 3 intentos, con 24 a 48 horas habiles entre cada uno.
- **Compensacion**: no corresponde.
- **Senales tipicas en tracking**: estado `INTENTO_FALLIDO` con intentos 1 a 3 y observacion de domicilio sin moradores.
- **Accion correctiva recomendada**: coordinar ventana horaria con el consumidor u ofrecer retiro en punto de conveniencia.

## M03 — Direccion incompleta o erronea

- **Descripcion**: la direccion carece de numero, departamento, comuna o contiene datos inconsistentes.
- **Responsabilidad**: Consumidor o retailer (origen del dato).
- **Computa para SLA**: No.
- **Reintentos**: hasta 2 intentos, solo despues de validar la direccion con el consumidor.
- **Compensacion**: no corresponde.
- **Senales tipicas en tracking**: estado `DIRECCION_OBSERVADA`, observacion de direccion sin numero o comuna que no coincide con el hub asignado.
- **Accion correctiva recomendada**: contactar al consumidor para validar direccion. Si no responde en 48 horas, devolucion al origen.

## M04 — Quiebre de capacidad del hub

- **Descripcion**: el volumen recibido excedio la capacidad de clasificacion o la flota disponible del hub.
- **Responsabilidad**: LogiRuta (planificacion de capacidad).
- **Computa para SLA**: Si.
- **Reintentos**: reprogramacion priorizada por tier de SLA del retailer.
- **Compensacion**: segun tramo de retraso en POL-COM-003.
- **Senales tipicas en tracking**: estado `EN_HUB` por mas de 48 horas sin asignacion a ruta, concentracion de envios detenidos en el mismo hub y fecha.
- **Accion correctiva recomendada**: activar red de transportistas freelance y derivar carga a hub alternativo.

## M05 — Rechazo del consumidor

- **Descripcion**: el consumidor se niega a recibir el paquete.
- **Responsabilidad**: Consumidor.
- **Computa para SLA**: No.
- **Reintentos**: no se reprograma. Se inicia devolucion al origen.
- **Compensacion**: no corresponde.
- **Senales tipicas en tracking**: estado `RECHAZADO` con observacion de negativa de recepcion.
- **Accion correctiva recomendada**: notificar al retailer para gestion comercial del caso.

## M06 — Zona de riesgo o acceso restringido

- **Descripcion**: la direccion se ubica en zona con restriccion de acceso, condominio sin autorizacion o area declarada de riesgo para el transportista.
- **Responsabilidad**: Compartida (contexto externo).
- **Computa para SLA**: No, si existe declaracion formal del jefe de hub.
- **Reintentos**: hasta 2 intentos, solo en horario diurno.
- **Compensacion**: no corresponde, salvo retraso superior a 72 horas por mala gestion interna.
- **Senales tipicas en tracking**: estado `INTENTO_FALLIDO` con observacion de acceso no autorizado o zona restringida.
- **Accion correctiva recomendada**: coordinar entrega en punto de retiro acordado.

## M07 — Paquete danado o perdido en red

- **Descripcion**: el paquete sufrio dano o no es localizable en la red logistica.
- **Responsabilidad**: LogiRuta.
- **Computa para SLA**: Si, como incidente grave.
- **Reintentos**: no aplica. Se activa protocolo de siniestro.
- **Compensacion**: cobertura del valor declarado con tope de 15 UF, mas reembolso del despacho.
- **Senales tipicas en tracking**: estado `INCIDENTE` sin movimiento por mas de 72 horas.
- **Accion correctiva recomendada**: escalar a Jefe de Operaciones y abrir siniestro con el retailer.

## Tabla resumen de responsabilidad

| Codigo | Motivo | Responsable | Computa SLA | Compensacion posible |
|---|---|---|---|---|
| M01 | Congestion vial o sobrecarga de ruta | LogiRuta | Si | Si |
| M02 | Cliente ausente | Consumidor | No | No |
| M03 | Direccion incompleta o erronea | Consumidor / Retailer | No | No |
| M04 | Quiebre de capacidad del hub | LogiRuta | Si | Si |
| M05 | Rechazo del consumidor | Consumidor | No | No |
| M06 | Zona de riesgo o acceso restringido | Compartida | No | Excepcional |
| M07 | Paquete danado o perdido | LogiRuta | Si | Si |
