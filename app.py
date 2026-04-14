import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from calculator import calculate_footprint, calculate_equivalences
from database import save_response
from analysis import load_data

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Huella de Carbono · ITZ",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos personalizados ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d2b1f 0%, #1a4a32 100%);
}
[data-testid="stSidebar"] * { color: #e8f5e9 !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 0.95rem; }

/* Encabezado principal */
.main-header {
    background: linear-gradient(135deg, #0d2b1f 0%, #1b5e3b 60%, #2e7d52 100%);
    color: white;
    padding: 2.5rem 2rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: "🌿";
    position: absolute;
    right: 2rem;
    top: 1rem;
    font-size: 5rem;
    opacity: 0.15;
}
.main-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.5px;
}
.main-header p {
    margin: 0;
    opacity: 0.8;
    font-size: 1rem;
    font-weight: 300;
}

/* Tarjetas de sección */
.section-card {
    background: #f8fdf9;
    border: 1px solid #c8e6c9;
    border-left: 4px solid #2e7d52;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
}
.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1b5e3b;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Resultado huella */
.result-box {
    background: linear-gradient(135deg, #0d2b1f, #1b5e3b);
    color: white;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin: 1.5rem 0;
}
.result-box .big-number {
    font-family: 'DM Serif Display', serif;
    font-size: 3.5rem;
    line-height: 1;
    color: #a5d6a7;
}
.result-box .unit { font-size: 1.1rem; opacity: 0.8; margin-top: 0.3rem; }
.result-box .label { font-size: 0.9rem; opacity: 0.6; margin-top: 0.2rem; }

/* Equivalencias */
.equiv-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; margin-top: 1rem; }
.equiv-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 10px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.equiv-card .equiv-icon { font-size: 1.6rem; }
.equiv-card .equiv-val { font-size: 1.2rem; font-weight: 600; color: #a5d6a7; margin: 0.2rem 0; }
.equiv-card .equiv-label { font-size: 0.72rem; opacity: 0.7; line-height: 1.3; }

/* Métricas dashboard */
.metric-card {
    background: white;
    border: 1px solid #e0f2e9;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.metric-card .m-val {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #1b5e3b;
}
.metric-card .m-label { font-size: 0.8rem; color: #666; margin-top: 0.2rem; }

/* Botón principal */
div.stButton > button {
    background: linear-gradient(135deg, #1b5e3b, #2e7d52);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.7rem 2rem;
    font-size: 1rem;
    font-weight: 500;
    font-family: 'DM Sans', sans-serif;
    cursor: pointer;
    width: 100%;
    transition: all 0.2s;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #2e7d52, #388e3c);
    transform: translateY(-1px);
}

/* Comparador promedio */
.compare-bar {
    background: #e8f5e9;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-top: 0.8rem;
    font-size: 0.9rem;
    color: #1b5e3b;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 ITZ Carbon")
    st.markdown("---")
    pagina = st.radio(
        "Navegación",
        ["📋 Calcular mi huella", "📊 Dashboard universitario"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.78rem; opacity:0.6; line-height:1.6'>
    Proyecto de investigación sobre<br>
    huella de carbono universitaria.<br><br>
    Tus respuestas son anónimas y<br>
    se usan solo con fines académicos.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 1 — CALCULADORA
# ══════════════════════════════════════════════════════════════════════════════
if "📋" in pagina:

    st.markdown("""
    <div class="main-header">
        <h1>Calculadora de Huella de Carbono</h1>
        <p>Responde las siguientes preguntas para conocer tu impacto ambiental estimado anual</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("formulario_huella"):

        # ── Sección 1: Datos personales ──
        st.markdown('<div class="section-card"><div class="section-title">👤 Datos personales</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            genero = st.selectbox("Género", ["Hombre", "Mujer", "Otro / Prefiero no decir"])
        with col2:
            edad = st.slider("Edad", 17, 50, 21)
        with col3:
            carrera = st.selectbox("Carrera / Programa", [
                "Administración",
                "Ingeniería Ambiental",
                "Arquitectura",
                "Ing. Electrónica",
                "Ing. Industrial",
                "Ing. en Geociencias",
                "Ing. en Gestión Empresarial",
                "Ing. Mecánica",
                "Ing. en Sistemas Computacionales",
                "Posgrado",
            ])
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Sección 2: Transporte ──
        st.markdown('<div class="section-card"><div class="section-title">🚗 Transporte</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            transporte_principal = st.selectbox("Medio de transporte principal al campus", [
                "Automóvil propio (gasolina)",
                "Automóvil propio (diésel)",
                "Motocicleta",
                "Transporte público (camión/metro)",
                "Bicicleta",
                "A pie",
            ])
            distancia_diaria = st.number_input(
                "Distancia diaria al campus, ida y vuelta (km)",
                min_value=0.0, max_value=300.0, value=10.0, step=0.5
            )
        with col2:
            dias_campus = st.slider("Días por semana que vas al campus", 1, 7, 5)
            num_vehiculos = st.number_input(
                "Vehículos de motor en tu hogar (autos + motos)",
                min_value=0, max_value=10, value=1
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Sección 3: Energía en el hogar ──
        st.markdown('<div class="section-card"><div class="section-title">⚡ Energía en el hogar</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            electricidad_kwh = st.number_input(
                "Consumo eléctrico mensual del hogar (kWh)",
                min_value=0.0, max_value=2000.0, value=250.0, step=10.0,
                help="Puedes encontrarlo en tu recibo de CFE"
            )
        with col2:
            gas_kg = st.number_input(
                "Consumo mensual de gas LP (kg)",
                min_value=0.0, max_value=100.0, value=10.0, step=0.5,
                help="Un tanque estacionario de 20 kg dura ~1 mes en hogar promedio"
            )
        with col3:
            personas_hogar = st.number_input(
                "Personas en tu hogar",
                min_value=1, max_value=15, value=4
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Sección 4: Vuelos ──
        st.markdown('<div class="section-card"><div class="section-title">✈️ Viajes en avión</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            vuelos_cortos = st.number_input(
                "Vuelos cortos al año (< 3 horas, ej. CDMX–GDL)",
                min_value=0, max_value=50, value=0
            )
        with col2:
            vuelos_largos = st.number_input(
                "Vuelos largos al año (> 3 horas, ej. México–EUA)",
                min_value=0, max_value=30, value=0
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Sección 5: Dieta ──
        st.markdown('<div class="section-card"><div class="section-title">🍽️ Alimentación</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            tipo_dieta = st.selectbox("Tipo de dieta predominante", [
                "Omnívora con carne roja frecuente (casi diario)",
                "Omnívora moderada (carne 3–4 veces/semana)",
                "Omnívora baja en carne (1–2 veces/semana)",
                "Pescetariana (sin carne roja/ave)",
                "Vegetariana",
                "Vegana",
            ])
        with col2:
            desperdicio_comida = st.selectbox("¿Cuánto alimento desperdicias aproximadamente?", [
                "Poco o nada (termino casi todo)",
                "Moderado (tiro algo ocasionalmente)",
                "Bastante (tiro comida con frecuencia)",
            ])
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Sección 6: Residuos y hábitos ──
        st.markdown('<div class="section-card"><div class="section-title">♻️ Residuos y hábitos digitales</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            recicla = st.selectbox("¿Reciclas regularmente?", [
                "Sí, separo y reciclo activamente",
                "Ocasionalmente",
                "No reciclo",
            ])
            compostas = st.selectbox("¿Compostas residuos orgánicos?", [
                "Sí",
                "No",
            ])
        with col2:
            correos_inbox = st.number_input(
                "Correos sin leer en tu bandeja de entrada (aprox.)",
                min_value=0, max_value=100000, value=500, step=100,
                help="Cada correo almacenado consume energía en servidores"
            )
            streaming_horas = st.number_input(
                "Horas de streaming diarias (YouTube, Netflix, etc.)",
                min_value=0.0, max_value=16.0, value=2.0, step=0.5
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Botón ──
        submitted = st.form_submit_button("🌿 Calcular mi huella de carbono")

    # ── Resultado ────────────────────────────────────────────────────────────
    if submitted:
        data = {
            "genero": genero,
            "edad": edad,
            "carrera": carrera,
            "transporte_principal": transporte_principal,
            "distancia_diaria_km": distancia_diaria,
            "dias_campus_semana": dias_campus,
            "num_vehiculos_hogar": num_vehiculos,
            "electricidad_kwh_mes": electricidad_kwh,
            "gas_lp_kg_mes": gas_kg,
            "personas_hogar": personas_hogar,
            "vuelos_cortos_anio": vuelos_cortos,
            "vuelos_largos_anio": vuelos_largos,
            "tipo_dieta": tipo_dieta,
            "desperdicio_comida": desperdicio_comida,
            "recicla": recicla,
            "compostas": compostas,
            "correos_inbox": correos_inbox,
            "streaming_horas_dia": streaming_horas,
        }

        huella = calculate_footprint(data)
        equiv = calculate_equivalences(huella)
        data["huella_ton_co2"] = huella

        save_response(data)

        # Resultado visual
        nivel = "🟢 Bajo" if huella < 2 else ("🟡 Moderado" if huella < 4 else "🔴 Alto")

        st.markdown(f"""
        <div class="result-box">
            <div style="font-size:0.85rem; opacity:0.7; margin-bottom:0.5rem">TU HUELLA DE CARBONO ANUAL ESTIMADA</div>
            <div class="big-number">{huella:.2f}</div>
            <div class="unit">toneladas de CO₂ equivalente / año</div>
            <div style="margin-top:0.8rem; font-size:1rem">{nivel}</div>
            <div class="equiv-grid">
                <div class="equiv-card">
                    <div class="equiv-icon">🌳</div>
                    <div class="equiv-val">{equiv['arboles']:,}</div>
                    <div class="equiv-label">árboles necesarios para absorber tu huella en 1 año</div>
                </div>
                <div class="equiv-card">
                    <div class="equiv-icon">💡</div>
                    <div class="equiv-val">{equiv['bombillas']:,}</div>
                    <div class="equiv-label">bombillas LED de 10W encendidas todo el año</div>
                </div>
                <div class="equiv-card">
                    <div class="equiv-icon">🚗</div>
                    <div class="equiv-val">{equiv['km_carro']:,}</div>
                    <div class="equiv-label">km en auto de gasolina equivalentes</div>
                </div>
                <div class="equiv-card">
                    <div class="equiv-icon">♻️</div>
                    <div class="equiv-val">{equiv['plastico_kg']:,} kg</div>
                    <div class="equiv-label">de plástico a reciclar para compensar</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Desglose por categoría
        st.markdown("#### Desglose por categoría")
        categorias = {
            "Transporte diario": equiv["desglose"]["transporte"],
            "Vuelos": equiv["desglose"]["vuelos"],
            "Electricidad": equiv["desglose"]["electricidad"],
            "Gas LP": equiv["desglose"]["gas"],
            "Dieta": equiv["desglose"]["dieta"],
            "Residuos y digital": equiv["desglose"]["residuos"],
        }
        df_desglose = pd.DataFrame({
            "Categoría": list(categorias.keys()),
            "ton CO₂/año": list(categorias.values())
        }).sort_values("ton CO₂/año", ascending=True)

        fig = px.bar(
            df_desglose,
            x="ton CO₂/año",
            y="Categoría",
            orientation="h",
            color="ton CO₂/año",
            color_continuous_scale=["#a5d6a7", "#2e7d52", "#1b3a2a"],
            title="Contribución por categoría (ton CO₂/año)",
        )
        fig.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="DM Sans",
            showlegend=False,
            margin=dict(l=0, r=20, t=40, b=0),
        )
        fig.update_xaxes(showgrid=True, gridcolor="#e8f5e9")
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)

        st.success("✅ Tu respuesta fue registrada. ¡Gracias por participar en el proyecto!")


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
else:

    st.markdown("""
    <div class="main-header">
        <h1>Dashboard Universitario</h1>
        <p>Análisis estadístico de la huella de carbono en el campus</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()

    if df.empty:
        st.warning("⚠️ Aún no hay datos registrados. Sé el primero en calcular tu huella.")
        st.stop()

    # ── Filtros ──
    with st.expander("🔍 Filtros", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            carreras_disponibles = ["Todas"] + sorted(df["carrera"].dropna().unique().tolist())
            carrera_filtro = st.selectbox("Carrera", carreras_disponibles)
        with col2:
            generos_disponibles = ["Todos"] + sorted(df["genero"].dropna().unique().tolist())
            genero_filtro = st.selectbox("Género", generos_disponibles)

    df_f = df.copy()
    if carrera_filtro != "Todas":
        df_f = df_f[df_f["carrera"] == carrera_filtro]
    if genero_filtro != "Todos":
        df_f = df_f[df_f["genero"] == genero_filtro]

    if df_f.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    # ── KPIs ──
    promedio = df_f["huella_ton_co2"].mean()
    mediana = df_f["huella_ton_co2"].median()
    maximo = df_f["huella_ton_co2"].max()
    n = len(df_f)

    col1, col2, col3, col4 = st.columns(4)
    for col, val, label in zip(
        [col1, col2, col3, col4],
        [n, f"{promedio:.2f}", f"{mediana:.2f}", f"{maximo:.2f}"],
        ["Respuestas", "Promedio (ton CO₂)", "Mediana (ton CO₂)", "Máximo (ton CO₂)"]
    ):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="m-val">{val}</div>
                <div class="m-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gráficas ──
    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df_f, x="huella_ton_co2", nbins=20,
            title="Distribución de huella de carbono",
            labels={"huella_ton_co2": "ton CO₂/año"},
            color_discrete_sequence=["#2e7d52"],
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_family="DM Sans")
        fig.update_xaxes(showgrid=True, gridcolor="#e8f5e9")
        fig.update_yaxes(showgrid=True, gridcolor="#e8f5e9")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.box(
            df_f, x="carrera", y="huella_ton_co2",
            title="Huella por carrera",
            labels={"huella_ton_co2": "ton CO₂/año", "carrera": ""},
            color="carrera",
            color_discrete_sequence=px.colors.sequential.Greens_r,
        )
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_family="DM Sans", showlegend=False,
            xaxis_tickangle=-35,
        )
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        transp_counts = df_f["transporte_principal"].value_counts().reset_index()
        transp_counts.columns = ["Transporte", "Conteo"]
        fig3 = px.pie(
            transp_counts, values="Conteo", names="Transporte",
            title="Distribución de transporte",
            color_discrete_sequence=px.colors.sequential.Greens,
            hole=0.4,
        )
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_family="DM Sans")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = px.box(
            df_f, x="genero", y="huella_ton_co2",
            title="Huella por género",
            labels={"huella_ton_co2": "ton CO₂/año", "genero": ""},
            color="genero",
            color_discrete_sequence=["#1b5e3b", "#4caf50", "#a5d6a7"],
        )
        fig4.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_family="DM Sans", showlegend=False,
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ── Dieta vs huella ──
    fig5 = px.bar(
        df_f.groupby("tipo_dieta")["huella_ton_co2"].mean().reset_index().sort_values("huella_ton_co2"),
        x="huella_ton_co2", y="tipo_dieta", orientation="h",
        title="Huella promedio por tipo de dieta",
        labels={"huella_ton_co2": "Promedio ton CO₂/año", "tipo_dieta": ""},
        color="huella_ton_co2",
        color_continuous_scale=["#a5d6a7", "#1b5e3b"],
    )
    fig5.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_family="DM Sans", coloraxis_showscale=False,
    )
    st.plotly_chart(fig5, use_container_width=True)

    # ── Tabla de datos ──
    with st.expander("📄 Ver datos crudos"):
        st.dataframe(df_f, use_container_width=True)
        csv = df_f.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar CSV", csv, "huella_carbono.csv", "text/csv")
