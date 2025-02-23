import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
from io import StringIO
import time

# Configuración de la página
st.set_page_config(page_title="CONTROL DE PARTICIPACIÓN", layout="wide")

# Aplicar estilo personalizado
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button { width: 100%; }
    .stTextInput>div>div>input { padding: 0.5rem; }
    div[data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"],
    div[data-testid="stFileUploader"] p,
    div[data-testid="stFileUploader"] span[data-testid="stMarkdownContainer"] {
        display: none !important;
    }
    div[data-testid="stFileUploader"] section {
        min-height: unset !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    div[data-testid="stFileUploader"] button {
        font-size: 9.5px !important;
        padding: 2px 8px !important;
    }
    div[data-testid="stFileUploader"] > div:first-child {
        margin: 0 !important;
        padding: 0 !important;
    }
    .uploadedFile { width: 15%; }
    .stFileUploader > section { width: 15%; padding: 1px; }
    .stFileUploader > div > div { width: 15%; padding: 1px; }
    .title {
        text-transform: uppercase;
        text-align: center;
        font-weight: bold;
        font-size: 2.5em;
    }
    .logo-upload {
        position: absolute;
        top: 2px;
        left: 2px;
        width: 15%;
        height: 15%;
        z-index: 100;
    }
    .logo-container {
        text-align: left;
        margin: 2px 0 20px 2px;
        max-width: 200px;
    }
    .student-section { font-size: 1.1em; }
    .question-box {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .question-completed {
        text-decoration: line-through;
        color: #6c757d;
    }
    .icon-container {
        display: inline-flex;
        gap: 5px;
        align-items: center;
    }
    .stButton button { padding: 0 10px; }
    .stButton button:contains("⬤") {
        color: #000000 !important;
        background-color: transparent !important;
        border: none !important;
        transition: color 0.3s ease;
        padding: 0 5px;
        font-size: 24px;
    }
    .stButton button[data-testid="secondary"]:contains("⬤") {
        color: #FFD700 !important;
    }
    .stButton button:contains("🗑️") {
        color: #ff4b4b !important;
        background-color: transparent !important;
        border: 1px solid #ff4b4b !important;
        border-radius: 4px;
    }
    .stButton button:contains("ELIMINAR TODOS") {
        background-color: #ff4b4b !important;
        color: white !important;
        margin-top: 20px;
    }
    .stButton button:contains("REINICIAR PUNTOS") {
        background-color: #1e88e5 !important;
        color: white !important;
    }
    .student-row {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #dee2e6;
        display: flex;
        align-items: center;
    }
    .student-controls { display: flex; gap: 10px; }
    .credits {
        text-align: center;
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-top: 30px;
    }
    .pregunta-card {
        background-color: #ffffff;
        border: 2px solid #e1e4e8;
        border-radius: 12px;
        padding: 30px;
        margin: 20px auto;
        max-width: 900px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        position: relative;
    }
    .pregunta-numero {
        position: absolute;
        top: 15px;
        right: 20px;
        color: #4a90e2;
        font-weight: 500;
        font-size: 1.1em;
    }
    .pregunta-texto {
        font-size: 1.4em;
        line-height: 1.6;
        color: #2e86de;
        padding: 15px 0;
        text-align: center;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

class ControlParticipacion:
    def __init__(self):
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Puntaje']
            )
        if 'participaciones_esperadas' not in st.session_state:
            st.session_state.participaciones_esperadas = 5
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []
        if 'pregunta_actual' not in st.session_state:
            st.session_state.pregunta_actual = 0
        if 'iconos_estado' not in st.session_state:
            st.session_state.iconos_estado = {}
        if 'logo' not in st.session_state:
            st.session_state.logo = None

    def cargar_logo(self):
        with st.container():
            with st.sidebar:
                logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="logo_uploader")
                if logo_file is not None:
                    st.session_state.logo = base64.b64encode(logo_file.read()).decode()

    def mostrar_header(self):
        if st.session_state.logo:
            st.markdown(f"""
                <div style="text-align: center; margin: 20px 0;">
                    <img src="data:image/png;base64,{st.session_state.logo}" 
                    style="max-width: 400px; margin-bottom: 15px;"/>
                </div>
            """, unsafe_allow_html=True)

    def cargar_archivo_txt(self, tipo):
        archivo = st.file_uploader(f"SUBE DATA AMIGO ({tipo})", type=['txt'], 
                                 key=f"uploader_{tipo}")
        if archivo is not None:
            try:
                contenido = StringIO(archivo.getvalue().decode("utf-8")).read().splitlines()
                contenido = [linea.strip() for linea in contenido if linea.strip()]
                
                if tipo == "estudiantes":
                    for estudiante in contenido:
                        if estudiante not in st.session_state.estudiantes['Nombre'].values:
                            nuevo_df = pd.DataFrame({
                                'Nombre': [estudiante],
                                'Participaciones': [0],
                                'Puntaje': [0]
                            })
                            st.session_state.estudiantes = pd.concat(
                                [st.session_state.estudiantes, nuevo_df],
                                ignore_index=True
                            )
                    st.success("Estudiantes cargados exitosamente")
            except Exception as e:
                st.error(f"Error al cargar el archivo: {str(e)}")

    def eliminar_estudiante(self, nombre):
        try:
            if nombre in st.session_state.iconos_estado:
                del st.session_state.iconos_estado[nombre]
            st.session_state.estudiantes = st.session_state.estudiantes[
                st.session_state.estudiantes['Nombre'] != nombre
            ].reset_index(drop=True)
            return True
        except Exception as e:
            st.error(f"Error al eliminar estudiante: {str(e)}")
            return False

    def limpiar_lista_estudiantes(self):
        try:
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Puntaje']
            )
            st.session_state.iconos_estado = {}
            return True
        except Exception as e:
            st.error(f"Error al limpiar lista: {str(e)}")
            return False

    def eliminar_pregunta(self, index):
        if 0 <= index < len(st.session_state.preguntas):
            del st.session_state.preguntas[index]
            return True
        return False

    def limpiar_preguntas(self):
        st.session_state.preguntas = []
        return True

    def mostrar_preguntas(self):
        # Agregar preguntas manualmente
        col1, col2 = st.columns([3, 1])
        with col1:
            nueva_pregunta = st.text_input("INGRESE NUEVA PREGUNTA:", key="input_pregunta")
        with col2:
            if st.button("AGREGAR PREGUNTA", key="btn_agregar_pregunta"):
                if nueva_pregunta.strip():
                    st.session_state.preguntas.append(nueva_pregunta.strip())
                    st.success("¡Pregunta agregada exitosamente!")
                    st.session_state.input_pregunta = ""
                    st.rerun()
                else:
                    st.error("Por favor, ingrese una pregunta válida")

        if st.session_state.preguntas:
            col1, col2, col3 = st.columns([1, 6, 1])
            
            with col1:
                if st.button("⬅️", key="prev_question", 
                           disabled=st.session_state.pregunta_actual == 0):
                    st.session_state.pregunta_actual = max(0, st.session_state.pregunta_actual - 1)
                    st.rerun()
            
            with col2:
                total_preguntas = len(st.session_state.preguntas)
                st.markdown(f"""
                    <div class="pregunta-card">
                        <div class="pregunta-numero">{st.session_state.pregunta_actual + 1}/{total_preguntas}</div>
                        <div class="pregunta-texto">{st.session_state.preguntas[st.session_state.pregunta_actual]}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_del, col_clear = st.columns(2)
                with col_del:
                    if st.button("🗑️ Eliminar Pregunta", key="del_current", type="secondary"):
                        if self.eliminar_pregunta(st.session_state.pregunta_actual):
                            if st.session_state.pregunta_actual >= len(st.session_state.preguntas):
                                st.session_state.pregunta_actual = max(0, len(st.session_state.preguntas) - 1)
                            st.success("Pregunta eliminada")
                            st.rerun()
                
                with col_clear:
                    if st.button("🗑️ Eliminar Todas", key="clear_questions", type="secondary"):
                        if self.limpiar_preguntas():
                            st.session_state.pregunta_actual = 0
                            st.success("Todas las preguntas eliminadas")
                            st.rerun()
            
            with col3:
                if st.button("➡️", key="next_question", 
                           disabled=st.session_state.pregunta_actual >= total_preguntas - 1):
                    st.session_state.pregunta_actual = min(total_preguntas - 1, 
                                                         st.session_state.pregunta_actual + 1)
                    st.rerun()

    def agregar_estudiante(self):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE")
        with col2:
            if st.button("AGREGAR ESTUDIANTE"):
                if nuevo_estudiante:
                    if nuevo_estudiante not in st.session_state.estudiantes['Nombre'].values:
                        nuevo_df = pd.DataFrame({
                            'Nombre': [nuevo_estudiante],
                            'Participaciones': [0],
                            'Puntaje': [0]
                        })
                        st.session_state.estudiantes = pd.concat(
                            [st.session_state.estudiantes, nuevo_df],
                            ignore_index=True
                        )
                        st.success(f"Estudiante {nuevo_estudiante} agregado con éxito")
                    else:
                        st.error("Este estudiante ya existe")
        with col3:
            self.cargar_archivo_txt("estudiantes")

    def mostrar_estudiantes(self):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown("### GESTIÓN DE ESTUDIANTES")
        with col2:
            st.session_state.participaciones_esperadas = int(st.text_input(
                "PARTICIPACIONES ESPERADAS",
                value=str(st.session_state.participaciones_esperadas),
                key="participaciones_input"
            ) or 5)
        with col3:
            if st.button("🔄 REINICIAR PUNTOS", type="secondary"):
                for nombre in st.session_state.iconos_estado:
                    st.session_state.iconos_estado[nombre] = [False] * st.session_state.participaciones_esperadas
                st.session_state.estudiantes['Participaciones'] = 0
                st.session_state.estudiantes['Puntaje'] = 0.0
                st.rerun()

        for _, estudiante in st.session_state.estudiantes.iterrows():
            nombre = estudiante['Nombre']
            
            if nombre not in st.session_state.iconos_estado:
                st.session_state.iconos_estado[nombre] = [False] * st.session_state.participaciones_esperadas
