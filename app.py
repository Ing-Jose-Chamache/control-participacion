import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
from io import StringIO

# Configuración de la página
st.set_page_config(page_title="CONTROL DE PARTICIPACIÓN", layout="wide")

# Aplicar estilo personalizado con diseño visual mejorado
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .logo-upload {
        position: absolute;
        top: 10px;
        left: 10px;
        width: 50px;
        height: 50px;
        opacity: 0.7;
    }
    .logo-container img {
        width: 396px;
        margin-top: -20px;
    }
    .title {
        text-transform: uppercase;
        text-align: center;
        font-weight: bold;
        font-size: 3em;
        color: #4CAF50;
        text-shadow: 2px 2px 4px #000000;
    }
    .student-row, .question-box {
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        padding: 15px;
        margin-bottom: 10px;
    }
    .question-completed {
        text-decoration: line-through;
        color: red;
    }
    .stats-container {
        display: flex;
        justify-content: space-around;
        gap: 20px;
        margin-bottom: 20px;
    }
    .stat-box {
        padding: 15px;
        border-radius: 12px;
        background-color: #F4F6F7;
        text-align: center;
        width: 100%;
        font-size: 1.2em;
    }
    .background {
        background: url('https://www.transparenttextures.com/patterns/diamond-upholstery.png');
    }
    .credits {
        text-align: center;
        padding: 20px;
        background-color: #e8f5e9;
        border-radius: 10px;
        margin-top: 30px;
        font-family: 'Arial', sans-serif;
    }
    .credits h3 {
        font-size: 1.8em;
        font-weight: bold;
    }
    .credits p {
        font-size: 1.1em;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Restauración completa del código original con las mejoras aplicadas

class ControlParticipacion:
    def __init__(self):
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Puntaje']
            )
        if 'participaciones_esperadas' not in st.session_state:
            st.session_state.participaciones_esperadas = 10
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = [f"Pregunta {i+1}" for i in range(5)]
        if 'preguntas_completadas' not in st.session_state:
            st.session_state.preguntas_completadas = set()
        if 'logo' not in st.session_state:
            st.session_state.logo = None

    def cargar_logo(self):
        logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
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

    def agregar_estudiante(self):
        nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE")
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

    def mostrar_estudiantes(self):
        if not st.session_state.estudiantes.empty:
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.markdown("### GESTIÓN DE ESTUDIANTES")
            st.session_state.participaciones_esperadas = col2.number_input(
                "PARTICIPACIONES ESPERADAS", min_value=1,
                value=st.session_state.participaciones_esperadas
            )
            if col3.button("LIMPIAR LISTA DE ESTUDIANTES"):
                st.session_state.estudiantes = pd.DataFrame(
                    columns=['Nombre', 'Participaciones', 'Puntaje']
                )
                st.success("Lista de estudiantes limpiada exitosamente")

            for _, estudiante in st.session_state.estudiantes.iterrows():
                cols = st.columns([3, 2, 2, 1, 1, 1])
                cols[0].write(f"**{estudiante['Nombre']}**")
                cols[1].write(f"Participaciones: {estudiante['Participaciones']}/{st.session_state.participaciones_esperadas}")
                cols[2].write(f"Nota: {estudiante['Puntaje']:.1f}")
                if cols[3].button("+1", key=f"plus_{estudiante['Nombre']}"):
                    idx = st.session_state.estudiantes[st.session_state.estudiantes['Nombre'] == estudiante['Nombre']].index[0]
                    st.session_state.estudiantes.at[idx, 'Participaciones'] += 1
                    st.session_state.estudiantes.at[idx, 'Puntaje'] = min(
                        20, (st.session_state.estudiantes.at[idx, 'Participaciones'] / 
                        st.session_state.participaciones_esperadas) * 20
                    )

                if cols[4].button("-1", key=f"minus_{estudiante['Nombre']}"):
                    idx = st.session_state.estudiantes[st.session_state.estudiantes['Nombre'] == estudiante['Nombre']].index[0]
                    if st.session_state.estudiantes.at[idx, 'Participaciones'] > 0:
                        st.session_state.estudiantes.at[idx, 'Participaciones'] -= 1
                        st.session_state.estudiantes.at[idx, 'Puntaje'] = min(
                            20, (st.session_state.estudiantes.at[idx, 'Participaciones'] / 
                            st.session_state.participaciones_esperadas) * 20
                        )

    def mostrar_creditos(self):
        st.markdown("""
        <div class="credits">
            <h3>Desarrollado por:</h3>
            <p><strong>Ing. José Yván Chamache Chiong</strong></p>
            <p>Lima, Perú - 2024</p>
        </div>
        """, unsafe_allow_html=True)

    def run(self):
        self.cargar_logo()
        self.mostrar_header()
        self.agregar_estudiante()
        self.mostrar_estudiantes()
        self.mostrar_creditos()

# Iniciar la aplicación
if __name__ == "__main__":
    app = ControlParticipacion()
    app.run()
