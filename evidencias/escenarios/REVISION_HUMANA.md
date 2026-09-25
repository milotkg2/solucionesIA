# Revisión humana de los escenarios

Las verificaciones automáticas de `RESUMEN.md` (34/34) comprueban patrones de texto y
fragmentos recuperados. No detectan si una afirmación citada está realmente respaldada por el
fragmento. Por eso cada respuesta se revisó manualmente contra las fuentes.

> Pendiente: validación final por ambos integrantes antes de la entrega.

## Resultado por escenario

| Escenario | Conclusión central | Revisión humana |
|---|---|---|
| ESC-01 (M01, 7 días) | Responsable LogiRuta, escalamiento y compensación del tramo > 5 días | Correcto |
| ESC-02 (M02, 2 intentos) | Sin compensación, queda 1 intento, RTO si falla | Correcto en lo central. **Defecto:** afirma que tras el tercer intento fallido "se escalará a Jefe de Operaciones" citando [F2]; el SOP-OPS-014 §4 indica devolución al origen y notificación al retailer, no escalamiento |
| ESC-03 (M03) | Validar dirección en 48 h, sin compensación, RTO | Correcto |
| ESC-04 (M04, ElectroMax SD) | Responsable LogiRuta, penalización Tier 1, escalamiento, compensación | Correcto |
| ESC-05 (temporada alta) | Extensión no válida por no informarse; rige fecha promesa; SLA leve | Correcto en lo central. **Defecto:** recupera EXT-NORM-002 [F7] pero no lo cita; menciona riesgo de reclamo SERNAC sin cita |
| ESC-06 (política general) | 3 intentos, sin compensación | Correcto |
| ESC-07 (código inexistente) | No genera diagnóstico ni llama al LLM | Correcto |

## Métricas frente a los objetivos de la propuesta

| Objetivo | Meta | Resultado |
|---|---|---|
| O1 — Causa coherente y citada | ≥ 80% de casos | 5/5 casos de diagnóstico con causa y responsable correctos (100%) |
| O2 — Respuestas con referencia a fuente | 100% | 6/6 respuestas generadas con citas [F#]. 2 afirmaciones secundarias sin respaldo exacto (ESC-02, ESC-05) |
| O3 — Acción alineada al SOP | ≥ 4/5 escenarios | 5/5 en la acción principal |
| O4 — De 4 sistemas a 1 consulta | 1 consulta | Cada escenario se resuelve con una consulta; latencia media 14,1 s |

## Limitaciones observadas

1. **Citas que no respaldan exactamente la afirmación.** El modelo puede agregar una
   inferencia plausible y asignarle una cita cercana (ESC-02). Las verificaciones automáticas
   por patrones no lo detectan; se requiere revisión humana o una verificación de fidelidad
   (por ejemplo, un segundo paso que compare cada afirmación con su fragmento).
2. **Fragmento recuperado no implica fragmento usado.** En ESC-05 la normativa externa llegó
   al contexto, pero el modelo prefirió la regla interna equivalente y no la citó.
3. **Verificaciones heurísticas.** Los patrones de texto pueden aprobar respuestas mal
   redactadas o fallar ante sinónimos; son apoyo, no reemplazo del juicio humano.
