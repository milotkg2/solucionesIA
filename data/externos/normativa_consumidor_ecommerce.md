---
documento: EXT-NORM-002
titulo: Marco normativo chileno aplicable a plazos de entrega en comercio electronico
tipo_fuente: Externa / Normativa
entidad: Biblioteca del Congreso Nacional de Chile / SERNAC
fecha_recopilacion: 2026-09-23
clasificacion: Publico
---

# EXT-NORM-002 — Marco normativo aplicable a plazos de entrega

> Sintesis de orientacion elaborada con fines academicos para la asignatura ISY0101. No
> constituye asesoria legal. Para efectos formales debe consultarse el texto vigente de la
> norma en la fuente oficial indicada.

## 1. Norma base

**Ley N° 19.496, sobre proteccion de los derechos de los consumidores** (LPC).
Texto oficial: https://www.bcn.cl/leychile/navegar?idNorma=61438

Principio central aplicable al caso: el proveedor debe **respetar las condiciones ofrecidas** al
consumidor al momento de la contratacion. El plazo de entrega informado en la compra forma
parte de esas condiciones y su incumplimiento habilita al consumidor a exigir el cumplimiento
de lo ofrecido o, en su caso, la restitucion de lo pagado.

## 2. Modificaciones relevantes para comercio electronico

**Ley N° 21.398 (conocida como Ley Pro Consumidor)** introdujo y reforzo obligaciones aplicables
a las compras a distancia, entre ellas:

- Informar de manera clara, veraz y oportuna las condiciones de despacho y el plazo de entrega.
- Mantener canales de atencion efectivos y trazables para consultas y reclamos.
- Entregar informacion sobre el estado del pedido cuando el consumidor lo solicita.
- Restricciones a la modificacion unilateral de las condiciones pactadas.

Texto oficial: https://www.bcn.cl/leychile/navegar?idNorma=1169268

## 3. Reglas practicas derivadas para la operacion logistica

| Regla practica | Implicancia operativa para LogiRuta |
|---|---|
| El plazo comprometido con el consumidor es el exigible | La fecha promesa registrada en el sistema es el dato de referencia para evaluar retraso, incluso si el plazo interno es distinto |
| La informacion de estado debe estar disponible y ser comprensible | El tracking debe traducirse a lenguaje claro en la respuesta al consumidor |
| La responsabilidad frente al consumidor recae en el proveedor que vendio | El operador logistico responde ante el retailer por contrato; el retailer responde ante el consumidor por ley |
| Las condiciones ofrecidas no pueden modificarse unilateralmente | Una extension de plazo por temporada solo es valida si fue informada al consumidor antes de la compra |
| El consumidor conserva su derecho legal independiente de la compensacion comercial | Un cupon o gesto comercial no extingue el derecho del consumidor |

## 4. Limite de uso en la solucion

El agente de IA de este proyecto **no emite calificaciones juridicas ni determina
responsabilidad legal**. Utiliza esta fuente unicamente para:

1. Recordar al operador que la fecha promesa informada al consumidor es el compromiso exigible.
2. Advertir cuando una extension de plazo por temporada no fue informada al consumidor.
3. Sugerir escalamiento cuando el caso presenta riesgo de reclamo formal.

Cualquier caso con riesgo legal debe derivarse al area correspondiente de la organizacion.

## 5. Fuentes para verificacion

- Biblioteca del Congreso Nacional de Chile, Ley N° 19.496: https://www.bcn.cl/leychile/navegar?idNorma=61438
- Biblioteca del Congreso Nacional de Chile, Ley N° 21.398: https://www.bcn.cl/leychile/navegar?idNorma=1169268
- SERNAC, informacion al consumidor sobre compras por internet: https://www.sernac.cl
