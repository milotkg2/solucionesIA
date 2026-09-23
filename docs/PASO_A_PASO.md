# Paso a paso — Evaluación Parcial 1 (ISY0101)

**Integrantes:** Camilo Romero · Eder Valdivia (`EderDev138`)  
**Entrega AVA:** **25 de septiembre de 2026** (informe + enlace al repositorio)  
**Presentación:** material listo el **25**; exposición el **26** (10 min exposición + 10 min preguntas)  
**Repositorio:** `solucionesIA` (público)  

---

## Resumen de entregables

| Entregable | Peso | Criterio clave |
|---|---|---|
| Informe técnico (máx. **5 páginas**, Word/PDF, APA) | 60% del encargo (junto al repo) | Redacción técnica, evidencias, diagramas |
| Repositorio GitHub | Obligatorio | Código, README, bocetos, evidencias, docs |
| Presentación | 40% | Coherencia datos→respuesta, arquitectura, decisiones, evidencias |

### Checklist mínimo del repo

- [ ] Código fuente
- [ ] README con cómo ejecutar
- [ ] Documentación de funcionamiento
- [ ] Bocetos / diagramas
- [ ] Evidencias de pruebas
- [ ] Prompts justificados
- [ ] Pipeline RAG implementado y explicado

---

## Caso elegido (resumen)

**LogiRuta SpA** (simulada): operador de última milla.  
**Problema real de fondo:** retrasos de entrega en e-commerce (principal motivo de reclamos SERNAC en peaks).  
**Solución:** agente con LLM + RAG que diagnostica retrasos y propone acciones usando fuentes internas (SOP, tracking simulado, SLAs) y externas (normativa / contexto SERNAC).

Detalle: [`propuesta_caso.md`](propuesta_caso.md)

**Pendiente:** stack técnico y API keys (definir 23–24/09).

---

## Cronograma día a día

### Miércoles 23/09 — Cierre de caso + repo + plan

| Tarea | Responsable | Done |
|---|---|---|
| Validar caso LogiRuta (o ajustar nombre/enfoque) | Ambos | [ ] |
| Crear repo público `solucionesIA` + colaborador Eder | Camilo | [ ] |
| Completar estructura inicial y este documento | Camilo | [ ] |
| Definir stack (LLM, framework RAG, UI, vector store) | Ambos | [ ] |
| Crear datasets simulados mínimos (tracking + SOP + SLA) | Eder (lead) / Camilo apoya | [ ] |
| Boceto 1 de arquitectura (caja negra: Usuario→Agente→RAG→LLM) | Camilo | [ ] |

**Salida del día:** caso cerrado, repo usable por ambos, stack decidido, datos base empezados.

---

### Jueves 24/09 — Desarrollo (prompts + RAG + agente)

| Tarea | Responsable | Done |
|---|---|---|
| Diseñar prompts (sistema + diagnóstico + respuesta cliente) y justificar estructura | Camilo | [ ] |
| Implementar chunking, embeddings e índice RAG | Eder | [ ] |
| Integrar agente (orquestación consulta → retrieve → generate) | Ambos | [ ] |
| Fuentes externas: incorporar 2–3 docs/contexto SERNAC o resumen normativo | Camilo | [ ] |
| Probar ≥ 5 escenarios (retraso, cliente ausente, SLA, peak Cyber, dirección incompleta) | Eder | [ ] |
| Guardar evidencias (capturas / logs) en `/evidencias` | Eder | [ ] |
| Actualizar diagrama de arquitectura a la solución real | Camilo | [ ] |

**Salida del día:** demo funcional end-to-end + evidencias iniciales.

---

### Viernes 25/09 — Documentación + informe + presentación (ENTREGA AVA)

| Tarea | Responsable | Done |
|---|---|---|
| Completar README (instalación, `.env`, scripts, cómo validar) | Eder | [ ] |
| Redactar informe ≤ 5 páginas (problema, solución, RAG, arquitectura, resultados, límites) | Camilo (lead) | [ ] |
| Tablas/diagramas y citas APA en el informe | Camilo | [ ] |
| Declaración de uso de IA + **reflexiones personales sin IA** (ambos) | Ambos | [ ] |
| Armar presentación (PPT/Canva): arquitectura, flujo datos→respuesta, decisiones, demo | Eder (lead) / Camilo | [ ] |
| Guion 10 min: quién habla qué (participación equitativa) | Ambos | [ ] |
| Ensayo rápido (cronómetro) | Ambos | [ ] |
| Subir informe + link del repo a **AVA** | Camilo (o quien tenga acceso) | [ ] |
| Push final al repo (código limpio, sin secretos) | Ambos | [ ] |

**Salida del día:** entrega AVA hecha + presentación lista.

---

### Sábado 26/09 — Exposición y defensa

| Tarea | Responsable | Done |
|---|---|---|
| Revisar guion y demo (5–10 min antes) | Ambos | [ ] |
| Exposición 10 min (ambos hablan) | Ambos | [ ] |
| Preguntas 10 min: arquitectura, RAG, prompts, limitaciones | Ambos | [ ] |

#### Guion sugerido (10 minutos)

| Min | Tema | Quién |
|---|---|---|
| 0–2 | Organización, problema real (SERNAC) y objetivos | Camilo |
| 2–4 | Arquitectura (diagrama) y rol del agente | Camilo |
| 4–7 | RAG + prompts + demo (datos → retrieve → respuesta) | Eder |
| 7–9 | Decisiones de diseño y evidencias | Eder |
| 9–10 | Limitaciones, aprendizajes y cierre | Ambos |

---

## Etapas alineadas a la pauta del curso

### Etapa 1 — Selección del caso
Organización + problema concreto y relevante → **LogiRuta / retrasos última milla**.

### Etapa 2 — Propuesta
Completar en `propuesta_caso.md`: objetivos medibles, datos, restricciones, justificación IA/LLM/RAG, referencias.

### Etapa 3 — Desarrollo
1. Análisis del caso (requerimientos ↔ solución).  
2. Diseño de prompts (estructura + justificación).  
3. Pipeline RAG (fuentes internas y externas, flujo de información).  
4. Arquitectura real (no decorativa).  
5. Implementación y pruebas con evidencias.

### Etapa 4 — Documentación
Informe ≤ 5 páginas, README, código, bocetos, evidencias, APA, declaración de IA, reflexiones personales.

### Etapa 5 — Presentación
Apoyo visual + demo + lenguaje técnico + participación equitativa.

### Etapa 6 — Defensa
Explicar coherencia datos recuperados → procesamiento → respuesta.

---

## Criterios de evaluación (orientación del trabajo)

| Aspecto | % | Cómo lo cubriremos |
|---|---|---|
| Diseño del proyecto de agente | 15% | Objetivos + flujo del agente |
| Formulación de prompts | 10% | Carpeta `/prompts` + justificación |
| Flujos RAG | 10% | Código + explicación en informe |
| Arquitectura | 15% | Diagrama en `/arquitectura` alineado al código |
| Informe técnico | 10% | `/informe` ≤ 5 páginas |
| Coherencia datos–respuestas | 10% | Escenarios + evidencias |
| Diagrama de arquitectura | 10% | Presentación + docs |
| Fundamentación de decisiones | 10% | Informe + defensa |
| Lenguaje técnico, evidencias y ejemplos | 10% | Demo + capturas |

---

## División de responsabilidades (visión general)

### Camilo Romero
- Propuesta de caso y justificación organizacional  
- Arquitectura y decisiones de diseño (documentadas)  
- Diseño/justificación de prompts (co-autoría)  
- Informe técnico (lead)  
- Citas APA y declaración de uso de IA  

### Eder Valdivia
- Datos simulados e indexación RAG  
- Implementación del pipeline y scripts de ejecución  
- Evidencias de pruebas  
- README técnico “cómo correr”  
- Lead de presentación / diapositivas  

Ambos validan el resultado final y participan en la defensa.

---

## Orden de trabajo recomendado (si se atrasa algo)

1. Datos + RAG mínimo funcionando  
2. 1 prompt bueno + 3 escenarios con evidencia  
3. Diagrama de arquitectura fiel al código  
4. Informe corto y claro (mejor 4 páginas sólidas que 5 vacías)  
5. Presentación con demo  

---

## Notas sobre uso ético de IA

Permitido: mejorar redacción, buscar referencias, crear diagramas, apoyar tareas.  
Obligatorio: declarar herramientas, citar, revisar y validar.  
Prohibido para la evaluación: usar IA en **conclusiones**, **justificaciones técnicas finales** y **reflexiones personales**.

---

## Próxima decisión inmediata

Antes de codear el 24/09, el equipo debe responder:

1. ¿Confirmamos **LogiRuta SpA** como nombre del caso?  
2. ¿Stack? (ej. Python + LangChain + Chroma + Streamlit + OpenAI/Gemini/local)  
3. ¿Quién aporta la API key o usamos modelo gratuito/local?
