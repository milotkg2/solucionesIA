"""Interfaz de demostracion de la Mesa de Control (Streamlit).

La pantalla no solo muestra la respuesta del agente: expone al lado la evidencia que la
sostiene. Esa decision responde a una restriccion del caso (toda respuesta debe poder mostrar
sus fuentes) y a un criterio de la evaluacion: la coherencia entre el dato recuperado y la
respuesta generada tiene que ser visible, no declarada.

Por eso se muestran, para cada consulta:
- los hechos que calculo la herramienta de tracking en codigo, antes de llamar al LLM;
- las consultas de recuperacion que el agente derivo de esos hechos, una por aspecto;
- los fragmentos recuperados con su score RRF, su posicion en cada recuperador y cual de los
  dos los encontro;
- el prompt exacto que se envio al modelo.

Ejecutar desde la raiz del repositorio:  streamlit run src/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Permite ejecutar con `streamlit run src/app.py` desde la raiz: streamlit no agrega la raiz
# del proyecto al path, por lo que `import src.agent` fallaria sin esto.
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

from src.agent import ResultadoAgente, responder  # noqa: E402
from src.config import CONFIG_MODELOS, DIR_INDICE, FECHA_OPERACION, ConfiguracionInvalida  # noqa: E402

st.set_page_config(page_title="Mesa de Control LogiRuta", page_icon="📦", layout="wide")

EJEMPLOS: dict[str, str] = {
    "M01 · Retraso por congestion, temporada alta": (
        "El cliente del envio LR-2026-004182 reclama que no ha llegado. "
        "Que le respondo y que corresponde hacer?"
    ),
    "M02 · Cliente ausente, dos intentos fallidos": (
        "El cliente del envio LR-2026-005271 reclama y pide compensacion. Corresponde?"
    ),
    "M03 · Direccion incompleta": (
        "Que hacemos con el envio LR-2026-006123? El cliente dice que su direccion esta bien."
    ),
    "M04 · Quiebre de hub, retailer Tier 1": (
        "ElectroMax escala el envio LR-2026-007334 y exige respuesta. Que le decimos?"
    ),
    "Temporada alta · la fuente externa decide": (
        "DecoCasa dice que el envio LR-2026-008455 llego un dia tarde pero que en temporada "
        "alta el plazo se extiende. Tienen razon?"
    ),
    "M07 · Paquete no localizable": (
        "El envio LR-2026-009011 no aparece. Que corresponde hacer y que le digo al cliente?"
    ),
    "Sin envio · consulta de politicas": (
        "Cuantos reintentos permite el procedimiento cuando el cliente esta ausente?"
    ),
    "Control · codigo inexistente": (
        "Revisa el envio LR-2026-999999, el cliente dice que no llega."
    ),
}

ETIQUETAS_TIPO = {
    "diagnostico": ("Diagnostico", "El agente detecto un codigo de envio y uso la herramienta de tracking."),
    "politicas": ("Politicas", "Sin codigo de envio: el flujo se resolvio solo con recuperacion documental."),
    "envio_no_encontrado": ("No encontrado", "No se llamo al LLM: no hay hechos verificados que diagnosticar."),
    "error": ("Error", "Fallo la generacion con el modelo de lenguaje."),
}


def indice_existe() -> bool:
    return (DIR_INDICE / "docstore.json").exists()


def tabla_hechos(resultado: ResultadoAgente) -> pd.DataFrame:
    """Hechos calculados en codigo, en el orden en que importan para el diagnostico."""
    hechos = resultado.hechos
    campos = [
        ("Codigo de seguimiento", hechos.codigo_seguimiento),
        ("Retailer", hechos.retailer),
        ("Servicio", f"{hechos.servicio} — {hechos.servicio_descripcion}"),
        ("Hub origen / destino", f"{hechos.hub_origen} → {hechos.comuna_destino}"),
        ("Fecha promesa", hechos.fecha_promesa),
        ("Fecha entrega real", hechos.fecha_entrega_real or "pendiente"),
        ("Estado", hechos.estado),
        ("Intentos de entrega", hechos.intentos_entrega),
        ("Motivo de falla", f"{hechos.motivo_falla or 'sin motivo'} — {hechos.motivo_nombre or 'n/a'}"),
        ("Responsable (CAT-OPS-007)", hechos.responsable or "n/a"),
        ("Computa para SLA", hechos.computa_sla),
        ("Compensacion posible", hechos.compensacion_posible),
        ("Temporada", hechos.temporada),
        ("Plazo extendido informado", hechos.plazo_extendido_informado),
        ("Dias de retraso", hechos.dias_retraso),
        ("Tramo (POL-COM-003)", hechos.tramo_retraso),
        ("Fecha de referencia", hechos.fecha_referencia),
    ]
    return pd.DataFrame(
        [{"Campo": nombre, "Valor": "" if valor is None else str(valor)} for nombre, valor in campos]
    )


def tabla_fragmentos(resultado: ResultadoAgente) -> pd.DataFrame:
    filas = []
    for numero, fragmento in enumerate(resultado.fragmentos, start=1):
        filas.append(
            {
                "Etiqueta": f"F{numero}",
                "Aspecto": fragmento.aspecto or "-",
                "Documento — seccion": fragmento.referencia,
                "Fuente": fragmento.tipo_fuente,
                "Recuperado por": fragmento.recuperado_por,
                "Rank denso": fragmento.rank_vectorial,
                "Rank BM25": fragmento.rank_lexico,
                "RRF": round(fragmento.score_rrf, 4),
            }
        )
    return pd.DataFrame(filas)


# --- Barra lateral -----------------------------------------------------------

with st.sidebar:
    st.header("Configuracion activa")
    st.caption("Los valores provienen de `.env` y se muestran para que la demo sea auditable.")
    st.markdown(
        f"""
        - **Proveedor LLM:** `{CONFIG_MODELOS.proveedor_llm}`
        - **Modelo:** `{CONFIG_MODELOS.modelo_groq if CONFIG_MODELOS.proveedor_llm == 'groq' else CONFIG_MODELOS.modelo_ollama}`
        - **Embeddings:** `{CONFIG_MODELOS.modelo_embeddings_ollama}` (local)
        - **Temperatura:** `{CONFIG_MODELOS.temperatura}`
        - **Fecha de operacion:** `{FECHA_OPERACION}`
        """
    )

    if indice_existe():
        st.success("Indice RAG disponible")
    else:
        st.warning(
            "No existe el indice RAG. Se construira en la primera consulta "
            "(tarda ~30 s) o puedes generarlo con `python -m src.ingest --reconstruir`."
        )

    if CONFIG_MODELOS.proveedor_llm == "groq" and not CONFIG_MODELOS.clave_groq:
        st.error("Falta `GROQ_API_KEY` en `.env`. La recuperacion funciona, la generacion no.")

    st.divider()
    st.caption(
        "Los datos de envios son simulados. El retraso de un envio no entregado se calcula "
        "contra la fecha de operacion fija, para que las evidencias sean reproducibles."
    )


# --- Cuerpo principal --------------------------------------------------------

st.title("Mesa de Control LogiRuta · asistente de diagnostico de retrasos")
st.caption(
    "Agente con RAG hibrido sobre fuentes internas y externas. Los hechos numericos se "
    "calculan en codigo; el modelo de lenguaje redacta y fundamenta, no calcula."
)

if "consulta" not in st.session_state:
    st.session_state.consulta = EJEMPLOS["M01 · Retraso por congestion, temporada alta"]

columna_ejemplo, columna_boton = st.columns([3, 1])
with columna_ejemplo:
    eleccion = st.selectbox(
        "Escenario de ejemplo",
        options=list(EJEMPLOS),
        index=0,
        help="Carga una consulta de prueba. Puedes editarla libremente.",
    )
with columna_boton:
    st.write("")
    if st.button("Cargar ejemplo", use_container_width=True):
        st.session_state.consulta = EJEMPLOS[eleccion]

consulta = st.text_area(
    "Consulta del analista",
    key="consulta",
    height=90,
    placeholder="Ej: el cliente del envio LR-2026-004182 reclama que no ha llegado...",
)

if st.button("Consultar al agente", type="primary"):
    if not consulta.strip():
        st.warning("Escribe una consulta.")
    else:
        try:
            with st.spinner("Recuperando fuentes y generando respuesta..."):
                st.session_state.resultado = responder(consulta)
        except ConfiguracionInvalida as error:
            st.error(f"Configuracion invalida: {error}")
        except Exception as error:  # noqa: BLE001 - la UI informa en vez de romperse
            st.error(f"{type(error).__name__}: {error}")

resultado: ResultadoAgente | None = st.session_state.get("resultado")

if resultado is not None:
    titulo_tipo, glosa_tipo = ETIQUETAS_TIPO.get(resultado.tipo, (resultado.tipo, ""))

    metrica_1, metrica_2, metrica_3, metrica_4 = st.columns(4)
    metrica_1.metric("Flujo", titulo_tipo)
    metrica_2.metric("Recuperacion", f"{resultado.latencia_recuperacion_s} s")
    metrica_3.metric("Generacion (LLM)", f"{resultado.latencia_llm_s} s")
    metrica_4.metric("Fragmentos", len(resultado.fragmentos))
    st.caption(glosa_tipo)

    if resultado.tipo == "error":
        st.error(resultado.error or "Error desconocido")

    pestanas = st.tabs(
        [
            "Respuesta",
            "Hechos verificados",
            "Fragmentos recuperados",
            "Consultas de recuperacion",
            "Prompt enviado",
        ]
    )

    with pestanas[0]:
        st.markdown(resultado.respuesta or "_Sin respuesta._")

    with pestanas[1]:
        if resultado.hechos is None:
            st.info(
                "La consulta no menciona un codigo de envio, por lo que no se invoco la "
                "herramienta de tracking. El flujo se resolvio solo con recuperacion documental."
            )
        elif not resultado.hechos.encontrado:
            st.warning(resultado.hechos.mensaje_error or "Envio no encontrado.")
            st.caption(
                "No se llamo al modelo de lenguaje: sin hechos verificados, cualquier "
                "diagnostico seria inventado."
            )
        else:
            st.caption(
                "Calculados con pandas sobre los CSV, antes de llamar al LLM. El modelo recibe "
                "estos valores ya resueltos y no puede contradecirlos."
            )
            st.dataframe(tabla_hechos(resultado), hide_index=True, use_container_width=True)
            if resultado.hechos.eventos:
                with st.expander(f"Historial de tracking ({len(resultado.hechos.eventos)} eventos)"):
                    st.dataframe(
                        pd.DataFrame([vars(evento) for evento in resultado.hechos.eventos]),
                        hide_index=True,
                        use_container_width=True,
                    )

    with pestanas[2]:
        if not resultado.fragmentos:
            st.info("No se recuperaron fragmentos.")
        else:
            st.caption(
                "`RRF` es el score fusionado; `Rank denso` y `Rank BM25` son la posicion en cada "
                "recuperador. Un guion significa que ese recuperador no encontro el fragmento: "
                "ahi se ve el aporte de cada uno."
            )
            st.dataframe(tabla_fragmentos(resultado), hide_index=True, use_container_width=True)
            for numero, fragmento in enumerate(resultado.fragmentos, start=1):
                with st.expander(
                    f"[F{numero}] {fragmento.referencia} · fuente {fragmento.tipo_fuente} "
                    f"· {fragmento.recuperado_por}"
                ):
                    st.text(fragmento.texto.strip())

    with pestanas[3]:
        st.caption(
            "El agente no busca con la pregunta cruda del analista: deriva una consulta por "
            "aspecto del caso a partir de los hechos ya calculados. Por eso la herramienta de "
            "tracking no solo aporta datos, tambien mejora la recuperacion."
        )
        st.dataframe(
            pd.DataFrame(
                [{"Aspecto": aspecto, "Consulta enviada al recuperador": texto}
                 for aspecto, texto in resultado.consultas_rag.items()]
            ),
            hide_index=True,
            use_container_width=True,
        )

    with pestanas[4]:
        st.caption(
            "Prompt de usuario exacto que recibio el modelo, con los hechos y los fragmentos "
            "etiquetados. El prompt de sistema vive en `prompts/sistema_agente.md`."
        )
        st.code(resultado.prompt_usuario or "(sin prompt: no se llamo al LLM)", language="markdown")
