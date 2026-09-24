# Guía de estudio técnica — Agente de diagnóstico de retrasos con RAG

**Asignatura:** ISY0101 — Ingeniería de Soluciones con IA
**Proyecto:** LogiRuta SpA — Mesa de Control asistida por IA
**Equipo:** Camilo Romero · Eder Valdivia
**Propósito de este documento:** explicar **qué** estamos construyendo, **cómo** funciona,
**con qué tecnologías** y sobre todo **por qué** se tomó cada decisión. Está escrito para
estudiar y para poder defender el proyecto en la presentación del 26/09.

> Este documento es material de apoyo al estudio. Las conclusiones, justificaciones finales
> del informe y las reflexiones personales deben ser redactadas por el equipo, según lo exige
> la pauta de la evaluación.

---

## 0. Cómo leer esta guía

| Si quieres... | Ve a la sección |
|---|---|
| Instalar el proyecto y probarlo en tu PC (Eder / Camilo) | 11 |
| Entender el vocabulario (LLM, RAG, embedding, chunk) | 2 |
| Entender qué problema resolvemos | 3 |
| Entender la arquitectura completa | 4 |
| Saber por qué elegimos cada tecnología | 5 |
| Seguir una consulta real paso a paso | 6 |
| Saber qué hace cada archivo del repositorio | 7 |
| Saber qué está listo y qué falta | 8 |
| Prepararte para las preguntas de la defensa | 9 |

---

## 1. Qué estamos construyendo (en una frase)

Un **agente de IA** que recibe una consulta en lenguaje natural sobre un envío atrasado,
consulta los datos reales del envío, recupera las políticas internas y la normativa externa
que aplican al caso, y devuelve un **diagnóstico de causa, la acción operativa que corresponde
según el procedimiento, y un mensaje listo para enviar al cliente**, citando en qué documento
y sección se basa cada afirmación.

La frase clave para la defensa: **no construimos un chatbot, construimos un asistente de
decisión trazable**. La diferencia es que cada respuesta puede auditarse hasta el documento
que la respalda.

---

## 2. Glosario mínimo (el vocabulario que hay que dominar)

| Término | Qué es | Cómo aparece en nuestro proyecto |
|---|---|---|
| **LLM** (Large Language Model) | Modelo de lenguaje entrenado para predecir texto. Sabe redactar y razonar sobre lenguaje, pero **no conoce** los datos privados de la empresa. | Groq `openai/gpt-oss-120b` (principal). Gemini y Ollama como respaldo. Redacta el diagnóstico y el mensaje al cliente. |
| **Prompt** | Instrucción de texto que se le entrega al LLM. Define rol, contexto, tarea, formato y restricciones. | Carpeta `prompts/`. Es un componente de ingeniería, no un texto improvisado. |
| **Alucinación** | Cuando el LLM afirma algo falso con tono seguro (inventa un plazo, una política, una compensación). | Es **el riesgo central** del proyecto. Lo combatimos con RAG y con cálculos deterministas. |
| **RAG** (Retrieval-Augmented Generation) | Técnica que consiste en **recuperar** fragmentos de documentos relevantes y **entregárselos al LLM** dentro del prompt, para que responda basándose en ellos y no en su memoria. | Todo el módulo `src/retrieval.py` + `src/ingest.py`. |
| **Chunk** (fragmento) | Trozo de un documento. Los documentos se parten porque no cabe todo en el prompt y porque trozos pequeños son más precisos al buscar. | Tenemos **43 fragmentos** indexados. |
| **Embedding** | Representación numérica (un vector de números) del significado de un texto. Textos con significado parecido quedan cerca en el espacio vectorial. | `nomic-embed-text` genera vectores de **768 dimensiones**. |
| **Vector store** | Base de datos que guarda esos vectores y permite buscar "los más parecidos". | `data/vectorstore/` (índice simple de LlamaIndex persistido en disco). |
| **Búsqueda densa / semántica** | Buscar por significado usando embeddings. Encuentra paráfrasis. | Uno de nuestros dos recuperadores. |
| **BM25 / búsqueda léxica** | Algoritmo clásico que busca por coincidencia de palabras, pesando qué tan raras son. Encuentra códigos y términos exactos. | El otro recuperador. |
| **Búsqueda híbrida** | Usar ambas y combinar resultados. | Nuestra estrategia de recuperación. |
| **RRF** (Reciprocal Rank Fusion) | Fórmula para combinar dos listas de resultados usando la **posición** en cada lista, no el puntaje crudo. | Implementada a mano en `src/retrieval.py`. |
| **top-k** | Cuántos fragmentos se recuperan. | 6 densos + 6 léxicos → 5 finales. |
| **Agente** | Sistema que no solo genera texto: **decide qué pasos ejecutar** y usa **herramientas** (consultar una base de datos, buscar en documentos) para cumplir un objetivo. | `src/agent.py`: detecta el envío, llama la herramienta de tracking, calcula hechos, consulta el RAG y recién entonces genera. |
| **Herramienta** (tool) | Función que el agente puede invocar para obtener información o actuar. | `consultar_envio()` en `src/tracking.py` sobre el CSV. |
| **SLA** (Service Level Agreement) | Acuerdo de nivel de servicio: el plazo y la calidad comprometidos por contrato. | `data/internos/matriz_sla_retailers.md`. |
| **OTD** (On Time Delivery) | % de envíos entregados a tiempo. Es el KPI que mide el problema. | Columna de cumplimiento mínimo en la matriz SLA. |

### La idea que hay que entender de RAG

Un LLM por sí solo es como un profesional muy elocuente que **nunca leyó los manuales de tu
empresa**. Si le preguntas "¿cuántos reintentos permite el procedimiento?", va a inventar una
cifra plausible. RAG resuelve esto así:

```
Pregunta → buscar en los documentos → pegar los fragmentos encontrados en el prompt →
el LLM responde usando SOLO esos fragmentos → la respuesta cita su fuente
```

Es equivalente a darle el manual abierto en la página correcta antes de que responda.

---

## 3. El problema y cómo la solución lo ataca

### 3.1 El problema organizacional

La Mesa de Control de LogiRuta SpA no logra diagnosticar a tiempo por qué se atrasó un envío
ni responder de forma consistente, **porque la información está dispersa en cuatro lugares**:
el sistema de tracking, el procedimiento de excepciones, la matriz de SLA por retailer y la
política de compensaciones. A eso se suma la normativa de protección al consumidor.

Evidencia externa que justifica la relevancia: el retraso en la entrega concentró cerca del
**78% de los reclamos navideños ante SERNAC en 2024** (1.354 de 1.731 casos).

### 3.2 Por qué es un problema adecuado para IA + LLM + RAG

| Característica del problema | Por qué habilita esta solución |
|---|---|
| La consulta llega en lenguaje natural y variable | Un LLM interpreta la intención sin necesidad de formularios rígidos |
| La respuesta correcta **está escrita** en documentos internos | RAG puede recuperarla en vez de que el modelo la invente |
| La decisión requiere **combinar** varias fuentes | Un agente orquesta múltiples pasos y fuentes en una sola consulta |
| La respuesta debe ser auditable | Las citas de RAG dan trazabilidad documento + sección |
| Hay reglas duras (plazos, tramos, responsabilidad) | Se calculan en código, no se dejan al LLM |

### 3.3 Objetivo medible que persigue el sistema

Reemplazar la búsqueda manual en 4 sistemas por **una sola consulta**, entregando diagnóstico,
acción y borrador de respuesta con **100% de trazabilidad a la fuente**.

---

## 4. Arquitectura de la solución

### 4.1 Diagrama lógico

```
                        ┌──────────────────────────────┐
   Operador de la       │   INTERFAZ (Streamlit)       │
   Mesa de Control ───► │   consulta en lenguaje       │
                        │   natural + panel de         │
                        │   evidencia                  │
                        └──────────────┬───────────────┘
                                       │
                        ┌──────────────▼───────────────┐
                        │   AGENTE (orquestador)       │
                        │   src/agent.py               │
                        └───┬───────────┬──────────────┘
                            │           │
         ┌──────────────────┘           └──────────────────┐
         │ 1. ¿La consulta trae                            │ 3. Construye consultas
         │    código de envío?                             │    de recuperación
         ▼                                                 ▼
┌────────────────────────┐                    ┌─────────────────────────────┐
│ HERRAMIENTA DE DATOS   │                    │ PIPELINE RAG                │
│ src/tracking.py        │                    │ src/retrieval.py            │
│                        │                    │                             │
│ • Lee envios.csv y     │                    │ ┌─────────────┬───────────┐ │
│   eventos_tracking.csv │                    │ │ Búsqueda    │ Búsqueda  │ │
│ • Calcula días de      │                    │ │ densa       │ léxica    │ │
│   retraso, tramo y     │                    │ │ (embeddings)│ (BM25)    │ │
│   responsabilidad      │                    │ └──────┬──────┴─────┬─────┘ │
│   EN CÓDIGO            │                    │        └─── RRF ─────┘      │
└───────────┬────────────┘                    └───────────┬─────────────────┘
            │ 2. Hechos verificados                       │ 4. Fragmentos + citas
            │                                             │
            └──────────────────┬──────────────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │  PROMPT ENSAMBLADO   │
                    │  rol + hechos +      │
                    │  fragmentos + reglas │
                    │  de formato          │
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────────┐        ┌─────────────────────┐
                    │  CAPA DE LLM         │◄──────►│ Groq gpt-oss-120b   │
                    │  src/config.py       │        │ (nube, principal)   │
                    │  intercambiable      │        ├─────────────────────┤
                    │                      │◄──────►│ Gemini / Ollama     │
                    └──────────┬───────────┘        │ (respaldos)         │
                               ▼                    └─────────────────────┘
                    ┌──────────────────────────────────────────┐
                    │  RESPUESTA: diagnóstico + acción         │
                    │  operativa + mensaje al cliente + citas  │
                    └──────────────────────────────────────────┘

  FUENTES DE INFORMACIÓN
  ├── Internas  → SOP-OPS-014, SLA-COM-002, POL-COM-003, CAT-OPS-007  (indexadas en RAG)
  ├── Internas  → envios.csv, eventos_tracking.csv  (consulta determinista, NO RAG)
  └── Externas  → EXT-SERNAC-001, EXT-NORM-002  (indexadas en RAG)
```

### 4.2 Qué hace cada componente y por qué existe

| Componente | Función | Por qué es necesario |
|---|---|---|
| **Interfaz Streamlit** | Recibe la consulta y muestra la respuesta junto a los fragmentos recuperados con sus puntajes | La transparencia es requisito: el operador debe poder ver en qué se basó el sistema. También genera las capturas de evidencia. |
| **Agente orquestador** | Decide la secuencia de pasos, invoca herramientas, ensambla el prompt | Sin esta capa solo tendríamos un chat genérico. Es lo que convierte al LLM en una solución operativa. |
| **Herramienta de tracking** | Consulta determinista del CSV y **cálculo en código** del retraso, el tramo y la responsabilidad | Los números no se pueden alucinar. Ver sección 5.6. |
| **Pipeline RAG** | Recupera los fragmentos normativos y de procedimiento aplicables | Es lo que ancla la respuesta en las políticas reales de la organización. |
| **Capa de LLM** | Abstrae el proveedor detrás de una interfaz común | Permite cambiar de motor por variable de entorno, sin reescribir el pipeline. Ver 5.1. |

### 4.3 El punto importante de la arquitectura

Observa el orden: **primero los datos duros, después la recuperación, y el LLM al final**.
El LLM nunca decide cuántos días de retraso hay ni si corresponde compensación: recibe esos
hechos ya calculados y su trabajo es **redactar y fundamentar**, no calcular.

Esta inversión de responsabilidades es la decisión de diseño más importante del proyecto.

---

## 5. Decisiones técnicas, alternativas y fundamentos

Esta sección es la más importante para la defensa, porque el 10% de la nota corresponde a
*Fundamentación de decisiones de diseño* y otro 15% a *Arquitectura*.

### 5.1 Motor de LLM: Groq en la nube como principal; Gemini y Ollama como respaldo

**Qué hicimos:** una capa de abstracción (`construir_llm()` en `src/config.py`) que devuelve
el LLM según la variable de entorno `LLM_PROVEEDOR`. Proveedores soportados: `groq` (principal),
`gemini` y `ollama` (respaldos). El modelo actual por defecto es `openai/gpt-oss-120b` vía Groq.

**Por qué descartamos Ollama como motor principal (evidencia medida):**

Hardware de desarrollo: Intel Core i5-7400 (4 núcleos), 8 GB de RAM, Radeon RX 570 (no utilizable
por Ollama en Windows → inferencia 100% CPU).

| Prueba realizada | Resultado medido |
|---|---|
| Llama 3.1 8B, pregunta corta sin contexto (Ollama) | **284,6 segundos** |
| Llama 3.2 3B, con contexto RAG de ~5.000 caracteres (Ollama) | **211,9 segundos** |
| Groq `openai/gpt-oss-120b`, pregunta corta | **~1–2 segundos** |
| Embedding `nomic-embed-text` (modelo cargado) | **~1 segundo** |
| Indexación completa del corpus (43 fragmentos) | **15 segundos** |

Además, el modelo local de 3B **falló en calidad**: ante un caso de cliente ausente (M02)
inventó una "compensación obligatoria", contradiciendo el catálogo interno.

**Por qué no quedó Gemini como principal:** la cuenta de Google AI Studio del equipo autentica
y lista modelos, pero al generar responde `403 PERMISSION_DENIED` en dos proyectos distintos
(bloqueo a nivel de cuenta/región, no de clave mal escrita). Por eso se migró a Groq.

**Por qué conservamos Gemini y Ollama en el código:** demuestran que la arquitectura no está
acoplada a un proveedor. Cambiar el motor es una variable de entorno, no un rediseño.

**Regla del equipo sobre claves:** cada integrante usa **su propia** `GROQ_API_KEY` en un
archivo `.env` local. El `.env` **no se versiona** (repo público).

**Alternativas descartadas:**

| Alternativa | Por qué se descartó |
|---|---|
| Solo Ollama local | Latencia (~3,5 min) y calidad insuficientes |
| Gemini como principal | Bloqueo 403 en la cuenta del equipo |
| OpenAI / GPT de pago | Requiere tarjeta; Groq gratuito cubre la demo |
| Ajuste fino (fine-tuning) | Fuera de alcance; además RAG es la técnica correcta cuando las políticas cambian |

### 5.2 Framework: LlamaIndex

**Por qué:** está especializado precisamente en la etapa que nos interesa (ingesta, indexación
y recuperación), trae los conectores de Groq, Ollama, Gemini y BM25 como módulos independientes, y
maneja los metadatos por fragmento, que es lo que nos permite citar documento y sección.

**Alternativas descartadas:**

| Alternativa | Por qué se descartó |
|---|---|
| LangChain | Equivalente en capacidades, pero su capa de abstracción es más amplia y opaca para lo que necesitamos; LlamaIndex está más enfocado en RAG |
| Todo desde cero con NumPy | Educativo pero perderíamos tiempo reimplementando parsers y persistencia sin ganar puntos de evaluación |

**Importante para la defensa:** aunque usamos el framework, **la fusión de resultados la
implementamos nosotros** (sección 5.4), justamente para no depender de un componente cerrado
en la parte que tenemos que explicar.

### 5.3 Embeddings locales con `nomic-embed-text`

**Por qué local, si el LLM es en la nube:** porque la economía de cómputo es distinta. La
indexación ocurre **una sola vez** (15 segundos para todo el corpus) y embeber una consulta
toma ~1 segundo. La lentitud del equipo no afecta la experiencia, y a cambio obtenemos:

- Costo cero y sin límites de cuota.
- El pipeline de recuperación **funciona sin internet**.
- Los documentos internos de la empresa nunca salen del equipo, lo que es coherente con la
  restricción de confidencialidad del caso (la matriz de SLA está clasificada como
  confidencial comercial).

Ese último punto es un argumento fuerte: **la fuente confidencial se procesa localmente**.

### 5.4 Recuperación híbrida (densa + BM25) fusionada con RRF

**Qué hicimos:** dos recuperadores en paralelo sobre los mismos 43 fragmentos, y fusión por
Reciprocal Rank Fusion.

**Por qué híbrida, con ejemplos de nuestro propio corpus:**

| Tipo de consulta | Ejemplo real | Qué recuperador gana |
|---|---|---|
| Contiene códigos o identificadores | "¿cuántos reintentos permite el motivo **M02**?" | **BM25**: `M02` es un token exacto y raro; los embeddings lo diluyen |
| Paráfrasis del lenguaje del usuario | "¿me devuelven la plata del despacho?" | **Densa**: el documento dice "reembolso del costo de despacho", sin ninguna palabra en común |

Nuestro corpus está **lleno** de identificadores (`M01` a `M07`, `SOP-OPS-014`, `SLA-COM-002`,
`POL-COM-003`, `LR-2026-004182`, servicios `SD`/`ND`/`ST`/`SE`). Un sistema solo denso fallaría
en las consultas más frecuentes de un operador.

**Cómo funciona RRF (hay que saber explicar esto):**

```
score_RRF(fragmento) = Σ  1 / (K + posición_en_esa_lista)
                    listas
```

con `K = 60`. Se usa la **posición** (rank) y no el puntaje crudo, porque los puntajes de
BM25 y de similitud coseno están en escalas distintas y no son comparables entre sí. La
constante K amortigua: evita que el primer lugar de una lista domine toda la fusión.

**Resultado medido** con la consulta "cuántos reintentos permite el motivo M02 cliente ausente":

| # | Recuperado por | RRF | Rank denso | Rank BM25 | Cita |
|---|---|---|---|---|---|
| 1 | ambos | 0,0328 | 1 | 1 | CAT-OPS-007 — M02 — Cliente ausente |
| 2 | ambos | 0,0320 | 2 | 3 | CAT-OPS-007 — Tabla resumen de responsabilidad |
| 3 | ambos | 0,0320 | 3 | 2 | SOP-OPS-014 — 4. Regla de intentos de entrega |
| 5 | solo denso | 0,0156 | 4 | — | CAT-OPS-007 — M05 — Rechazo del consumidor |

Lectura del resultado: el sistema recuperó **la definición del motivo, la tabla de
responsabilidad y la regla de reintentos**, que son exactamente los tres fragmentos necesarios
para responder. Y se observa el efecto de la fusión: un fragmento que solo encontró el
recuperador denso obtiene la mitad del puntaje que los encontrados por ambos.

**Alternativa descartada:** usar `QueryFusionRetriever` de LlamaIndex. Lo descartamos porque
(a) en su configuración por defecto genera consultas adicionales con el LLM, lo que agrega
latencia y costo, y (b) al implementar la fusión nosotros podemos mostrar en la interfaz el
aporte de cada recuperador, que es justamente la evidencia que pide la evaluación.

### 5.5 Segmentación (chunking) en dos etapas

**Qué hicimos:** primero `MarkdownNodeParser` (corta respetando los encabezados), después
`SentenceSplitter` con 600 tokens y 120 de solape.

**Por qué en dos etapas:**

1. **Cortar por estructura primero** hace que cada fragmento coincida con una sección real del
   documento. Eso permite citar "SOP-OPS-014 — sección 4. Regla de intentos de entrega" en vez
   de "SOP-OPS-014, en alguna parte". La precisión de la cita es un criterio evaluado.
2. **Cortar por tamaño después** garantiza que ninguna sección larga desborde el contexto y que
   quepan varios fragmentos de distintos documentos en el prompt.
3. **El solape de 120 tokens** evita perder información que quede justo en el borde de un
   corte: una regla partida en dos fragmentos aparecería incompleta en ambos.

**Detalle de implementación que tuvimos que corregir:** la sección se resuelve **antes** del
corte por tamaño. Al principio lo hicimos después y todos los fragmentos quedaron etiquetados
como "Documento completo", porque los fragmentos de continuación ya no empezaban con un
encabezado. Al mover el cálculo antes del segundo corte, los fragmentos hijos **heredan** la
sección de su sección padre y la cita queda correcta.

### 5.6 Los datos estructurados NO pasan por RAG

**Qué hicimos:** `envios.csv` y `eventos_tracking.csv` se consultan con pandas de forma
determinista. No se indexan ni se embeben.

**Por qué (esta es probablemente la pregunta más probable de la defensa):**

| Razón | Explicación |
|---|---|
| **Precisión** | Buscar el envío `LR-2026-004182` por similitud semántica puede devolver `LR-2026-004190`, que es un envío distinto de otro cliente. Una consulta exacta por clave nunca se equivoca. |
| **Aritmética** | Los LLM son poco confiables calculando diferencias de fechas y comparando umbrales. "¿Han pasado más de 72 horas desde la fecha promesa?" se resuelve con una resta en código. |
| **Auditoría** | El cálculo en código es reproducible y testeable; una inferencia del LLM no. |
| **Evidencia empírica propia** | Nuestro modelo de 3B ya inventó una compensación prohibida por el procedimiento. Ese es exactamente el error que esta separación previene. |

**La regla general que hay que saber enunciar:** *RAG para conocimiento no estructurado
(procedimientos, políticas, normativa); consultas deterministas para datos estructurados
(registros, fechas, estados). Usar RAG sobre una tabla es un antipatrón.*

### 5.7 Fuentes internas y externas, y por qué ambas

La evaluación exige considerar fuentes internas y externas. En nuestro caso no es un requisito
decorativo, cada una cumple una función distinta:

| Fuente | Tipo | Qué aporta a la respuesta |
|---|---|---|
| SOP-OPS-014 (procedimiento de excepciones) | Interna | Qué acción operativa corresponde y cuántos reintentos quedan |
| SLA-COM-002 (matriz de SLA) | Interna | Si el caso incumple el contrato del retailer y en qué plazo hay que responder |
| POL-COM-003 (compensaciones) | Interna | Qué compensación está autorizada y quién debe aprobarla |
| CAT-OPS-007 (catálogo de motivos) | Interna | A quién se atribuye la causa y si computa para el SLA |
| EXT-SERNAC-001 (evidencia pública) | Externa | Magnitud y contexto del problema; riesgo de reclamo formal |
| EXT-NORM-002 (normativa) | Externa | Que el plazo exigible es el informado al consumidor, y el límite de lo que el agente puede afirmar |

**Caso donde la fuente externa cambia la respuesta:** el envío `LR-2026-008455` es de temporada
alta con `plazo_extendido_informado = NO`. La matriz interna permite extender el plazo en
temporada alta, **pero** solo si el retailer informó al consumidor. Como no lo informó, la
norma externa obliga a mantener la fecha promesa original. Sin la fuente externa, el sistema
habría concluido erróneamente que no hubo incumplimiento. Este ejemplo es oro para la defensa.

### 5.8 Detalles menores pero que conviene poder explicar

| Decisión | Motivo |
|---|---|
| Índice vectorial simple persistido en disco, sin Chroma ni FAISS | Con 43 fragmentos la búsqueda exhaustiva es instantánea. Un motor con indexación aproximada agregaría una dependencia sin beneficio medible. Se documenta como limitación de escala. |
| `data/vectorstore/` está en `.gitignore` | Es un artefacto **derivado y reconstruible** con un comando. Versionar binarios generados es mala práctica. |
| Fecha de operación fija (`FECHA_OPERACION=2026-09-23`) | El retraso de un envío no entregado depende de "hoy". Si dependiera de la fecha real del sistema, las evidencias dejarían de ser reproducibles mañana. |
| Los archivos de datos simulados se escribieron sin tildes | Evita problemas de codificación de caracteres en la consola de Windows al mostrar evidencias. La documentación sí usa tildes porque se lee en el editor. |
| Temperatura del LLM en 0.1 | Queremos respuestas consistentes y apegadas a la fuente, no creatividad. |
| Datos de envíos totalmente simulados | Restricción del caso: no usar datos personales reales. |

---

## 6. Recorrido completo de una consulta (el flujo que hay que saber contar)

Consulta del operador: *"El cliente del envío LR-2026-004182 reclama que no ha llegado. ¿Qué
le respondo y qué corresponde hacer?"*

**Paso 1 — Detección de entidad.** El agente identifica con una expresión regular el código
`LR-2026-004182`. Si no hubiera código, el flujo seguiría solo como consulta de políticas.

**Paso 2 — Consulta determinista (herramienta).** Se busca la fila exacta en `envios.csv` y su
historial en `eventos_tracking.csv`:

```
retailer: TiendaNova      servicio: ND (1 día hábil)     hub: Quilicura
fecha promesa: 2026-09-16    fecha entrega real: (vacía)   estado: EN_RUTA
intentos: 0    motivo: M01    temporada: ALTA    plazo extendido informado: NO
último evento: 2026-09-17 REPROGRAMADO, sin intento de entrega registrado
```

**Paso 3 — Cálculo de hechos en código.** No lo hace el LLM:

- Retraso = fecha de operación (2026-09-23) − fecha promesa (2026-09-16) = **7 días**.
- Tramo = superior a 72 horas.
- Motivo M01 → responsabilidad de LogiRuta → **computa para SLA**.
- Servicio ND → **no admite extensión de plazo** en temporada alta.

**Paso 4 — Recuperación RAG.** Con esos hechos se construyen las consultas de recuperación
(no se usa la pregunta cruda del usuario, se usa una consulta enriquecida con el motivo, el
servicio, el tier del retailer y el tramo de retraso). El recuperador híbrido devuelve
fragmentos como:

- `CAT-OPS-007 — M01 — Congestión vial o sobrecarga de ruta`
- `SOP-OPS-014 — 6. Matriz de decisión de acción operativa`
- `SOP-OPS-014 — 7. Escalamiento`
- `POL-COM-003 — 2. Tabla de compensaciones al consumidor final`
- `SLA-COM-002 — 3. Matriz contractual por retailer`

**Paso 5 — Ensamblado del prompt.** Rol + hechos verificados + fragmentos etiquetados
`[F1]...[F5]` + instrucción de formato + restricciones (no inventar, citar siempre, no afirmar
nada que no esté en los fragmentos).

**Paso 6 — Generación.** El LLM redacta diagnóstico, acción y mensaje al cliente, citando.

**Paso 7 — Respuesta trazable.** La interfaz muestra la respuesta y, al lado, los fragmentos
con sus puntajes y quién los recuperó.

**La coherencia datos → procesamiento → respuesta** que pide la pauta se demuestra así:
el dato `motivo = M01` viene del CSV, el fragmento recuperado dice que M01 computa para SLA
y que un retraso mayor a 72 horas exige escalamiento a Jefe de Operaciones, y la respuesta
final escala y compensa. Cada eslabón es visible.

---

## 7. Estructura del repositorio y qué hace cada archivo

```
SolucionesIA-EV1/
├── requirements.txt              Dependencias exactas del proyecto
├── .env.example                  Plantilla de configuración (sin secretos)
│
├── data/
│   ├── internos/                 FUENTES INTERNAS (simuladas)
│   │   ├── sop_excepciones_reintentos.md   SOP-OPS-014 → procedimiento, reintentos, escalamiento
│   │   ├── matriz_sla_retailers.md         SLA-COM-002 → plazos, OTD, penalizaciones, exclusiones
│   │   ├── politica_compensaciones.md      POL-COM-003 → qué compensación y quién la aprueba
│   │   ├── catalogo_motivos_falla.md       CAT-OPS-007 → motivos M01-M07 y responsabilidad
│   │   ├── envios.csv                      40 envíos (NO va a RAG)
│   │   └── eventos_tracking.csv            43 eventos de tracking (NO va a RAG)
│   ├── externos/                 FUENTES EXTERNAS
│   │   ├── sernac_reclamos_retraso_entrega.md   EXT-SERNAC-001 → evidencia pública
│   │   └── normativa_consumidor_ecommerce.md    EXT-NORM-002 → Ley 19.496 y 21.398
│   └── vectorstore/              Índice generado (no se versiona, se reconstruye)
│
├── src/
│   ├── config.py                 Rutas, parámetros y FÁBRICAS de LLM y embeddings
│   ├── ingest.py                 Carga, segmenta, embebe y persiste el índice
│   ├── retrieval.py              Recuperación híbrida + fusión RRF + formato de citas
│   ├── tracking.py               Consulta determinista del CSV y cálculo de hechos
│   ├── prompts.py                (pendiente) Carga y ensamblado de prompts
│   ├── agent.py                  (pendiente) Orquestación completa
│   ├── app.py                    (pendiente) Interfaz Streamlit
│   └── evaluar.py                (pendiente) Ejecuta los escenarios y guarda evidencias
│
├── prompts/                      (pendiente) Prompts + justificación de su diseño
├── arquitectura/                 (pendiente) Diagrama de arquitectura
├── evidencias/                   (pendiente) Capturas y salidas de las pruebas
├── informe/                      (pendiente) Informe ≤ 5 páginas
├── presentacion/                 (pendiente) Diapositivas y guion
└── docs/
    ├── propuesta_caso.md         Caso, problema, objetivos, restricciones, referencias
    ├── PASO_A_PASO.md            Cronograma y división de tareas
    ├── GUIA_ESTUDIO.md           Este documento
    └── documentacion_tecnica.md  (pendiente) Documentación de funcionamiento
```

### Funciones clave que conviene reconocer en el código

| Archivo | Función | Qué hace |
|---|---|---|
| `config.py` | `construir_llm()` | Devuelve Groq, Gemini u Ollama según `.env`. Es la capa de abstracción. |
| `config.py` | `construir_embeddings()` | Devuelve el modelo de embeddings local. |
| `ingest.py` | `cargar_documentos()` | Lee los `.md`, extrae los metadatos de la cabecera y marca interna/externa. |
| `ingest.py` | `segmentar()` | Corte en dos etapas y asignación de la sección para citar. |
| `ingest.py` | `construir_indice()` | Genera embeddings y persiste el índice en disco. |
| `retrieval.py` | `RecuperadorHibrido.recuperar()` | Lanza las dos búsquedas y devuelve los fragmentos fusionados. |
| `retrieval.py` | `_fusionar()` | Implementa la fórmula RRF. |
| `retrieval.py` | `formatear_contexto()` | Arma el bloque `[F1]...[Fn]` que se inyecta en el prompt. |
| `tracking.py` | `detectar_codigo()` | Extrae `LR-2026-...` del texto del operador. |
| `tracking.py` | `consultar_envio()` | Busca el CSV por clave exacta y calcula retraso, tramo y responsabilidad. |
| `tracking.py` | `formatear_hechos()` | Bloque de hechos listo para el prompt. |

### Tecnologías instaladas y para qué sirve cada una

| Tecnología | Versión / modelo | Rol en el proyecto |
|---|---|---|
| Python | 3.13.4 | Lenguaje base |
| LlamaIndex Core | 0.14.25 | Framework de ingesta, indexación y recuperación |
| `llama-index-llms-groq` | 0.6.1 | Conector al LLM principal (Groq) |
| `llama-index-llms-google-genai` | 0.11.2 | Conector Gemini (respaldo) |
| `llama-index-llms-ollama` | 0.11.0 | Conector LLM local (respaldo) |
| `llama-index-embeddings-ollama` | 0.10.0 | Conector de embeddings locales |
| `llama-index-retrievers-bm25` | 0.8.0 | Recuperador léxico BM25 |
| `bm25s` | 0.3.11 | Implementación eficiente de BM25 |
| `PyStemmer` | 2.2.0.3 | Stemmer en **español** para BM25 |
| Ollama | 0.32.1 | Servidor local (embeddings + LLM de respaldo) |
| `nomic-embed-text` | — | Embeddings, 768 dimensiones |
| Groq `openai/gpt-oss-120b` | — | LLM principal (~1–2 s por consulta) |
| Streamlit | 1.64.0 | Interfaz web de la demostración (pendiente de cablear) |
| pandas | 3.0.6 | Consulta determinista de los CSV |
| `python-dotenv` | 1.2.3 | Carga de configuración desde `.env` |

Nota sobre PyStemmer: configurar el stemmer en **español** importa. Sin él, BM25 trataría
"reintento", "reintentos" y "reintentar" como palabras distintas y perdería coincidencias.

---

## 8. Estado de avance

### Terminado y verificado

| Ítem | Evidencia de que funciona |
|---|---|
| Decisiones de stack fundamentadas | Sección 5, con mediciones propias |
| 6 documentos de fuentes (4 internas + 2 externas) | `data/internos/`, `data/externos/` |
| 2 datasets estructurados (40 envíos, eventos de tracking) | `envios.csv`, `eventos_tracking.csv` |
| Capa de abstracción de LLM y embeddings | `src/config.py` (groq / gemini / ollama) |
| Pipeline de ingesta e indexación | 43 fragmentos generados en 15 s |
| Recuperación híbrida con RRF | Probada con consulta por código y con paráfrasis |
| Citas precisas a documento y sección | Corregido y verificado |
| Herramienta de tracking determinista | `src/tracking.py` — retraso, tramo y responsabilidad en código |
| LLM Groq operativo | ~1–2 s por consulta con `openai/gpt-oss-120b` |
| README con pasos de instalación | Raíz del repo, sección “Cómo ejecutar” |

### Pendiente

1. `prompts/` — los prompts y su justificación escrita.
2. `src/agent.py` — orquestación completa.
3. `src/app.py` — interfaz Streamlit.
4. `src/evaluar.py` — ejecución de los 5 escenarios y captura de evidencias.
5. Diagrama de arquitectura como imagen.
6. Documentación técnica e informe ≤ 5 páginas.
7. Presentación / guion de defensa.

---

## 9. Preguntas probables en la defensa y cómo responderlas

**¿Por qué RAG y no entrenar un modelo propio?**
Porque el conocimiento del caso son políticas que cambian de versión (el SOP está en v3.2, la
matriz de SLA en v2.4). Con RAG, actualizar el sistema es reemplazar un documento y reindexar;
con ajuste fino habría que reentrenar. Además no tenemos volumen de datos ni GPU para entrenar,
y el ajuste fino no resuelve el problema de la trazabilidad de la cita.

**¿Por qué búsqueda híbrida y no solo embeddings?**
Porque el corpus está lleno de identificadores exactos (M02, SOP-OPS-014, códigos de envío) y
la búsqueda densa los diluye. Mostrar la tabla de resultados de la sección 5.4.

**¿Por qué la tabla de envíos no está en el RAG?**
Porque buscar un código de envío por similitud semántica puede devolver un envío distinto, y
porque el LLM no es confiable calculando diferencias de fechas. Mencionar la evidencia propia:
el modelo local inventó una compensación que el procedimiento prohíbe.

**¿Cómo evitan las alucinaciones?**
Tres mecanismos combinados: (1) el LLM solo puede usar los fragmentos recuperados, (2) los
hechos numéricos y la responsabilidad se calculan en código antes de llamar al LLM, y (3) toda
afirmación debe citar su fragmento, lo que permite verificarla.

**¿Qué pasa si el RAG no recupera nada relevante?**
El prompt instruye a declarar que no hay respaldo documental y a escalar, en vez de responder
por inferencia propia. Es preferible un "no lo sé, escale" que una política inventada.

**¿Por qué Groq y no un modelo local, si tenían Ollama instalado?**
Mostrar las mediciones: 212 segundos por consulta en Ollama 3B y un error de razonamiento
verificado (inventó una compensación). Groq responde en ~1–2 s. Ollama y Gemini siguen
disponibles como respaldo por configuración, porque la arquitectura desacopla el proveedor.
Gemini se descartó como principal por un 403 a nivel de cuenta, no por preferencia estética.

**¿Cuáles son las limitaciones de su solución?**
Índice de búsqueda exhaustiva (no escala a cientos de miles de fragmentos sin cambiar a un
motor vectorial con indexación aproximada); los datos son simulados; no hay evaluación
automática de la calidad de recuperación con métricas formales; depende de una API externa
para la generación; y el sistema no emite calificaciones jurídicas, solo alerta riesgos.

**¿Qué rol cumple cada fuente externa?**
La de SERNAC dimensiona el problema y el riesgo reputacional; la normativa fija que el plazo
exigible es el informado al consumidor. Usar el caso `LR-2026-008455` como ejemplo de que la
fuente externa **cambia** el resultado del diagnóstico.

---

## 10. Bitácora de lo realizado

| # | Actividad | Resultado |
|---|---|---|
| 1 | Clonado del repositorio y revisión de la documentación existente | Caso definido, sin código aún |
| 2 | Inventario del entorno | Python 3.13.4, Ollama con Llama 3.1 8B, sin dependencias |
| 3 | Decisión de stack con el equipo | LlamaIndex + Streamlit + embeddings Ollama |
| 4 | Descarga de `nomic-embed-text` y creación del entorno virtual | Entorno aislado en `.venv` |
| 5 | Instalación de dependencias | LlamaIndex 0.14.25 y BM25 operativos |
| 6 | Medición de rendimiento del LLM local | 284 s (8B) y 212 s (3B) → inviable |
| 7 | Verificación del hardware | i5-7400, 8 GB RAM, GPU no utilizable |
| 8 | Primer intento con Gemini | 403 PERMISSION_DENIED en dos proyectos |
| 9 | Migración a Groq como motor principal | `openai/gpt-oss-120b` en ~1–2 s |
| 10 | Creación de las 6 fuentes documentales | 4 internas y 2 externas, con metadatos de citación |
| 11 | Creación de los datasets estructurados | 40 envíos + eventos de tracking |
| 12 | Implementación de `config.py`, `ingest.py` y `retrieval.py` | Índice de 43 fragmentos y recuperación híbrida |
| 13 | Corrección de la asignación de secciones | Citas precisas a documento y sección |
| 14 | Implementación de `tracking.py` | Hechos (retraso, tramo, responsabilidad) en código |
| 15 | README + esta guía actualizados para que Eder pueda probar | Pasos reproducibles sin compartir claves |

---

## 11. Cómo instalar y probar (para Eder / Camilo)

> Resumen operativo. La versión canónica con comandos también está en el `README.md` de la raíz.

### Regla de secretos

- El repo es **público**.
- Cada integrante crea **su propia** clave en [console.groq.com/keys](https://console.groq.com/keys).
- Se copia `.env.example` → `.env` y se completa `GROQ_API_KEY`.
- **Nunca** se hace `git add .env`.

### Checklist rápido

1. `git pull`
2. Crear / activar `.venv` e instalar `requirements.txt`
3. Crear `.env` desde `.env.example` con tu clave Groq
4. `ollama serve` + `ollama pull nomic-embed-text`
5. `python -m src.ingest --reconstruir`
6. Probar:
   - `python -m src.retrieval "cuantos reintentos permite el motivo M02"`
   - `python -m src.tracking LR-2026-004182`
   - `python -c "from src.config import construir_llm; print(construir_llm().complete('Di solo: OK'))"`

### Qué esperar si todo está bien

| Comando | Resultado esperado |
|---|---|
| `ingest` | Mensaje con **43 fragmentos** |
| `retrieval` M02 | Primer resultado: `CAT-OPS-007 — M02 — Cliente ausente` |
| `tracking` 004182 | 7 días de retraso, tramo `mas_de_5_dias`, responsable LogiRuta |
| prueba Groq | Respuesta en ~1–2 segundos |

### Problemas frecuentes

| Síntoma | Qué revisar |
|---|---|
| `Falta GROQ_API_KEY` | Existe `.env` y la clave no está vacía |
| Error de conexión a Ollama | `ollama serve` está corriendo; URL en `.env` = `http://localhost:11434` |
| `model_not_found` en Groq | Usar `GROQ_MODELO=openai/gpt-oss-120b` (el catálogo gratuito cambió) |
| CSV no abre / ParserError | Actualizar el repo (`git pull`): los CSV ya fueron corregidos con comillas |
| Índice vacío o desactualizado | Volver a correr `python -m src.ingest --reconstruir` |
