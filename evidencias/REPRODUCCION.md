# Acta de reproducción cruzada de los escenarios

**Fecha:** 25 de septiembre de 2026
**Objetivo:** comprobar que los resultados de `evidencias/escenarios/` no dependen de la
máquina que los generó.

Las evidencias de `escenarios/` fueron producidas el 24/09 en el equipo de Camilo Romero. Este
documento registra su reejecución completa en el equipo de Eder Valdivia, en un entorno
instalado desde cero, para verificar que el pipeline es reproducible.

---

## 1. Entornos comparados

| | Equipo de origen | Equipo de verificación |
|---|---|---|
| Fecha de ejecución | 2026-09-24 23:58 | 2026-09-25 00:29 |
| Python | 3.13.4 | 3.13.15 |
| Entorno virtual | Preexistente | Creado desde cero para esta prueba |
| LLM | Groq `openai/gpt-oss-120b` | Groq `openai/gpt-oss-120b` |
| Embeddings | `nomic-embed-text` (Ollama local) | `nomic-embed-text` (Ollama local) |
| Fecha de operación | `2026-09-23` | `2026-09-23` |

Las versiones de las dependencias resueltas coinciden: `llama-index-core 0.14.25`,
`llama-index-retrievers-bm25 0.8.0`, `PyStemmer 2.2.0.3`, `bm25s 0.3.11`, `pandas 3.0.6`.

---

## 2. Resultados

### 2.1 Indexación

`python -m src.ingest --reconstruir` produjo **43 fragmentos**, la misma cifra registrada en
`docs/GUIA_ESTUDIO.md`. Tiempo de indexación: 31 s.

### 2.2 Recuperación

La consulta de control «cuantos reintentos permite el motivo M02 cliente ausente» devolvió los
mismos fragmentos, en el mismo orden y con los mismos puntajes:

| # | Recuperado por | RRF | Rank denso | Rank BM25 | Cita |
|---|---|---|---|---|---|
| 1 | ambos | 0.0328 | 1 | 1 | CAT-OPS-007 — M02 — Cliente ausente |
| 2 | ambos | 0.0320 | 2 | 3 | CAT-OPS-007 — Tabla resumen de responsabilidad |
| 3 | ambos | 0.0320 | 3 | 2 | SOP-OPS-014 — 4. Regla de intentos de entrega |
| 5 | solo denso | 0.0156 | 4 | — | CAT-OPS-007 — M05 — Rechazo del consumidor |

### 2.3 Escenarios completos

`python -m src.evaluar` sobre los 7 escenarios: **34/34 verificaciones cumplidas (100%)**,
igual que en la corrida original. Latencia media extremo a extremo: 14,0 s (14,1 s en origen).

### 2.4 Comparación de los archivos generados

Al comparar la salida de ambas corridas con `git diff`, **las tablas de fragmentos recuperados
no presentan ninguna diferencia** en los cinco escenarios de diagnóstico:

```
ESC-01: 0 líneas de tabla de fragmentos cambiadas
ESC-02: 0 líneas de tabla de fragmentos cambiadas
ESC-03: 0 líneas de tabla de fragmentos cambiadas
ESC-04: 0 líneas de tabla de fragmentos cambiadas
ESC-05: 0 líneas de tabla de fragmentos cambiadas
```

Las únicas diferencias corresponden a la prosa redactada por el modelo, las marcas de tiempo y
las latencias medidas.

---

## 3. Interpretación

El resultado separa con precisión las dos capas del sistema:

- **La capa determinista es reproducible.** La consulta al CSV, el cálculo de días de retraso
  y de tramo, la construcción de las consultas dirigidas y la recuperación híbrida con fusión
  RRF producen exactamente la misma salida en máquinas distintas, con entornos instalados
  por separado. Esto es consecuencia directa de dos decisiones de diseño: excluir los datos
  estructurados del índice vectorial y fijar la fecha de operación.
- **La variabilidad está confinada a la generación.** Solo cambia el texto que redacta el LLM,
  y aun con temperatura 0,1 esa variación persiste, como es esperable en un modelo de lenguaje.

En términos del caso: los hechos sobre los que la Mesa de Control toma decisiones —quién es
responsable, cuántos días de retraso hay, qué compensación corresponde— son estables y
auditables. Lo que varía es la redacción, que es precisamente la tarea delegada al modelo.

---

## 4. Defecto reproducido

La reejecución confirmó también una de las limitaciones registradas en
`escenarios/REVISION_HUMANA.md`. En una consulta de diagnóstico sobre `LR-2026-004182`, el
fragmento `[F7]` correspondiente a la fuente externa `EXT-NORM-002` fue recuperado y entregado
al modelo, pero no aparece en la lista de fuentes citadas de la respuesta. El modelo prefirió
la regla interna equivalente. En la misma respuesta se observó una afirmación sobre riesgo de
reclamo ante SERNAC sin cita de respaldo.

Que el defecto se reproduzca en otra máquina indica que **no es aleatorio sino sistemático**, y
confirma la limitación ya declarada: que un fragmento sea recuperado no implica que el modelo
lo utilice ni lo cite. La verificación de la correspondencia entre afirmación y cita sigue
requiriendo revisión humana.

---

## 5. Reproducir esta verificación

```powershell
python -m src.ingest --reconstruir     # espera: 43 fragmentos
python -m src.retrieval "cuantos reintentos permite el motivo M02 cliente ausente"
python -m src.evaluar                  # espera: 34/34 verificaciones
git diff --stat evidencias/
```
