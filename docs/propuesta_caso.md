# Propuesta de caso — Logística (simulado, problema real)

**Curso:** ISY0101 — Ingeniería de Soluciones con IA  
**Equipo:** Camilo Romero · Eder Valdivia  
**Fecha de entrega:** 25 de septiembre de 2026  

---

## 1. Organización (simulada)

| Campo | Detalle |
|---|---|
| **Nombre** | LogiRuta SpA |
| **Rubro** | Operador logístico de **última milla** para e-commerce y retail |
| **Tamaño** | PyME mediana: ~180 colaboradores, 3 hubs en Región Metropolitana, ~45 vehículos propios + red de freelancers |
| **Contexto** | Atiende despachos B2C para tiendas online. En peaks (CyberDay, Black Friday, Navidad) el volumen se multiplica y satura la operación, generando retrasos, reclamos y costos de reintento de entrega. |

> **Nota académica:** la empresa es ficticia, pero el **problema** está anclado en evidencia pública chilena (SERNAC / análisis de e-commerce y última milla).

---

## 2. Problema o desafío (basado en evidencia real)

### Problema a resolver
El **centro de atención / mesa de control** de LogiRuta no logra diagnosticar a tiempo las causas de retraso ni responder de forma consistente a clientes y retailers, porque la información está dispersa (tracking, políticas internas, SLAs, normativa).

### Por qué es importante (evidencia externa)
- En Navidad 2024, el **retraso en la entrega** concentró cerca del **78%** de los reclamos navideños ante SERNAC (1.354 de 1.731 en el período comparable). Fuente: [SERNAC](https://www.sernac.cl/portal/604/w3-article-83820.html).
- En CyberDay, el retardo en la entrega (junto a cancelaciones unilaterales) fue el principal motivo de reclamos. Fuente: [SERNAC](https://www.sernac.cl/portal/604/w3-article-82103.html).
- Análisis de Duoc UC señala que los fallos **no son solo de última milla**: inventarios, preparación, promesas irreales de plazo y mala coordinación también disparan el retraso. Fuente: [Logística 360 Chile](https://logistica360chile.cl/duoc-uc-descarta-que-fallas-en-el-e-commerce-sean-solo-de-la-ultima-milla/).

### Impacto actual en la organización (simulado)
- Aumento de tickets de soporte y tiempos de respuesta.
- Penalizaciones / pérdida de contratos con retailers por incumplimiento de SLA.
- Reintentos de entrega y costos operativos.
- Baja satisfacción del consumidor final y riesgo reputacional.

---

## 3. Objetivos de la solución (concretos y medibles)

| ID | Objetivo | Métrica propuesta (demo) |
|---|---|---|
| O1 | Diagnosticar causa probable de un retraso a partir de tracking + políticas | ≥ 80% de casos de prueba con causa coherente y citada |
| O2 | Responder al cliente/retailer con mensaje accionable y trazable | 100% de respuestas con referencia a fuente interna/externa (RAG) |
| O3 | Sugerir siguiente acción operativa (reintento, compensación, escalamiento) | Checklist de acciones alineado a SOP interno en ≥ 4/5 escenarios |
| O4 | Reducir tiempo de análisis del agente humano | Demo: de “buscar en 4 sistemas” a **1 consulta** al agente |

---

## 4. Datos disponibles (simulados + externos)

### Internos (a simular en `/data`)
- Histórico de envíos / tracking (estados, hubs, fechas comprometidas vs reales).
- Manual de procedimientos (SOP) de excepciones y reintentos.
- Política de compensaciones y SLAs con retailers.
- Catálogo de motivos de falla (dirección incompleta, cliente ausente, congestión, quiebre de capacidad, etc.).

### Externos
- Criterios SERNAC / Reglamento de Comercio Electrónico (plazos, información de despacho).
- Notas/artículos sobre retrasos en peaks e-commerce (contexto del problema).

### Uso en la solución
Los documentos se indexan en un **pipeline RAG**. El agente recupera fragmentos relevantes y el LLM genera diagnóstico + respuesta + acción, citando fuentes.

---

## 5. Restricciones o requerimientos

- Datos personales: usar solo datasets **simulados** (sin RUT/teléfonos reales).
- Tiempo de desarrollo: entrega 25/09/2026.
- Stack técnico: **pendiente** (definir el 23–24/09).
- Transparencia: toda respuesta debe poder mostrar **fuentes recuperadas**.
- Cumplir requisitos del curso: agentes + LLM + RAG + prompts + arquitectura + evidencias.

---

## 6. Justificación de IA, LLM y RAG

| Tecnología | Por qué aplica |
|---|---|
| **Agente de IA** | Orquesta pasos: interpretar consulta → recuperar contexto → diagnosticar → proponer acción → redactar respuesta. |
| **LLM** | Interpreta lenguaje natural de operadores/clientes y genera respuestas consistentes a partir de políticas. |
| **RAG** | Evita alucinaciones sobre SLAs/SOP/normativa; ancla respuestas en documentos internos y fuentes externas actualizables. |

Sin RAG, el LLM inventaría plazos o políticas. Sin agente, solo habría un chat genérico sin flujo operativo.

---

## 7. Referencias (APA — borrador)

Servicio Nacional del Consumidor. (2024). *El 26 de diciembre se consolida como el día con más reclamos navideños*. https://www.sernac.cl/portal/604/w3-article-83820.html  

Servicio Nacional del Consumidor. (2024). *Retardo en la entrega y cancelaciones unilaterales, los principales problemas de los últimos Cyber*. https://www.sernac.cl/portal/604/w3-article-82103.html  

Logística 360 Chile. (n.d.). *Duoc UC descarta que fallas en el e-commerce sean solo de la última milla*. https://logistica360chile.cl/duoc-uc-descarta-que-fallas-en-el-e-commerce-sean-solo-de-la-ultima-milla/  

Cooperativa Ciencia. (2024). *¿Cómo funciona la «última milla» en Chile?* https://www.cooperativaciencia.cl/radiociencia/2024/05/15/como-funciona-la-ultima-milla-en-chile/  

---

## Decisión pendiente del equipo

Confirmar nombre comercial simulado (**LogiRuta SpA** u otro) y el stack (Python + LangChain / LlamaIndex, vector store, UI Streamlit/Gradio, proveedor LLM).
