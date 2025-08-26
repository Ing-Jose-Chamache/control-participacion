import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import base64
from io import StringIO
import json
import os
import uuid  # Importamos uuid para generar IDs únicos de sesión
import pytz  # Para zonas horarias

# Configuración de la página - DEBE SER LO PRIMERO
st.set_page_config(page_title="Control de Participación", layout="wide")

# Crear directorio para las sesiones en caso de que no exista
if not os.path.exists('sesiones'):
    try:
        os.makedirs('sesiones')
    except Exception as e:
        pass  # Ignorar errores silenciosamente

# Uso de query parameters para mantener el ID de sesión
query_params = st.query_params
session_param = query_params.get('session_id', [None])[0]

# Modificación: Inicialización del ID de sesión
if 'session_id' not in st.session_state or session_param:
    # Si hay un ID en el parámetro de URL, lo usamos
    if session_param:
        st.session_state.session_id = session_param
    # De lo contrario generamos uno nuevo
    else:
        st.session_state.session_id = str(uuid.uuid4())
        # Actualizamos la URL con el nuevo ID de sesión
        query_params['session_id'] = st.session_state.session_id
    
# Mostrar ID de sesión estéticamente en la barra lateral
st.sidebar.markdown(f"""
    <div style='
        background-color: #f0f8ff;
        padding: 10px 15px;
        border-radius: 8px;
        border-left: 4px solid #0066cc;
        margin-bottom: 15px;
        font-size: 0.9em;
        font-family: monospace;
        display: inline-block;
    '>
        <span style='color: #555;'>ID:</span> <span style='color: #0066cc; font-weight: bold;'>{st.session_state.session_id[:8]}...</span>
    </div>
""", unsafe_allow_html=True)
# Funciones de persistencia
def save_state():
    # Usar el ID de sesión en el nombre del archivo
    state_data = {
        'estudiantes': st.session_state.estudiantes.to_dict(),
        'preguntas': st.session_state.preguntas,
        'pregunta_actual': st.session_state.pregunta_actual,
        'num_preguntas': st.session_state.num_preguntas
    }
    # Guardar en un archivo específico para esta sesión
    with open(f'sesiones/app_state_{st.session_state.session_id}.json', 'w') as f:
        json.dump(state_data, f)

def load_state():
    try:
        # Cargar desde el archivo específico de esta sesión
        session_file = f'sesiones/app_state_{st.session_state.session_id}.json'
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                state_data = json.load(f)
            # Restaurar el DataFrame
            st.session_state.estudiantes = pd.DataFrame.from_dict(state_data['estudiantes'])
            st.session_state.preguntas = state_data['preguntas']
            st.session_state.pregunta_actual = state_data['pregunta_actual']
            st.session_state.num_preguntas = state_data['num_preguntas']
            return True
        return False
    except Exception as e:
        print(f"Error loading state: {e}")
        return False

def reset_state():
    # Eliminar solo el archivo de la sesión actual
    session_file = f'sesiones/app_state_{st.session_state.session_id}.json'
    if os.path.exists(session_file):
        os.remove(session_file)
    st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Respuestas', 'Respuestas_Correctas'])
    st.session_state.preguntas = []
    st.session_state.pregunta_actual = 0
    st.session_state.num_preguntas = 5
    # Generar un nuevo ID de sesión para forzar una nueva sesión
    st.session_state.session_id = str(uuid.uuid4())
    # Actualizar la URL con el nuevo ID
    st.query_params['session_id'] = st.session_state.session_id

# Función para descargar CSV
def download_csv(df):
    # Preparamos datos para el análisis completo
    data_export = df.copy()
    
    # Añadimos columnas para el análisis completo
    data_export['Nota_Vigesimal'] = data_export['Respuestas_Correctas'].apply(
        lambda x: round((x / st.session_state.num_preguntas) * 20, 1)
    )
    
    # Añadimos columna de estado
    data_export['Estado'] = data_export['Nota_Vigesimal'].apply(
        lambda nota: "APROBADO" if nota >= 14 else ("REGULAR" if nota >= 11 else "DESAPROBADO")
    )
    
    # Añadimos columna de nivel de rendimiento
    data_export['Nivel_Rendimiento'] = data_export['Porcentaje'].apply(
        lambda p: "Excelente (90-100%)" if p >= 90 else 
                 ("Bueno (70-89%)" if p >= 70 else 
                  ("Regular (60-69%)" if p >= 60 else "En riesgo (<60%)"))
    )
    
    # Exportamos el CSV
    csv = data_export.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="estadisticas_completas.csv" class="download-button">📊 Descargar Estadísticas Completas (CSV)</a>'
    return href
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
    button[data-testid="baseButton-secondary"] {
        background-color: transparent !important;
        color: #808080 !important;
    }
    button[data-testid="baseButton-primary"] {
        background-color: #0066cc !important;
        color: white !important;
    }
    div[data-testid="stFileUploader"] {
        width: 50px;
        height: 50px;
        overflow: hidden;
        background-color: #9b9b9b;
    }
    div[data-testid="stFileUploader"] div {
        padding: 0 !important;
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
        font-weight: bold;
        margin: 10px 0;
    }
    .question-number {
        font-size: 1.1em;
        color: #333;
        font-weight: bold;
        margin-bottom: 5px;
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
    .upload-container {
        position: fixed;
        z-index: 1000;
        width: 50px;
    }
    .upload-logo {
        top: 10px;
        left: 10px;
    }
    .upload-students {
        bottom: 10px;
        right: 70px;
    }
    .upload-questions {
        bottom: 10px;
        right: 10px;
    }
    .reset-button {
        position: fixed;
        top: 10px;
        right: 70px;
        z-index: 1000;
    }
    .reset-button button {
        background-color: #dc3545 !important;
        color: white !important;
        padding: 8px 16px !important;
        border-radius: 4px !important;
        border: none !important;
    }
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { 
        -webkit-appearance: none;
        margin: 0;
    }
    input[type=number] {
        -moz-appearance: textfield;
        padding: 5px;
        font-size: 16px;
    }
    .performance-stats {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stats-title {
        color: #0066cc;
        font-size: 1.2em;
        margin-bottom: 15px;
        text-align: center;
    }
    .stats-subtitle {
        color: #333;
        font-size: 1.1em;
        margin: 12px 0;
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
    }
    .stats-highlight {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 8px 0;
    }
    .credits {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 12px;
        border-radius: 8px;
        margin-top: 25px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        font-size: 0.85em;
        clear: both;
    }
    .credits h2 {
        color: #0066cc;
        font-size: 1.1em;
        margin-bottom: 12px;
        font-weight: bold;
    }
    .credits-info {
        color: #666;
        font-size: 0.9em;
        line-height: 1.5;
        margin: 6px 0;
    }
    .credits-divider {
        height: 1px;
        background: linear-gradient(to right, transparent, #0066cc, transparent);
        margin: 8px auto;
        width: 35%;
        opacity: 0.4;
    }
    /* Nuevos estilos para el header */
    .header-section {
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        padding: 20px;
        margin: 20px 0;
    }
    
    /* Estilos para el reloj de Perú - MODIFICACIÓN DE LA POSICIÓN */
    .peru-clock {
        position: absolute;
        right: 50px;
        top: -800px; /* Modificado: Movido mucho más arriba para alinearlo con la cabeza del personaje */
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        text-align: center;
        font-family: 'Courier New', monospace;
        border: 2px solid #ff0000; /* Borde rojo para mayor visibilidad */
        z-index: 9999; /* Asegurar que esté por encima de otros elementos */
    }
    .clock-time {
        font-size: 2em;
        font-weight: bold;
        color: #333;
        margin: 5px 0;
    }
    .clock-date {
        font-size: 0.9em;
        color: #666;
    }
    .clock-title {
        font-size: 0.8em;
        font-weight: bold;
        color: #0066cc;
        margin-bottom: 3px;
        text-transform: uppercase;
    }
    
    .logo-container {
        margin: 0 auto;
        text-align: center;
    }
    .ruleta-link {
        position: absolute;
        right: 220px;
        top: 30px;
        transform: none;
    }
    /* Nuevo botón de descarga */
    .download-button {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        padding: 10px 15px;
        text-align: center;
        text-decoration: none;
        border-radius: 5px;
        margin: 10px 0;
        font-weight: bold;
    }
    .download-button:hover {
        background-color: #45a049;
    }
    /* Estilos para el botón de ChatGPT */
    .chatgpt-link {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 1001;
    }
    .chatgpt-link a {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 40px;
        height: 40px;
        background-color: #10a37f;
        border-radius: 50%;
        text-align: center;
        font-size: 14px;
        color: white;
        font-weight: bold;
        text-decoration: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        z-index: 9999;
    }
    .chatgpt-link a:hover {
        background-color: #0d8c6d;
        transform: scale(1.05);
    }
    /* Estilos para el botón de AnyDesk */
    .anydesk-button {
        position: relative !important;
        display: block !important;
        width: fit-content !important;
        margin: 15px auto !important;
        z-index: 1002 !important;
    }
    .anydesk-link {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #ef443b !important;
        color: white !important;
        font-weight: bold !important;
        padding: 10px 18px !important;
        border-radius: 8px !important;
        text-decoration: none !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        font-size: 1em !important;
        transition: transform 0.2s ease !important;
    }
    .anydesk-link:hover {
        background-color: #d63c33 !important;
        transform: scale(1.05);
    }
    /* Estilos para el menú de IA */
    .ia-menu {
        position: fixed !important;
        top: 85px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 9999 !important;
    }
    .ia-button {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 60px !important;
        height: 60px !important;
        background-color: #7b2cbf !important;
        border-radius: 50% !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 18px !important;
        text-decoration: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        cursor: pointer !important;
        background-image: url('https://cdn-icons-png.flaticon.com/512/6295/6295417.png') !important;
        background-size: 65% !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
    }
    .ia-dropdown {
        display: none;
        position: absolute;
        right: 0;
        top: 50px;
        background-color: #ffffff;
        min-width: 160px;
        box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
        z-index: 9999;
        border-radius: 5px;
        overflow: hidden;
    }
    .ia-dropdown a {
        color: black;
        padding: 12px 16px;
        text-decoration: none;
        display: block;
        border-bottom: 1px solid #f1f1f1;
        font-size: 14px;
    }
    .ia-dropdown a:hover {
        background-color: #f1f1f1;
    }
    .ia-menu:hover .ia-dropdown {
        display: block;
    }
    </style>
""", unsafe_allow_html=True)
# Inicialización del estado antes de cargar
if 'estudiantes' not in st.session_state:
    st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Respuestas', 'Respuestas_Correctas'])
if 'preguntas' not in st.session_state:
    st.session_state.preguntas = []
if 'pregunta_actual' not in st.session_state:
    st.session_state.pregunta_actual = 0
if 'num_preguntas' not in st.session_state:
    st.session_state.num_preguntas = 5

# Cargar estado al inicio
if 'state_loaded' not in st.session_state:
    loaded = load_state()
    st.session_state.state_loaded = True
    if loaded:
        # Si se cargaron datos, no hacemos nada más
        pass

# Botón de reinicio
st.markdown('<div class="reset-button">', unsafe_allow_html=True)
if st.button("🗑️ Reiniciar Todo"):
    reset_state()
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Menú desplegable para elegir entre Claude y ChatGPT (centrado arriba)
st.markdown(
    '''
    <div class="ia-menu">
        <div class="ia-button"></div>
        <div class="ia-dropdown">
            <a href="https://claude.ai" target="_blank">Claude AI</a>
            <a href="https://chatgpt.com" target="_blank">ChatGPT</a>
        </div>
    </div>
    ''',
    unsafe_allow_html=True
)
# Header con Logo, Ruleta y Reloj
st.markdown('<div class="header-section">', unsafe_allow_html=True)

# Logo centrado grande (opción para cambiarlo)
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.markdown('<div class="upload-container upload-logo">', unsafe_allow_html=True)
logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="logo")
st.markdown('</div>', unsafe_allow_html=True)

# Mostrar logo actual o el predeterminado
if logo_file:
    st.image(logo_file, width=745)
else:
    # Logo predeterminado (usar la URL de la imagen del Grafiquito)
    st.image("https://github.com/Ing-Jose-Chamache/imagenesjch/blob/main/GRAFIQUITO.jpg?raw=true", width=745)

st.markdown('</div>', unsafe_allow_html=True)

# Obtener la hora actual en Perú
peru_timezone = pytz.timezone('America/Lima')
peru_time = datetime.now(peru_timezone)
current_time = peru_time.strftime("%H:%M:%S")
current_date = peru_time.strftime("%d/%m/%Y")

# Reloj de Perú con valores estáticos reales
st.markdown(
    f"""
    <div class="peru-clock">
        <div class="clock-title">Hora - Perú</div>
        <div class="clock-time">{current_time}</div>
        <div class="clock-date">{current_date}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Enlace a la ruleta (icono en la derecha, modificado posición)
st.markdown(
    f'<div class="ruleta-link">'
    f'<a href="https://miruletajychch.streamlit.app/" target="_blank">'
    f'<img src="https://github.com/Ing-Jose-Chamache/imagenesjch/blob/main/ruleta-logo.png?raw=true" width="182" height="220">'
    f'</a>'
    f'</div>',
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)

# Configuración inicial
col1, col2, _ = st.columns([2, 1, 1])
with col1:
    nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE")
with col2:
    num_preguntas = st.text_input("NÚMERO DE PREGUNTAS", value=str(st.session_state.num_preguntas), key="num_preguntas_input")
    try:
        st.session_state.num_preguntas = int(num_preguntas)
        save_state()
    except ValueError:
        st.error("Por favor ingrese un número válido")
      # Botón para agregar estudiante
if st.button("AGREGAR ESTUDIANTE") and nuevo_estudiante:
    if nuevo_estudiante not in st.session_state.estudiantes['Nombre'].values:
        nuevo_df = pd.DataFrame({
            'Nombre': [nuevo_estudiante],
            'Respuestas': ['0' * st.session_state.num_preguntas],
            'Respuestas_Correctas': [0]
        })
        st.session_state.estudiantes = pd.concat([st.session_state.estudiantes, nuevo_df], ignore_index=True)
        save_state()

# Cargar estudiantes desde archivo
st.markdown('<div class="upload-container upload-students">', unsafe_allow_html=True)
students_file = st.file_uploader("", type=['txt'], key="students")
st.markdown('</div>', unsafe_allow_html=True)

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
        save_state()
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
            save_state()
            st.rerun()
    with col2:
        st.markdown(f"<div class='question-number'>Pregunta {st.session_state.pregunta_actual + 1}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='question-text'>{st.session_state.preguntas[st.session_state.pregunta_actual]}</div>", unsafe_allow_html=True)
    with col3:
        if st.button("→") and st.session_state.pregunta_actual < len(st.session_state.preguntas) - 1:
            st.session_state.pregunta_actual += 1
            save_state()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Botón de AnyDesk (reubicado debajo de la sección de preguntas)
    st.markdown("""
        <div class="anydesk-button">
            <a href="anydesk:" target="_blank" class="anydesk-link">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 10px;">
                    <path d="M15 3h6v6M14 10l6.1-6.1M9 21H3v-6M10 14l-6.1 6.1"/>
                </svg>
                SOPORTE ESTUDIANTE VÍA ANYDESK
            </a>
        </div>
    """, unsafe_allow_html=True)

# Cargar preguntas
st.markdown('<div class="upload-container upload-questions">', unsafe_allow_html=True)
questions_file = st.file_uploader("", type=['txt'], key="questions")
st.markdown('</div>', unsafe_allow_html=True)

if questions_file:
    contenido = StringIO(questions_file.getvalue().decode("utf-8")).read().splitlines()
    st.session_state.preguntas = [linea.strip() for linea in contenido if linea.strip()]
    save_state()
    st.success(f"Se cargaron {len(st.session_state.preguntas)} preguntas")
    
# Mostrar estudiantes
for idx, estudiante in st.session_state.estudiantes.iterrows():
    st.markdown("<div class='student-row'>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([2, 6, 1, 1])
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
                save_state()
                st.rerun()
    with col3:
        nota = (sum(1 for r in estudiante['Respuestas'] if r == '1') / st.session_state.num_preguntas) * 20
        nota = round(nota, 1)
        if nota >= 14:
            color = '#28a745'  # Verde
        elif nota >= 11:
            color = '#ffc107'  # Amarillo
        else:
            color = '#dc3545'  # Rojo
        st.markdown(f"<span style='color:{color};font-weight:bold;font-size:1.1em'>{nota}</span>", unsafe_allow_html=True)
    with col4:
        if st.button("🗑️", key=f"delete_{estudiante['Nombre']}"):
            # Eliminar el estudiante del DataFrame
            st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)
            # Guardar el estado actualizado
            save_state()
            # Recargar la página para reflejar los cambios
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Separador decorativo entre estudiantes
    st.markdown("""
        <div class="student-separator">
            <div class="separator-dots">• • •</div>
            <div class="separator-line"></div>
        </div>
    """, unsafe_allow_html=True)
  # Estadísticas
if not st.session_state.estudiantes.empty:
    st.markdown("### Estadísticas de Participación")
    
    # Preparar datos para estadísticas
    df_stats = pd.DataFrame({
        'Nombre': st.session_state.estudiantes['Nombre'],
        'Respuestas_Correctas': st.session_state.estudiantes['Respuestas'].apply(lambda x: sum(1 for r in x if r == '1')),
        'Porcentaje': st.session_state.estudiantes['Respuestas'].apply(lambda x: sum(1 for r in x if r == '1') / st.session_state.num_preguntas * 100)
    })
    
    # Genera datos resumen para métricas adicionales en el CSV
    promedio_clase = df_stats['Respuestas_Correctas'].mean() * 20 / st.session_state.num_preguntas
    
    # Preparamos todos los datos para facilitar exportación
    df_stats['Nota_Vigesimal'] = df_stats['Respuestas_Correctas'].apply(
        lambda x: round((x / st.session_state.num_preguntas) * 20, 1)
    )
    
    df_stats['Estado'] = df_stats['Nota_Vigesimal'].apply(
        lambda nota: "APROBADO" if nota >= 14 else ("REGULAR" if nota >= 11 else "DESAPROBADO")
    )
    
    # Botón de descarga más visible
    download_button_html = download_csv(df_stats)
    st.markdown(f'<div style="text-align: center; margin: 15px 0;">{download_button_html}</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([3, 3, 3, 3])
    
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
        st.markdown("<div class='performance-stats'>", unsafe_allow_html=True)
        st.markdown("<div class='stats-title'>Análisis de Rendimiento</div>", unsafe_allow_html=True)
        
        # Mejor estudiante
        mejor_estudiante = df_stats.loc[df_stats['Porcentaje'].idxmax()]
        st.markdown("<div class='stats-highlight'>", unsafe_allow_html=True)
        st.markdown(f"🏆 **Mejor estudiante**: **{mejor_estudiante['Nombre']}** ({mejor_estudiante['Porcentaje']:.1f}%)")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Clasificación por niveles
        st.markdown('<div class="stats-subtitle">Niveles de Rendimiento:</div>', unsafe_allow_html=True)
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

    with col4:
        st.markdown("<div class='performance-stats'>", unsafe_allow_html=True)
        st.markdown("<div class='stats-title'>Notas Vigesimales (0-20)</div>", unsafe_allow_html=True)
        
        # Notas por estudiante
        st.markdown("<div class='stats-subtitle'>Calificaciones:</div>", unsafe_allow_html=True)
        
        # Calcular y mostrar notas
        for _, estudiante in df_stats.iterrows():
            nota = (estudiante['Respuestas_Correctas'] / st.session_state.num_preguntas) * 20
            nota = round(nota, 1)
            
            # Determinar color según la nota
            if nota >= 14:
                color = '#28a745'  # Verde (Aprobado)
                estado = "✓ APROBADO"
            elif nota >= 11:
                color = '#ffc107'  # Amarillo (Regular)
                estado = "⚠ REGULAR"
            else:
                color = '#dc3545'  # Rojo (Desaprobado)
                estado = "✗ DESAPROBADO"
            
            # Mostrar cada nota con formato
            st.markdown(f"""
                <div style='
                    background-color: #f8f9fa;
                    padding: 8px;
                    border-radius: 5px;
                    margin: 5px 0;
                    border-left: 4px solid {color};
                '>
                    <strong>{estudiante['Nombre']}</strong><br/>
                    Nota: <span style='color:{color};font-size:1.1em;font-weight:bold'>{nota}</span><br/>
                    <span style='color:{color};font-size:0.9em'>{estado}</span>
                </div>
            """, unsafe_allow_html=True)
        
        # Mostrar promedio del aula
        promedio = df_stats['Respuestas_Correctas'].mean() * 20 / st.session_state.num_preguntas
        st.markdown("<div class='stats-highlight' style='margin-top:15px'>", unsafe_allow_html=True)
        st.markdown(f"📊 **Promedio del aula**: {promedio:.1f}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Créditos
st.markdown("""
    <div class="credits">
        <h2>Créditos</h2>
        <div class="credits-divider"></div>
        <div class="credits-info">
            <strong>Desarrollador:</strong> Ing. José Yván Chamache Chiong<br>
            <strong>Lenguaje:</strong> Python<br>
            <strong>Ciudad:</strong> Lima, 25 Agosto 2025<br>
            <strong>Escuela:</strong> Instructor de la Escuela Profesional de Artes Gráficas
        </div>
        <div class="credits-divider"></div>
    </div>
""", unsafe_allow_html=True)

# Crear un .gitignore para evitar subir datos de sesiones
if not os.path.exists('.gitignore'):
    try:
        with open('.gitignore', 'w') as f:
            f.write("sesiones/\n.streamlit/\n")
    except:
        pass  # JYCHCH - Ignorar errores al crear el .gitignore
