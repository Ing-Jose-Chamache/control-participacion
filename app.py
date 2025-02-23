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
        margin: 15px 0;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        position: relative;
    }
    .student-row::after {
        content: "";
        position: absolute;
        bottom: -15px;
        left: 50%;
        transform: translateX(-50%);
        width: 80%;
        height: 2px;
        background: linear-gradient(to right, transparent, #0066cc, transparent);
    }
    div[data-testid="stFileUploader"] {
        width: 50px;
        height: 50px;
        overflow: hidden;
    }
    div[data-testid="stFileUploader"] div {
        padding: 0 !important;
    }
    .stats-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .stats-highlight {
        color: #0066cc;
        font-weight: bold;
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

# Logo
col1, col2 = st.columns([1, 4])
with col1:
    logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'])
    if logo_file:
        st.image(logo_file, width=200)

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

# Mostrar preguntas en cuadro amarillo suave
if st.session_state.preguntas:
    st.markdown("<div class='question-container'>", unsafe_allow_html=True)
    col_prev, col_quest, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("←") and st.session_state.pregunta_actual > 0:
            st.session_state.pregunta_actual -= 1
    with col_quest:
        st.markdown(f"<div class='question-text'>Pregunta {st.session_state.pregunta_actual + 1}:</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='question-text'>{st.session_state.preguntas[st.session_state.pregunta_actual]}</div>", unsafe_allow_html=True)
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
    
    # Calcular estadísticas
    estudiantes_stats = []
    for _, estudiante in st.session_state.estudiantes.iterrows():
        correctas = sum(1 for r in estudiante['Respuestas'] if r == '1')
        porcentaje = (correctas / st.session_state.num_preguntas) * 100
        estudiantes_stats.append({
            'Nombre': estudiante['Nombre'],
            'Respuestas_Correctas': correctas,
            'Porcentaje': porcentaje
        })
    
    df_stats = pd.DataFrame(estudiantes_stats)
    
    # Mostrar estadísticas en 3 columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Gráfico de barras de respuestas correctas
        fig = px.bar(df_stats, x='Nombre', y='Respuestas_Correctas',
                    title='Respuestas Correctas por Estudiante',
                    color='Respuestas_Correctas',
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig)
    
    with col2:
        # Gráfico de torta para porcentaje de participación
        fig = px.pie(df_stats, values='Porcentaje', names='Nombre',
                    title='Distribución de Participación (%)')
        st.plotly_chart(fig)
    
    with col3:
        # Nueva estadística: Análisis de Rendimiento
        st.markdown("<div class='stats-container'>", unsafe_allow_html=True)
        st.markdown("#### Análisis de Rendimiento")
        
        # Calcular rendimiento promedio de la clase
        promedio_clase = df_stats['Porcentaje'].mean()
        mejor_estudiante = df_stats.loc[df_stats['Porcentaje'].idxmax()]
        estudiantes_riesgo = df_stats[df_stats['Porcentaje'] < 60]
        
        st.write(f"Promedio de la clase: **{promedio_clase:.1f}%**")
        st.write(f"Mejor rendimiento: **{mejor_estudiante['Nombre']}** ({mejor_estudiante['Porcentaje']:.1f}%)")
        st.write(f"Estudiantes en riesgo: **{len(estudiantes_riesgo)}**")
        
        # Mostrar niveles de rendimiento
        st.markdown("##### Niveles de Rendimiento:")
        
        # Clasificar estudiantes por nivel
        niveles = {
            'Excelente (90-100%)': df_stats[df_stats['Porcentaje'] >= 90]['Nombre'].tolist(),
            'Bueno (70-89%)': df_stats[(df_stats['Porcentaje'] >= 70) & (df_stats['Porcentaje'] < 90)]['Nombre'].tolist(),
            'Regular (60-69%)': df_stats[(df_stats['Porcentaje'] >= 60) & (df_stats['Porcentaje'] < 70)]['Nombre'].tolist(),
            'En riesgo (<60%)': df_stats[df_stats['Porcentaje'] < 60)]['Nombre'].tolist()
        }
        
        for nivel, estudiantes in niveles.items():
            cantidad = len(estudiantes)
            st.write(f"{nivel}: **{cantidad}** estudiantes")
            if cantidad > 0:
                nombres = ", ".join(estudiantes)
                if nivel == 'Excelente (90-100%)':
                    st.markdown(f"**Estudiantes**: _{nombres}_")
                else:
                    st.write(f"Estudiantes: {nombres}")
        
        # Destacar mejor estudiante
        if not df_stats.empty:
            mejor = df_stats.loc[df_stats['Porcentaje'].idxmax()]
            st.markdown("---")
            st.markdown(f"⭐ **Mejor estudiante**: **{mejor['Nombre']}** con **{mejor['Porcentaje']:.1f}%** de rendimiento")
        
        st.markdown("</div>", unsafe_allow_html=True)
