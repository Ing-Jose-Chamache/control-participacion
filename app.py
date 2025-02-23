import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
from io import StringIO

# Configuración de la página
st.set_page_config(page_title="CONTROL DE PARTICIPACIÓN", layout="wide")

# Estilo personalizado
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stButton>button {
        background-color: transparent;
        border: none;
    }
    .circle-btn {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        margin: 0 5px;
        cursor: pointer;
        display: inline-block;
    }
    .black-circle {
        background-color: black;
        color: white;
    }
    .yellow-circle {
        background-color: yellow;
        color: black;
    }
    .title {
        font-size: 2em;
        font-weight: bold;
        text-align: center;
        margin: 1em 0;
    }
    .question-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }
    .student-row {
        display: flex;
        align-items: center;
        padding: 10px;
        margin: 5px 0;
        background-color: #ffffff;
        border-radius: 5px;
    }
    div[data-testid="stFileUploader"] {
        width: 50px;
        height: 50px;
        overflow: hidden;
    }
    div[data-testid="stFileUploader"] div {
        padding: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'estudiantes' not in st.session_state:
    st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Respuestas'])
if 'preguntas' not in st.session_state:
    st.session_state.preguntas = []
if 'pregunta_actual' not in st.session_state:
    st.session_state.pregunta_actual = 0
if 'num_preguntas' not in st.session_state:
    st.session_state.num_preguntas = 5

# Logo y título
col1, col2 = st.columns([1, 4])
with col1:
    logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'])
    if logo_file:
        st.image(logo_file, width=200)
with col2:
    st.markdown("<h1 class='title'>CONTROL DE PARTICIPACIÓN</h1>", unsafe_allow_html=True)

# Configuración
col_nombre, col_num, _ = st.columns([2, 1, 1])
with col_nombre:
    nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE")
with col_num:
    num_preguntas = st.number_input("NÚMERO DE PREGUNTAS", min_value=1, value=5)
    st.session_state.num_preguntas = num_preguntas

# Botón para agregar estudiante
if st.button("AGREGAR ESTUDIANTE") and nuevo_estudiante:
    if nuevo_estudiante not in st.session_state.estudiantes['Nombre'].values:
        nuevo_df = pd.DataFrame({
            'Nombre': [nuevo_estudiante],
            'Respuestas': ['0' * st.session_state.num_preguntas]
        })
        st.session_state.estudiantes = pd.concat([st.session_state.estudiantes, nuevo_df], ignore_index=True)

# Mostrar preguntas
if st.session_state.preguntas:
    st.markdown("<div class='question-container'>", unsafe_allow_html=True)
    col_prev, col_quest, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("←") and st.session_state.pregunta_actual > 0:
            st.session_state.pregunta_actual -= 1
    with col_quest:
        st.write(f"### Pregunta {st.session_state.pregunta_actual + 1}")
        st.write(st.session_state.preguntas[st.session_state.pregunta_actual])
    with col_next:
        if st.button("→") and st.session_state.pregunta_actual < len(st.session_state.preguntas) - 1:
            st.session_state.pregunta_actual += 1
    st.markdown("</div>", unsafe_allow_html=True)

# Mostrar estudiantes y círculos
for idx, estudiante in st.session_state.estudiantes.iterrows():
    col1, col2, col3 = st.columns([2, 6, 1])
    with col1:
        st.write(estudiante['Nombre'])
    with col2:
        respuestas = list(estudiante['Respuestas'])
        for i in range(st.session_state.num_preguntas):
            if st.button("⬤", key=f"{estudiante['Nombre']}_{i}", 
                        help="Click para marcar respuesta",
                        type="secondary" if respuestas[i] == '0' else "primary"):
                respuestas_list = list(st.session_state.estudiantes.loc[idx, 'Respuestas'])
                respuestas_list[i] = '1' if respuestas_list[i] == '0' else '0'
                st.session_state.estudiantes.loc[idx, 'Respuestas'] = ''.join(respuestas_list)
                st.rerun()
    with col3:
        if st.button("🗑️", key=f"delete_{estudiante['Nombre']}"):
            st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)
            st.rerun()

# Cargar preguntas
txt_file = st.file_uploader("", type=['txt'])
if txt_file:
    contenido = StringIO(txt_file.getvalue().decode("utf-8")).read().splitlines()
    st.session_state.preguntas = [linea.strip() for linea in contenido if linea.strip()]
    st.success(f"Se cargaron {len(st.session_state.preguntas)} preguntas")

# Estadísticas
if not st.session_state.estudiantes.empty:
    st.markdown("### Estadísticas de Participación")
    col1, col2 = st.columns(2)
    
    with col1:
        # Calcular respuestas correctas por estudiante
        estudiantes_stats = []
        for _, estudiante in st.session_state.estudiantes.iterrows():
            correctas = sum(1 for r in estudiante['Respuestas'] if r == '1')
            estudiantes_stats.append({
                'Nombre': estudiante['Nombre'],
                'Respuestas_Correctas': correctas
            })
        
        df_stats = pd.DataFrame(estudiantes_stats)
        fig = px.bar(df_stats, x='Nombre', y='Respuestas_Correctas',
                    title='Respuestas Correctas por Estudiante')
        st.plotly_chart(fig)
    
    with col2:
        # Gráfico de torta para porcentaje de participación
        total_preguntas = st.session_state.num_preguntas
        df_stats['Porcentaje'] = (df_stats['Respuestas_Correctas'] / total_preguntas * 100).round(2)
        fig = px.pie(df_stats, values='Porcentaje', names='Nombre',
                    title='Porcentaje de Participación')
        st.plotly_chart(fig)
