# Codigo fuente

| Modulo | Estado | Que hace |
|---|---|---|
| `config.py` | Listo | Fabricas de LLM (groq/gemini/ollama) y embeddings |
| `ingest.py` | Listo | Indexacion RAG de fuentes internas y externas |
| `retrieval.py` | Listo | Recuperacion hibrida + fusion RRF |
| `tracking.py` | Listo | Consulta determinista del CSV y calculo de hechos |
| `prompts.py` | Listo | Carga y ensamblado de los prompts |
| `agent.py` | Listo | Orquestacion: tracking, consultas dirigidas, RAG y LLM |
| `app.py` | Listo | Interfaz Streamlit con panel de evidencia |
| `evaluar.py` | Listo | Ejecuta los 7 escenarios y escribe las evidencias |

Como instalar y probar: ver el `README.md` de la raiz del repositorio.
