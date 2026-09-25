# Resumen de escenarios de prueba

- **Fecha:** 2026-09-24 23:59
- **Motor:** groq `openai/gpt-oss-120b`
- **Verificaciones cumplidas:** 34/34 (100%)
- **Respuestas generadas con citas [F#]:** 6/6
- **Latencia media extremo a extremo (escenarios con LLM):** 14.1 s

| Escenario | Titulo | Verificaciones | Latencia total (s) | Evidencia |
|---|---|---|---|---|
| ESC-01 | Retraso por congestion en temporada alta (M01) | 6/6 | 11.4 | [ESC-01.md](ESC-01.md) |
| ESC-02 | Cliente ausente con dos intentos fallidos (M02) | 5/5 | 8.8 | [ESC-02.md](ESC-02.md) |
| ESC-03 | Direccion incompleta (M03) | 6/6 | 7.8 | [ESC-03.md](ESC-03.md) |
| ESC-04 | Quiebre de capacidad del hub, retailer Tier 1 same day (M04) | 6/6 | 22.3 | [ESC-04.md](ESC-04.md) |
| ESC-05 | Temporada alta sin plazo extendido informado (fuente externa decisiva) | 6/6 | 21.6 | [ESC-05.md](ESC-05.md) |
| ESC-06 | Consulta general de politicas (sin envio) | 3/3 | 12.4 | [ESC-06.md](ESC-06.md) |
| ESC-07 | Codigo de envio inexistente (control de alucinacion) | 2/2 | 0.0 | [ESC-07.md](ESC-07.md) |

Las verificaciones son automaticas (patrones de texto y fragmentos recuperados) y se
complementan con revision humana de cada respuesta.
