import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import StringIO

# Configuración de la página
st.set_page_config(page_title="CONTROL DE PARTICIPACIÓN", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .title {
        text-transform: uppercase;
        text-align: center;
        font-weight: bold;
        font-size: 2.5em;
    }
    .logo-upload {
        width: 100px !important;
        position: fixed;
        top: 10px;
        left: 10px;
    }
    .question-completed {
        text-decoration: line-through;
        font-weight: bold;
        color: #6c757d;
    }
    </style>
""", unsafe_allow_html=True)

class ControlParticipacion:
    def __init__(self):
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Participaciones', 'Puntaje'])
        if 'participaciones_esperadas' not in st.session_state:
            st.session_state.participaciones_esperadas = 10
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []
        if 'preguntas_completadas' not in st.session_state:
            st.session_state.preguntas_completadas = set()
        if 'logo' not in st.session_state:
            st.session_state.logo = None

    def cargar_logo(self):
        st.markdown('<div class="logo-upload">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="logo_upload")
        st.markdown('</div>', unsafe_allow_html=True)
        if uploaded_file:
            st.session_state.logo = base64.b64encode(uploaded_file.getvalue()).decode()

    def mostrar_header(self):
        if st.session_state.logo:
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 1rem;">
                    <img src="data:image/png;base64,{st.session_state.logo}" width="300"/>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("<h1 class='title'>CONTROL DE PARTICIPACIÓN</h1>", unsafe_allow_html=True)

    def actualizar_puntaje(self, idx):
        participaciones = st.session_state.estudiantes.at[idx, 'Participaciones']
        st.session_state.estudiantes.at[idx, 'Puntaje'] = min(
            20, (participaciones / st.session_state.participaciones_esperadas) * 20
        )

    def mostrar_estudiantes(self):
        # Control de participaciones esperadas
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### GESTIÓN DE ESTUDIANTES")
        with col2:
            nuevo_valor = st.number_input("PARTICIPACIONES ESPERADAS", 
                                        min_value=1, 
                                        value=st.session_state.participaciones_esperadas)
            if nuevo_valor != st.session_state.participaciones_esperadas:
                st.session_state.participaciones_esperadas = nuevo_valor
                for idx in st.session_state.estudiantes.index:
                    self.actualizar_puntaje(idx)

        # Agregar nuevo estudiante
        col1, col2 = st.columns([3, 1])
        with col1:
            nombre = st.text_input("NOMBRE DEL ESTUDIANTE")
        with col2:
            if st.button("AGREGAR") and nombre:
                if nombre not in st.session_state.estudiantes['Nombre'].values:
                    st.session_state.estudiantes = pd.concat([
                        st.session_state.estudiantes,
                        pd.DataFrame({
                            'Nombre': [nombre],
                            'Participaciones': [0],
                            'Puntaje': [0]
                        })
                    ], ignore_index=True)

        # Lista de estudiantes
        for idx, estudiante in st.session_state.estudiantes.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            with col1:
                st.write(f"**{estudiante['Nombre']}**")
            with col2:
                st.write(f"Participaciones: {estudiante['Participaciones']}/{st.session_state.participaciones_esperadas} | Nota: {estudiante['Puntaje']:.1f}")
            with col3:
                if st.button("+1", key=f"plus_{idx}"):
                    st.session_state.estudiantes.at[idx, 'Participaciones'] += 1
                    self.actualizar_puntaje(idx)
                    st.rerun()
            with col4:
                if st.button("-1", key=f"minus_{idx}"):
                    if st.session_state.estudiantes.at[idx, 'Participaciones'] > 0:
                        st.session_state.estudiantes.at[idx, 'Participaciones'] -= 1
                        self.actualizar_puntaje(idx)
                        st.rerun()
            with col5:
                if st.button("❌", key=f"delete_{idx}"):
                    st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)
                    st.rerun()

        # Botón para eliminar todos
        if not st.session_state.estudiantes.empty:
            if st.button("ELIMINAR TODOS LOS ESTUDIANTES"):
                st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Participaciones', 'Puntaje'])
                st.rerun()

    def mostrar_graficos(self):
        if not st.session_state.estudiantes.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig_bar = px.bar(
                    st.session_state.estudiantes,
                    x='Nombre',
                    y='Participaciones',
                    title='PARTICIPACIONES POR ESTUDIANTE'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                total = st.session_state.estudiantes['Participaciones'].sum()
                if total > 0:
                    datos_torta = st.session_state.estudiantes.copy()
                    datos_torta['Porcentaje'] = (datos_torta['Participaciones'] / total * 100)
                    fig_pie = px.pie(
                        datos_torta,
                        values='Porcentaje',
                        names='Nombre',
                        title='DISTRIBUCIÓN DE PARTICIPACIONES (%)'
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

    def gestionar_preguntas(self):
        st.markdown("### PREGUNTAS PLANIFICADAS")
        
        # Agregar pregunta
        nueva_pregunta = st.text_input("ESCRIBA UNA NUEVA PREGUNTA")
        if st.button("AGREGAR PREGUNTA") and nueva_pregunta:
            st.session_state.preguntas.append(nueva_pregunta)
            st.rerun()

        # Mostrar preguntas
        for i, pregunta in enumerate(st.session_state.preguntas):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if i in st.session_state.preguntas_completadas:
                    st.markdown(f"<p class='question-completed'>{i+1}. {pregunta}</p>", unsafe_allow_html=True)
                else:
                    st.write(f"{i+1}. {pregunta}")
            with col2:
                if st.button("✓" if i not in st.session_state.preguntas_completadas else "↩", key=f"complete_{i}"):
                    if i in st.session_state.preguntas_completadas:
                        st.session_state.preguntas_completadas.remove(i)
                    else:
                        st.session_state.preguntas_completadas.add(i)
                    st.rerun()
            with col3:
                if st.button("❌", key=f"delete_pregunta_{i}"):
                    st.session_state.preguntas.pop(i)
                    st.session_state.preguntas_completadas = {
                        x if x < i else x - 1 for x in st.session_state.preguntas_completadas if x != i
                    }
                    st.rerun()

        # Eliminar todas las preguntas
        if st.session_state.preguntas:
            if st.button("ELIMINAR TODAS LAS PREGUNTAS"):
                st.session_state.preguntas = []
                st.session_state.preguntas_completadas = set()
                st.rerun()

    def run(self):
        self.cargar_logo()
        self.mostrar_header()
        self.mostrar_estudiantes()
        self.mostrar_graficos()
        st.markdown("---")
        self.gestionar_preguntas()
        st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <h3>Desarrollado por:</h3>
                <p><strong>Ing. José Yván Chamache Chiong</strong></p>
                <p>Lima, Perú - 2024</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    app = ControlParticipacion()
    app.run()
