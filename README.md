# solucionesIA — Primera Evaluación Parcial ISY0101

**Asignatura:** Ingeniería de Soluciones con IA (ISY0101)  
**Integrantes:** Camilo Romero · Eder Valdivia  
**Entrega AVA (informe + repo):** 25 de septiembre de 2026  
**Presentación / defensa:** 26 de septiembre de 2026  

## Caso (simulado, basado en problema real)

**Organización:** LogiRuta SpA (operador logístico de última milla, Región Metropolitana)  
**Problema:** Retrasos y falta de trazabilidad en despachos e-commerce en peaks de demanda, alineado con el problema más reportado ante SERNAC: retardo en la entrega.

> Caso completo: [`docs/propuesta_caso.md`](docs/propuesta_caso.md)  
> Cronograma: [`docs/PASO_A_PASO.md`](docs/PASO_A_PASO.md)  
> Guía de estudio (para defender el proyecto): [`docs/GUIA_ESTUDIO.md`](docs/GUIA_ESTUDIO.md)

## Stack técnico (decidido)

| Capa | Tecnología |
|---|---|
| LLM (generación) | **Groq** — `openai/gpt-oss-120b` (principal). Gemini y Ollama como respaldo. |
| Embeddings | **Ollama** local — `nomic-embed-text` |
| Framework RAG | **LlamaIndex** |
| Recuperación | Híbrida: embeddings + BM25, fusión RRF |
| Datos estructurados | pandas sobre CSV (sin RAG) |
| UI (pendiente) | Streamlit |

## Estado del proyecto

| Componente | Estado |
|---|---|
| Propuesta de caso | Lista |
| Fuentes internas / externas | Listas (6 documentos + 2 CSV) |
| Pipeline RAG (ingest + retrieval) | Funcional |
| Herramienta de tracking | Funcional |
| Prompts + agente + UI | Pendiente |
| Informe (máx. 5 páginas) | Pendiente |
| Presentación | Pendiente |

## Cómo ejecutar (guía para Eder / cualquier integrante)

### 0. Requisitos

- Python 3.11+ (probado con 3.13)
- [Ollama](https://ollama.com/) instalado (solo para embeddings)
- Cuenta gratuita en [Groq](https://console.groq.com) (**cada integrante usa su propia clave**)

> **Importante:** el archivo `.env` **no se sube al repo** (contiene secretos).
> Cada uno crea el suyo a partir de `.env.example`.

### 1. Clonar / actualizar

```bash
git clone https://github.com/milotkg2/solucionesIA.git
cd solucionesIA
# o, si ya lo tenías:
git pull
```

### 2. Crear entorno virtual e instalar dependencias

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configurar tu clave (propia, no la de Camilo)

1. Entra a [console.groq.com/keys](https://console.groq.com/keys)
2. Crea una API Key (gratis, sin tarjeta)
3. Copia la plantilla y completa:

```powershell
copy .env.example .env
```

Edita `.env` y deja al menos:

```env
LLM_PROVEEDOR=groq
GROQ_API_KEY=pega_aqui_tu_clave
GROQ_MODELO=openai/gpt-oss-120b
EMBEDDINGS_PROVEEDOR=ollama
EMBEDDINGS_MODELO=nomic-embed-text
FECHA_OPERACION=2026-09-23
```

### 4. Levantar Ollama y bajar el modelo de embeddings

```powershell
ollama serve
```

En otra terminal:

```powershell
ollama pull nomic-embed-text
```

### 5. Construir el índice RAG (una sola vez)

Desde la raíz del repo, con el venv activo:

```powershell
python -m src.ingest --reconstruir
```

Deberías ver algo como: `Indice construido con 43 fragmentos...`

### 6. Probar lo que ya funciona

**A) Recuperación RAG (sin LLM):**

```powershell
python -m src.retrieval "cuantos reintentos permite el motivo M02 cliente ausente"
python -m src.retrieval "me devuelven la plata del despacho si llega muy tarde"
```

**B) Tracking determinista (sin LLM):**

```powershell
python -m src.tracking LR-2026-004182
python -m src.tracking "El cliente del envio LR-2026-005271 reclama"
```

**C) LLM Groq (solo generación):**

```powershell
python -c "from src.config import construir_llm; print(construir_llm().complete('Di solo: OK'))"
```

### 7. Códigos de envío útiles para probar

| Código | Escenario |
|---|---|
| `LR-2026-004182` | Retraso por congestión (M01), responsabilidad LogiRuta |
| `LR-2026-005271` | Cliente ausente (M02), sin compensación |
| `LR-2026-006123` | Dirección incompleta (M03) |
| `LR-2026-007334` | Quiebre de capacidad hub (M04), ElectroMax Tier 1 |
| `LR-2026-008455` | Retraso 1 día + temporada alta sin plazo extendido informado |
| `LR-2026-009011` | Paquete no localizable (M07) |

## Estructura del repositorio

```text
solucionesIA/
├── README.md
├── requirements.txt
├── .env.example              # plantilla (sin secretos)
├── docs/
│   ├── propuesta_caso.md
│   ├── PASO_A_PASO.md
│   └── GUIA_ESTUDIO.md       # estudiar y defender el proyecto
├── src/
│   ├── config.py             # fábricas LLM / embeddings
│   ├── ingest.py             # indexación RAG
│   ├── retrieval.py          # recuperación híbrida + RRF
│   └── tracking.py           # consulta CSV + hechos calculados
├── data/internos/            # SOP, SLA, políticas, CSV
├── data/externos/            # SERNAC + normativa
├── prompts/                  # (pendiente)
├── arquitectura/             # (pendiente)
├── evidencias/               # (pendiente)
├── presentacion/             # (pendiente)
└── informe/                  # (pendiente)
```

## Integrantes y roles

| Persona | Enfoque principal |
|---|---|
| **Camilo Romero** | Caso, arquitectura, informe, parte de prompts |
| **Eder Valdivia** | Pipeline RAG, implementación, evidencias, presentación |

## Uso de IA (declaración)

Se permite usar IA como apoyo (redacción, diagramas, búsqueda de referencias), citando herramientas y validando el contenido.  
**No** se usará IA para conclusiones, justificaciones técnicas finales ni reflexiones personales.

## Licencia / visibilidad

Repositorio **público** para la evaluación parcial. Por eso las claves API **nunca** se versionan.
