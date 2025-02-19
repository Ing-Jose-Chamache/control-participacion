import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json

# Configuración de la página
st.set_page_config(page_title="Control de Participación", layout="wide")

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
    </style>
""", unsafe_allow_html=True)

class ControlParticipacion:
    def __init__(self):
        # Inicializar estados de sesión
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Puntaje']
            )
        
        if 'participaciones_esperadas' not in st.session_state:
            st.session_state.participaciones_esperadas = 10
            
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []

    def mostrar_header(self):
        st.title("Control de Participación")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### Gestión de Estudiantes")
        with col2:
            st.session_state.participaciones_esperadas = st.number_input(
                "Participaciones esperadas",
                min_value=1,
                value=st.session_state.participaciones_esperadas
            )

    def agregar_estudiante(self):
        col1, col2 = st.columns([3, 1])
        with col1:
            nuevo_estudiante = st.text_input("Nombre del estudiante")
        with col2:
            if st.button("Agregar"):
                if nuevo_estudiante:
                    if nuevo_estudiante not in st.session_state.estudiantes['Nombre'].values:
                        nuevo_df = pd.DataFrame({
                            'Nombre': [nuevo_estudiante],
                            'Participaciones': [0],
                            'Puntaje': [0]
                        })
                        st.session_state.estudiantes = pd.concat([st.session_state.estudiantes, nuevo_df], ignore_index=True)
                        st.success(f"Estudiante {nuevo_estudiante} agregado con éxito")
                    else:
                        st.error("Este estudiante ya existe")

    def mostrar_estudiantes(self):
        for _, estudiante in st.session_state.estudiantes.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            with col1:
                st.write(estudiante['Nombre'])
            with col2:
                st.write(f"{estudiante['Participaciones']}/{st.session_state.participaciones_esperadas}")
            with col3:
                st.write(f"Nota: {estudiante['Puntaje']}")
            with col4:
                if st.button("+1", key=f"plus_{estudiante['Nombre']}"):
                    idx = st.session_state.estudiantes[st.session_state.estudiantes['Nombre'] == estudiante['Nombre']].index[0]
                    st.session_state.estudiantes.loc[idx, 'Participaciones'] += 1
                    st.session_state.estudiantes.loc[idx, 'Puntaje'] = min(
                        20,
                        (st.session_state.estudiantes.loc[idx, 'Participaciones'] / 
                         st.session_state.participaciones_esperadas) * 20
                    )
            with col5:
                if st.button("-1", key=f"minus_{estudiante['Nombre']}"):
                    idx = st.session_state.estudiantes[st.session_state.estudiantes['Nombre'] == estudiante['Nombre']].index[0]
                    if st.session_state.estudiantes.loc[idx, 'Participaciones'] > 0:
                        st.session_state.estudiantes.loc[idx, 'Participaciones'] -= 1
                        st.session_state.estudiantes.loc[idx, 'Puntaje'] = min(
                            20,
                            (st.session_state.estudiantes.loc[idx, 'Participaciones'] / 
                             st.session_state.participaciones_esperadas) * 20
                        )

    def mostrar_graficos(self):
        if not st.session_state.estudiantes.empty:
            fig = px.bar(
                st.session_state.estudiantes,
                x='Nombre',
                y='Participaciones',
                title='Participaciones por Estudiante'
            )
            st.plotly_chart(fig, use_container_width=True)

    def gestionar_preguntas(self):
        st.markdown("### Preguntas Planificadas")
        nueva_pregunta = st.text_input("Escriba una nueva pregunta...")
        if st.button("Agregar Pregunta"):
            if nueva_pregunta:
                st.session_state.preguntas.append(nueva_pregunta)

        if st.session_state.preguntas:
            for i, pregunta in enumerate(st.session_state.preguntas, 1):
                st.write(f"{i}. {pregunta}")

        if st.button("Limpiar Preguntas"):
            st.session_state.preguntas = []

    def run(self):
        self.mostrar_header()
        self.agregar_estudiante()
        st.markdown("---")
        self.mostrar_estudiantes()
        self.mostrar_graficos()
        st.markdown("---")
        self.gestionar_preguntas()

# Iniciar la aplicación
if __name__ == "__main__":
    app = ControlParticipacion()
    app.run()
