import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
from io import StringIO

# Configuración de la página
st.set_page_config(page_title="CONTROL DE PARTICIPACIÓN", layout="wide")

# Aplicar estilo personalizado
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .stTextInput>div>div>input {
        padding: 0.5rem;
    }
    .title {
        text-transform: uppercase;
        text-align: center;
        font-weight: bold;
        font-size: 2.5em;
    }
    .logo-upload {
        position: absolute;
        top: 10px;
        left: 10px;
        width: 80px;
        z-index: 100;
    }
    .logo-upload .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        cursor: pointer;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    .logo-upload .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
        transition: all 0.3s ease;
    }
    .logo-container {
        text-align: center;
        margin: 20px auto;
        max-width: 600px;
    }
    .logo-container img {
        width: 100%;
        height: auto;
        max-width: 500px;
        margin: 0 auto;
        display: block;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Resto de los estilos permanecen igual */
    </style>
""", unsafe_allow_html=True)

class ControlParticipacion:
    def __init__(self):
        # El resto del código del init permanece igual
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Puntaje']
            )
        if 'participaciones_esperadas' not in st.session_state:
            st.session_state.participaciones_esperadas = 10
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []
        if 'preguntas_completadas' not in st.session_state:
            st.session_state.preguntas_completadas = set()
        if 'logo' not in st.session_state:
            st.session_state.logo = None

    def cargar_logo(self):
        with st.container():
            st.markdown('<div class="logo-upload">', unsafe_allow_html=True)
            st.markdown("""
                <style>
                    [data-testid="stFileUploadDropzone"] {
                        width: 40px !important;
                        height: 40px !important;
                        border-radius: 50% !important;
                        background-color: #4CAF50 !important;
                        border: none !important;
                        color: white !important;
                    }
                    [data-testid="stFileUploadDropzone"] div {
                        display: none;
                    }
                    [data-testid="stFileUploadDropzone"]::before {
                        content: "📷";
                        font-size: 20px;
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                    }
                </style>
            """, unsafe_allow_html=True)
            logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'])
            st.markdown('</div>', unsafe_allow_html=True)
            if logo_file is not None:
                st.session_state.logo = base64.b64encode(logo_file.read()).decode()

    def mostrar_header(self):
        if st.session_state.logo:
            st.markdown(f"""
                <div class="logo-container">
                    <img src="data:image/png;base64,{st.session_state.logo}"/>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<h1 class='title'>CONTROL DE PARTICIPACIÓN</h1>", unsafe_allow_html=True)

    # El resto de los métodos permanecen igual
