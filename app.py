import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import base64
from io import StringIO

# Configuración de la página
st.set_page_config(page_title="Control de Participación", layout="wide")

# Estilo personalizado
st.markdown("""
    <style>
    .main {
        padding: 1rem;
        background-color: #f5f5f5;
    }
    .stApp {
        background-color: #f5f5f5;
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
    .question-container {
        background-color: #FFFACD;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .question-text {
        color: #0066cc;
        font-size: 1.2em;
        font-weight: 500;
    }
    .student-row {
        display: flex;
        align-items: center;
        padding: 15px;
        margin: 20px 0;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .student-separator {
        text-align: center;
        padding: 10px 0;
    }
    .separator-dots {
        color: #0066cc;
        letter-spacing: 3px;
        font-size: 20px;
    }
    .separator-line {
        height: 2px;
        background: linear-gradient(to right, transparent, #0066cc, transparent);
        margin: 5px auto;
        width: 80%;
    }
    div[data-testid="stFileUploader"] {
        width: 50px;
        height: 50px;
        overflow: hidden;
        background-color: #4d4d4d;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    div[data-testid="stFileUploader"] div {
        padding: 0 !important;
    }
    div[data-testid="stFileUploader"]:hover {
        background-color: #666666;
    }
    .upload-container {
        position: fixed;
        z-index: 1000;
        display: flex;
        gap: 10px;
    }
    .upload-logo {
        top: 10px;
        left: 10px;
    }
    .upload-students {
        top: 70px;
        left: 10px;
    }
    .upload-questions {
        bottom: 10px;
        right: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialización del estado
if 'estudiantes' not in st.session_state:
    st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Respuestas', 'Respuestas_Correctas'])
if 'preguntas' not in st.session_state:
    st.session_state.preguntas = []
if 'pregunta_actual' not in st.session_state:
    st.session_state.pregunta_actual = 0
if 'num_preguntas' not in st.session_state:
    st.session_state.num_preguntas = 5

# Botones de carga
st.markdown('<div class="upload-container upload-logo">', unsafe_allow_html=True)
logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="logo")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="upload-container upload-students">', unsafe_allow_html=True)
students_file = st.file_uploader("", type=['txt'], key="students")
st.markdown('</div>', unsafe_allow_html=True)

if logo_file:
    st.image(logo_file, width=200)

# Configuración inicial
col1, col2, _ = st.columns([2, 1, 1])
with col1:
    nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE")
with col2:
    num_preguntas = st.number_input("NÚMERO DE PREGUNTAS", min_value=1, value=5)
    st.session_state.num_preguntas = num_preguntas

# Botón para agregar estudiante
if st.button("AGREGAR ESTUDIANTE") and nuevo_estudiante:
    if nuevo_estudiante not in st.session_state.estudiantes['Nombre'].values:
        nuevo_df = pd.DataFrame({
            'Nombre': [nuevo_estudiante],
            'Respuestas': ['0' * st.session_state.num_preguntas],
            'Respuestas_Correctas': [0]
        })
        st.session_state.estudiantes = pd.concat([st.session_state.estudiantes, nuevo_df], ignore_index=True)

# Cargar estudiantes desde archivo
if students_file:
    try:
        contenido = StringIO(students_file.getvalue().decode("utf-8")).read().splitlines()
        for estudiante in contenido:
            if estudiante.strip() and estudiante not in st.session_state.estudiantes['Nombre'].values:
                nuevo_df = pd.DataFrame({
                    'Nombre': [estudiante.strip()],
                    'Respuestas': ['0' * st.session_state.num_preguntas],
                    'Respuestas_Correctas': [0]
                })
                st.session_state.estudiantes = pd.concat([st.session_state.estudiantes, nuevo_df], ignore_index=True)
        st.success(f"Se cargaron {len(contenido)} estudiantes")
    except Exception as e:
        st.error(f"Error al cargar estudiantes: {str(e)}")

# Mostrar preguntas
if st.session_state.preguntas:
    st.markdown("<div class='question-container'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("←") and st.session_state.pregunta_actual > 0:
            st.session_state.pregunta_actual -= 1
            st.rerun()
    with col2:
        st.markdown(f"<div class='question-text'>Pregunta {st.session_state.pregunta_actual + 1}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='question-text'>{st.session_state.preguntas[st.session_state.pregunta_actual]}</div>", unsafe_allow_html=True)
    with col3:
        if st.button("→") and st.session_state.pregunta_actual < len(st.session_state.preguntas) - 1:
            st.session_state.pregunta_actual += 1
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Mostrar estudiantes
for idx, estudiante in st.session_state.estudiantes.iterrows():
    st.markdown("<div class='student-row'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 6, 1])
    with col1:
        st.write(estudiante['Nombre'])
    with col2:
        for i in range(st.session_state.num_preguntas):
            respuestas = list(estudiante['Respuestas'])
            if st.button("⬤", key=f"circle_{estudiante['Nombre']}_{i}", 
                        help="Click para marcar respuesta",
                        type="secondary" if respuestas[i] == '0' else "primary"):
                respuestas[i] = '1' if respuestas[i] == '0' else '0'
                st.session_state.estudiantes.loc[idx, 'Respuestas'] = ''.join(respuestas)
                st.session_state.estudiantes.loc[idx, 'Respuestas_Correctas'] = sum(1 for r in respuestas if r == '1')
                st.rerun()
    with col3:
        if st.button("🗑️", key=f"delete_{estudiante['Nombre']}"):
            st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Separador decorativo entre estudiantes
    st.markdown("""
        <div class="student-separator">
            <div class="separator-dots">• • •</div>
            <div class="separator-line"></div>
        </div>
    """, unsafe_allow_html=True)

# Cargar preguntas
st.markdown('<div class="upload-container upload-questions">', unsafe_allow_html=True)
questions_file = st.file_uploader("", type=['txt'], key="questions")
st.markdown('</div>', unsafe_allow_html=True)

if questions_file:
    contenido = StringIO(questions_file.getvalue().decode("utf-8")).read().splitlines()
    st.session_state.preguntas = [linea.strip() for linea in contenido if linea.strip()]
    st.success(f"Se cargaron {len(st.session_state.preguntas)} preguntas")

# Estadísticas
if not st.session_state.estudiantes.empty:
    st.markdown("### Estadísticas de Participación")
    
    # Preparar datos para estadísticas
    df_stats = pd.DataFrame({
        'Nombre': st.session_state.estudiantes['Nombre'],
        'Respuestas_Correctas': st.session_state.estudiantes['Respuestas'].apply(lambda x: sum(1 for r in x if r == '1')),
        'Porcentaje': st.session_state.estudiantes['Respuestas'].apply(lambda x: sum(1 for r in x if r == '1') / st.session_state.num_preguntas * 100)
    })
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig = px.bar(df_stats, x='Nombre', y='Respuestas_Correctas',
                    title='Respuestas Correctas por Estudiante',
                    color='Respuestas_Correctas',
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig)
    
    with col2:
        fig = px.pie(df_stats, values='Porcentaje', names='Nombre',
                    title='Distribución de Participación (%)')
        st.plotly_chart(fig)
    
    with col3:
        st.markdown("<div class='stats-container'>", unsafe_allow_html=True)
        st.markdown("#### Análisis de Rendimiento")
        
        # Mejor estudiante
        mejor_estudiante = df_stats.loc[df_stats['Porcentaje'].idxmax()]
        st.markdown(f"🏆 **Mejor estudiante**: **{mejor_estudiante['Nombre']}** ({mejor_estudiante['Porcentaje']:.1f}%)")
        
        # Clasificación por niveles
        st.markdown("##### Niveles de Rendimiento:")
        niveles = {
            'Excelente (90-100%)': df_stats[df_stats['Porcentaje'] >= 90]['Nombre'].tolist(),
            'Bueno (70-89%)': df_stats[(df_stats['Porcentaje'] >= 70) & (df_stats['Porcentaje'] < 90)]['Nombre'].tolist(),
            'Regular (60-69%)': df_stats[(df_stats['Porcentaje'] >= 60) & (df_stats['Porcentaje'] < 70)]['Nombre'].tolist(),
            'En riesgo (<60%)': df_stats[df_stats['Porcentaje'] < 60]['Nombre'].tolist()
        }

        for nivel, estudiantes in niveles.items():
            st.write(f"{nivel}: **{len(estudiantes)}** estudiantes")
            if estudiantes:
                st.write(f"_{', '.join(estudiantes)}_")
        
        st.markdown("</div>", unsafe_allow_html=True)
