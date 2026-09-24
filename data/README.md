# Datos del proyecto (simulados)

## Estructura

### Internos (indexados en RAG)
- `sop_excepciones_reintentos.md` — SOP-OPS-014
- `matriz_sla_retailers.md` — SLA-COM-002
- `politica_compensaciones.md` — POL-COM-003
- `catalogo_motivos_falla.md` — CAT-OPS-007

### Internos estructurados (consulta determinista, NO van al RAG)
- `envios.csv` — 40 envios simulados
- `eventos_tracking.csv` — historial de tracking

### Externos (indexados en RAG)
- `../externos/sernac_reclamos_retraso_entrega.md` — EXT-SERNAC-001
- `../externos/normativa_consumidor_ecommerce.md` — EXT-NORM-002

No incluir datos personales reales.

## Nota para el equipo

Los CSV se consultan con `src/tracking.py`. El indice vectorial se genera en
`data/vectorstore/` (carpeta ignorada por git) ejecutando:

```bash
python -m src.ingest --reconstruir
```
