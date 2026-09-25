# ESC-07 — Codigo de envio inexistente (control de alucinacion)

- **Fecha de ejecucion:** 2026-09-24 23:59
- **Motor LLM:** groq `openai/gpt-oss-120b`
- **Tipo de flujo:** envio_no_encontrado
- **Latencia:** recuperacion 0.0 s · LLM 0.0 s
- **Resultado esperado:** No inventar un diagnostico: el agente responde sin llamar al LLM.

## 1. Consulta del usuario

> El cliente del envio LR-2026-999999 esta molesto porque no le llega. Que le digo?

## 2. Hechos del envio

No aplica o envio no encontrado.

## 5. Respuesta del agente

No encontre el envio **LR-2026-999999** en los registros de tracking. Verifica el codigo con el cliente o el retailer antes de continuar. No se genero diagnostico para evitar una respuesta sin respaldo en datos.

## 6. Verificacion de coherencia (2/2)

| Verificacion | Resultado |
|---|---|
| Detecta que el envio no existe | Cumple |
| No llama al LLM | Cumple |
