# solucionesIA — Primera Evaluación Parcial ISY0101

**Asignatura:** Ingeniería de Soluciones con IA (ISY0101)  
**Integrantes:** Camilo Romero · Eder Valdivia  
**Entrega AVA (informe + repo):** 25 de septiembre de 2026  
**Presentación / defensa:** 26 de septiembre de 2026  

## Caso (simulado, basado en problema real)

**Organización:** LogiRuta SpA (operador logístico de última milla, Región Metropolitana)  
**Problema:** Retrasos y falta de trazabilidad en despachos e-commerce en peaks de demanda (Cyber / Navidad), alineado con el problema más reportado ante SERNAC: retardo en la entrega.

> Detalle del caso, objetivos, datos y justificación IA/LLM/RAG: ver [`docs/propuesta_caso.md`](docs/propuesta_caso.md)  
> Guía completa del trabajo y cronograma: ver [`docs/PASO_A_PASO.md`](docs/PASO_A_PASO.md)

## Estado del proyecto

| Componente | Estado |
|---|---|
| Propuesta de caso | Definida (datos simulados) |
| Stack técnico (LLM, RAG, UI) | Pendiente de decisión |
| Implementación agente + RAG | Pendiente |
| Informe (máx. 5 páginas) | Pendiente |
| Presentación | Pendiente (lista el 25; se expone el 26) |

## Estructura del repositorio

```text
solucionesIA/
├── README.md                 # Este archivo
├── docs/                     # Documentación y paso a paso
├── src/                      # Código fuente de la solución
├── data/                     # Fuentes internas/externas (simuladas)
├── prompts/                  # Prompts del agente y justificación
├── arquitectura/             # Diagramas de arquitectura
├── evidencias/               # Capturas y resultados de pruebas
├── presentacion/             # PPT/Canva y guion de defensa
└── informe/                  # Informe técnico (Word/PDF)
```

## Cómo ejecutar

> Pendiente: se completará cuando se fije el stack (Python/LangChain, API, etc.).

Pasos previstos:

1. Clonar el repositorio  
2. Crear entorno virtual e instalar dependencias  
3. Configurar variables en `.env` (plantilla: `.env.example`)  
4. Indexar documentos RAG  
5. Levantar la interfaz / agente  

## Integrantes y roles (resumen)

| Persona | Enfoque principal |
|---|---|
| **Camilo Romero** | Caso, arquitectura, informe, parte de prompts |
| **Eder Valdivia** | Pipeline RAG, implementación, evidencias, presentación |

Ver división día a día en [`docs/PASO_A_PASO.md`](docs/PASO_A_PASO.md).

## Uso de IA (declaración)

Se permite usar IA como apoyo (redacción, diagramas, búsqueda de referencias), citando herramientas y validando el contenido.  
**No** se usará IA para conclusiones, justificaciones técnicas finales ni reflexiones personales (requisito de la evaluación).

## Licencia / visibilidad

Repositorio **público** para la evaluación parcial.
