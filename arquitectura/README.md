# Arquitectura de la solución

Hay **dos versiones**, porque cumplen funciones distintas:

| Archivo | Uso |
|---|---|
| `diagrama_arquitectura.mmd` · `.png` · `.svg` | **Versión resumida.** Tres etapas y la frontera determinista/generativo. Es la que va en el informe y en las diapositivas: entra en una página y se lee de lejos |
| `diagrama_detallado.mmd` · `.svg` | **Versión detallada.** Rotula cada función real del código. Sirve como anexo y para responder preguntas en la defensa. Es muy alta, por eso se entrega en SVG (vectorial, se amplía sin pérdida) |

La versión resumida no simplifica el diseño, solo agrupa: las tres etapas que muestra
corresponden exactamente a los módulos del detallado.

Regenerar tras editar un `.mmd`:

```bash
npx @mermaid-js/mermaid-cli -i diagrama_arquitectura.mmd -o diagrama_arquitectura.png --size 2000 --scale 2 --backgroundColor white
```

También se puede pegar el contenido del `.mmd` en <https://mermaid.live>.

---

## El diagrama corresponde al código real

La evaluación exige que la arquitectura represente la solución desarrollada y no sea un esquema
decorativo. Por eso cada caja rotula **el archivo y la función que la implementan**, y no una
etiqueta genérica. Cualquier componente del diagrama puede abrirse en el código.

| Componente del diagrama | Función real | Archivo | Por qué existe |
|---|---|---|---|
| Interfaz | Aplicación Streamlit | `src/app.py` | La transparencia es una restricción del caso: el analista debe poder ver en qué se basó el sistema. También produce las capturas de evidencia |
| Detección de entidad | `detectar_codigo()` | `src/tracking.py` | Decide si el flujo es diagnóstico de envío o consulta de políticas |
| Herramienta determinista | `consultar_envio()`, `_clasificar_tramo()` | `src/tracking.py` | Los días de retraso, el tramo y la responsabilidad se calculan en código. El modelo no puede alucinarlos |
| Consultas dirigidas | `construir_consultas_dirigidas()` | `src/agent.py` | La pregunta del analista no contiene los términos que identifican los fragmentos aplicables; los hechos sí |
| Búsqueda densa | `VectorStoreIndex.as_retriever()` | `src/retrieval.py` | Recupera paráfrasis: «me devuelven la plata» frente a «reembolso del costo de despacho» |
| Búsqueda léxica | `BM25Retriever` con stemmer español | `src/retrieval.py` | Recupera identificadores exactos (`M02`, `SOP-OPS-014`) que la búsqueda densa diluye |
| Fusión RRF | `_fusionar()`, `K_RRF = 60` | `src/retrieval.py` | Combina por posición y no por puntaje, porque las escalas de BM25 y coseno no son comparables |
| Selección por aspecto | `_recuperar_por_aspectos()` | `src/agent.py` | Garantiza que cada aspecto del caso quede representado en el contexto |
| Índice | `segmentar()`, `construir_indice()` | `src/ingest.py` | Segmentación en dos etapas: por encabezados y luego por tamaño, para poder citar documento **y** sección |
| Prompts | `prompt_sistema()`, `prompt_diagnostico()` | `src/prompts.py` + `prompts/*.md` | Los textos viven fuera del código para poder revisarse y justificarse sin leer Python |
| Capa de LLM | `construir_llm()` | `src/config.py` | Abstrae el proveedor: cambiar de motor es una variable de entorno, no un rediseño |

---

## Lo que el diagrama quiere mostrar

**El orden de las capas.** Primero los datos duros, después la recuperación, el modelo al
final. Las cajas deterministas y las generativas están coloreadas de forma distinta
precisamente para que esa frontera se vea: todo lo verde ocurre en código y es reproducible;
lo morado es lo único que varía entre ejecuciones.

**Los dos caminos de salida.** Existe una flecha punteada que va desde la herramienta de
tracking directamente a la respuesta, sin pasar por el modelo: es el caso del envío inexistente.
Sin hechos verificados no hay diagnóstico posible, y el sistema lo dice en lugar de inventarlo.

**Las fuentes externas como componente, no como anexo.** El aspecto `normativa` se recupera
restringido a fuentes externas, para que la norma llegue al contexto aunque las fuentes
internas obtengan mejor puntaje. El caso `LR-2026-008455` demuestra que esa decisión cambia el
diagnóstico.

**Que los CSV no entran al índice.** Aparecen conectados solo a la herramienta determinista.
Es la decisión de diseño más importante del proyecto y el diagrama la hace visible.
