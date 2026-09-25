# Documentación técnica

**Proyecto:** Mesa de Control asistida por IA — LogiRuta SpA
**Asignatura:** ISY0101 — Ingeniería de Soluciones con IA
**Última actualización:** 25 de septiembre de 2026

Este documento describe **qué** se construyó, **cómo funciona**, **qué decisiones se tomaron**,
**qué resultados se obtuvieron** y **qué limitaciones** presenta la solución.

Documentos complementarios, para no duplicar contenido:

| Documento | Qué aporta |
|---|---|
| [`README.md`](../README.md) | Instalación y ejecución paso a paso |
| [`propuesta_caso.md`](propuesta_caso.md) | Organización, problema, objetivos y restricciones |
| [`GUIA_ESTUDIO.md`](GUIA_ESTUDIO.md) | Fundamento extendido de cada decisión, glosario y preparación de la defensa |
| [`prompts/README.md`](../prompts/README.md) | Diseño de los prompts y su justificación |
| [`evidencias/escenarios/RESUMEN.md`](../evidencias/escenarios/RESUMEN.md) | Resultados de los 7 escenarios |
| [`evidencias/REPRODUCCION.md`](../evidencias/REPRODUCCION.md) | Verificación cruzada entre dos equipos |

---

## 1. Qué se desarrolló

Un agente que recibe una consulta en lenguaje natural sobre un envío atrasado y devuelve un
diagnóstico de la causa, la acción operativa que corresponde según el procedimiento, un
borrador de mensaje para el cliente y las alertas contractuales o normativas del caso, citando
en cada afirmación el documento y la sección que la respaldan.

La caracterización que distingue la solución: **no es un chatbot, es un asistente de decisión
trazable.** Cada respuesta puede auditarse hasta la fuente que la sostiene, y cada número puede
reproducirse ejecutando el módulo de tracking de forma independiente.

### Componentes

| Módulo | Responsabilidad |
|---|---|
| `src/config.py` | Rutas, parámetros y fábricas intercambiables de LLM y embeddings |
| `src/ingest.py` | Carga de fuentes, segmentación en dos etapas, embeddings y persistencia |
| `src/retrieval.py` | Recuperación híbrida densa + BM25 con fusión RRF |
| `src/tracking.py` | Consulta determinista de los CSV y cálculo de hechos en código |
| `src/prompts.py` | Carga y ensamblado de las plantillas de `prompts/` |
| `src/agent.py` | Orquestación de la secuencia completa |
| `src/app.py` | Interfaz Streamlit con panel de evidencia |
| `src/evaluar.py` | Ejecución de los escenarios y generación de evidencias |

---

## 2. Cómo funciona

> Diagrama: [`arquitectura/diagrama_arquitectura.png`](../arquitectura/diagrama_arquitectura.png)

El flujo de una consulta con código de envío, tal como lo implementa `responder()` en
`src/agent.py`:

**1 · Detección de entidad.** `detectar_codigo()` busca el patrón `LR-AAAA-NNNNNN` en el texto.
Si no hay código, el flujo continúa como consulta de políticas: solo recuperación documental.

**2 · Consulta determinista.** `consultar_envio()` busca la fila por clave exacta en
`envios.csv`, recupera el historial de `eventos_tracking.csv` y calcula **en código** los días
de retraso, el tramo según POL-COM-003 y la responsabilidad según CAT-OPS-007. Si el envío no
existe, el agente responde sin invocar al modelo: no hay hechos que diagnosticar y cualquier
respuesta generada sería inventada.

**3 · Consultas de recuperación dirigidas.** `construir_consultas_dirigidas()` traduce los
hechos en una consulta por aspecto del caso: motivo, intentos, acción, compensación, SLA,
escalamiento, temporada, normativa y siniestro. No se busca con la pregunta cruda del analista.
El aspecto `normativa` se restringe a fuentes externas, para garantizar que la norma llegue al
contexto aunque las fuentes internas obtengan mejor puntaje.

**4 · Recuperación híbrida.** Cada consulta pasa por los dos recuperadores y se fusiona con
RRF. `_recuperar_por_aspectos()` toma primero el mejor fragmento de cada aspecto, para que
todos queden representados, y completa el cupo de 8 con los restantes, sin duplicados.

**5 · Ensamblado del prompt.** Prompt de sistema + hechos verificados + fragmentos etiquetados
`[F1]…[Fn]` + instrucciones de formato.

**6 · Generación.** `_llamar_llm()` invoca al proveedor configurado, con reintento ante límites
de cuota y normalización de las citas que algunos modelos emiten con corchetes anchos.

**7 · Respuesta trazable.** Se devuelve la respuesta junto con los hechos, las consultas
generadas, los fragmentos con sus puntajes y el prompt, que es lo que la interfaz muestra.

### El orden es la decisión de diseño

Primero los datos duros, después la recuperación, el modelo al final. El LLM nunca decide
cuántos días de retraso hay ni si corresponde compensación: recibe esos hechos ya calculados y
su función es **redactar y fundamentar, no calcular**.

---

## 3. Decisiones tomadas y su fundamento

Resumen. El desarrollo completo de cada una está en [`GUIA_ESTUDIO.md`](GUIA_ESTUDIO.md) §5.

| Decisión | Fundamento |
|---|---|
| Los CSV **no** se indexan | Buscar un código por similitud puede devolver otro envío; los LLM son poco confiables restando fechas. Evidencia propia: el modelo local de 3B inventó una compensación prohibida por CAT-OPS-007 |
| Recuperación híbrida densa + BM25 | El corpus está lleno de identificadores exactos que la búsqueda densa diluye; las consultas de los operadores son paráfrasis que BM25 no alcanza |
| Fusión RRF implementada por el equipo | Los puntajes de BM25 y de coseno no son comparables: se fusiona por posición. Implementarla permite mostrar el aporte de cada recuperador |
| Segmentación en dos etapas | Cortar primero por encabezados permite citar documento **y sección**, que es lo que hace auditable la respuesta |
| Embeddings locales, LLM en la nube | La indexación ocurre una vez; la generación en cada consulta. Además, la matriz SLA es confidencial y no sale del equipo |
| Groq como motor principal | 1–5 s frente a 212–285 s medidos con inferencia local en CPU. Gemini quedó descartado por `403 PERMISSION_DENIED` a nivel de cuenta |
| Tres proveedores en el código | Demuestra que la arquitectura no está acoplada: cambiar de motor es una variable de entorno |
| Orquestación determinista | El flujo de la Mesa de Control es estable; fijar la secuencia da latencia predecible, reproducibilidad y auditabilidad |
| Índice exhaustivo sin motor vectorial | Con 43 fragmentos la búsqueda exhaustiva es instantánea y exacta. Se declara como limitación de escala |
| Fecha de operación fija | El retraso de un envío no entregado depende de «hoy»; fijarla hace reproducibles las evidencias |
| Temperatura 0,1 | Se busca consistencia y apego a la fuente, no creatividad |

---

## 4. Resultados obtenidos

### 4.1 Escenarios de prueba

Siete escenarios ejecutables (`src/evaluar.py`) que cubren cinco motivos de falla, una consulta
sin envío y un control de alucinación: **34/34 verificaciones cumplidas (100%)**, latencia media
de 14,1 s extremo a extremo.

### 4.2 Cumplimiento de los objetivos

| Objetivo | Meta | Resultado |
|---|---|---|
| O1 — Causa coherente y citada | ≥ 80% | 5/5 casos de diagnóstico (100%) |
| O2 — Respuesta con referencia a fuente | 100% | 6/6 con citas `[F#]` |
| O3 — Acción alineada al SOP | ≥ 4/5 | 5/5 en la acción principal |
| O4 — De 4 sistemas a 1 consulta | 1 consulta | 1 consulta, 14 s promedio |

Sobre O4 corresponde una precisión metodológica: la reducción se reporta como **número de
consultas**, verificable por inspección del flujo, y no como porcentaje de ahorro de tiempo. No
se midió la línea base del procedimiento manual porque la organización es simulada.

### 4.3 Coherencia dato → recuperación → respuesta

El caso `LR-2026-008455` demuestra la cadena completa. El dato `plazo_extendido_informado = NO`
proviene del CSV; la matriz interna permite extender plazos en temporada alta; la fuente
externa condiciona esa extensión a que se informe al consumidor; la respuesta concluye que rige
la fecha promesa original. **Sin la fuente externa el diagnóstico habría sido el contrario.**

### 4.4 Reproducibilidad verificada

Los escenarios se reejecutaron en un segundo equipo con entorno instalado desde cero: 34/34
verificaciones y **tablas de fragmentos recuperados sin ninguna diferencia** respecto de la
corrida original. Solo varía la prosa del modelo.

Esto confirma empíricamente la separación de responsabilidades del diseño: la capa determinista
es reproducible entre máquinas y la variabilidad está confinada a la generación. Detalle en
[`evidencias/REPRODUCCION.md`](../evidencias/REPRODUCCION.md).

---

## 5. Limitaciones

1. **Citas que no respaldan exactamente la afirmación.** El modelo puede añadir una inferencia
   plausible y asignarle una cita cercana. Detectado en revisión humana (ESC-02) y
   **reproducido en el segundo equipo**, lo que lo confirma como sistemático.
2. **Fragmento recuperado no implica fragmento usado.** En ESC-05 la normativa externa llegó al
   contexto y el modelo prefirió la regla interna sin citarla.
3. **Sin evaluación cuantitativa de la recuperación.** No se construyó un conjunto anotado que
   permita medir precisión y exhaustividad con métricas formales. Es la limitación
   metodológica más relevante.
4. **El índice no escala.** Búsqueda exhaustiva adecuada para 43 fragmentos, inadecuada para
   cientos de miles.
5. **Dependencia de un servicio externo** para la generación. Mitigada por la capa de
   abstracción, pero la alternativa local tiene latencia de minutos.
6. **Datos simulados.** El sistema no fue expuesto a la ambigüedad ni a los registros
   incompletos de una operación real.
7. **Sin calificaciones jurídicas.** Limitación deliberada, derivada del límite de uso
   declarado en EXT-NORM-002 §4.

---

## 6. Requisitos de entorno

**Python 3.11 a 3.13.** El proyecto **no instala en Python 3.14**:
`llama-index-retrievers-bm25` exige `pystemmer<3.0.0` en todas sus versiones, y PyStemmer 2.x
no publica binario para 3.14, por lo que `pip` intenta compilarlo y falla pidiendo Microsoft
C++ Build Tools. Se detectó al replicar el entorno el 25/09.

Requiere además Ollama en ejecución con `nomic-embed-text` para los embeddings, y una clave de
Groq por integrante en un archivo `.env` local, que no se versiona.

---

## 7. Evidencias que respaldan lo anterior

| Evidencia | Qué demuestra |
|---|---|
| `evidencias/escenarios/ESC-01..07.md` | Consulta, hechos, consultas generadas, fragmentos con puntajes y respuesta, por escenario |
| `evidencias/escenarios/RESUMEN.md` | Verificaciones automáticas y latencias |
| `evidencias/escenarios/REVISION_HUMANA.md` | Revisión manual con los defectos encontrados |
| `evidencias/REPRODUCCION.md` | Verificación cruzada entre dos equipos |
| `evidencias/01_...`, `02_...` | Iteración de los prompts de v1 a v2 |
| `data/vectorstore/resumen_indice.md` | Composición del índice (generado en la ingesta) |

---

## 8. Trabajo futuro

1. **Evaluación cuantitativa de la recuperación** con un conjunto anotado, que permitiría
   además justificar empíricamente los valores de `top_k` y de la constante de amortiguación.
2. **Verificación automática de la atribución:** comprobar que cada cita emitida corresponda a
   un fragmento recuperado, convirtiendo en garantía verificada lo que hoy es una instrucción
   del prompt.
3. **Registro de trazas de ejecución** para auditoría retrospectiva.
4. **Integración con los sistemas de origen**, sustituyendo los CSV por conectores reales sin
   alterar la separación entre consulta determinista y recuperación documental.
