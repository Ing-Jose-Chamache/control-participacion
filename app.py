import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import StringIO
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="CONTROL DE PARTICIPACIÓN", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .title {
        text-transform: uppercase;
        text-align: center;
        font-weight: bold;
        font-size: 2.5em;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 1rem;
    }
    .student-row {
        background-color: #ffffff;
        padding: 8px;
        border-radius: 5px;
        margin-bottom: 5px;
        border: 1px solid #dee2e6;
    }
    .question-box {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .question-completed {
        text-decoration: line-through;
        font-weight: bold;
        color: #6c757d;
        background-color: #e9ecef;
    }
    .control-buttons {
        display: flex;
        gap: 10px;
    }
    .credits {
        text-align: center;
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

class ControlParticipacion:
    def __init__(self):
        """Inicializa la aplicación y sus estados."""
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Participaciones', 'Puntaje'])
        if 'participaciones_esperadas' not in st.session_state:
            st.session_state.participaciones_esperadas = 5
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []
        if 'preguntas_completadas' not in st.session_state:
            st.session_state.preguntas_completadas = set()
        if 'logo' not in st.session_state:
            st.session_state.logo = None

    def cargar_logo(self):
        """Maneja la carga y visualización del logo."""
        col1, col2, col3 = st.columns([1, 10, 1])
        with col1:
            logo_file = st.file_uploader("", type=['jpg', 'bmp'], key='logo_upload')
            if logo_file:
                st.session_state.logo = base64.b64encode(logo_file.getvalue()).decode()
                st.experimental_rerun()

    def mostrar_header(self):
        """Muestra el encabezado y el logo si existe."""
        if st.session_state.logo:
            st.markdown(f"""
                <div class="logo-container">
                    <img src="data:image/jpeg;base64,{st.session_state.logo}" width="300"/>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("<h1 class='title'>CONTROL DE PARTICIPACIÓN</h1>", unsafe_allow_html=True)

    def actualizar_puntaje(self, idx, participaciones):
        """Actualiza el puntaje de un estudiante basado en sus participaciones."""
        puntaje = (participaciones / st.session_state.participaciones_esperadas) * 20
        st.session_state.estudiantes.at[idx, 'Participaciones'] = participaciones
        st.session_state.estudiantes.at[idx, 'Puntaje'] = puntaje

    def mostrar_estudiantes(self):
        """Gestiona la sección de estudiantes."""
        st.markdown("### GESTIÓN DE ESTUDIANTES")
        
        # Control de participaciones esperadas
        participaciones = st.number_input(
            "PARTICIPACIONES ESPERADAS",
            min_value=1,
            value=st.session_state.participaciones_esperadas
        )
        if participaciones != st.session_state.participaciones_esperadas:
            st.session_state.participaciones_esperadas = participaciones
            for idx in st.session_state.estudiantes.index:
                self.actualizar_puntaje(idx, st.session_state.estudiantes.at[idx, 'Participaciones'])
            st.experimental_rerun()

        # Agregar estudiante
        col1, col2 = st.columns([3, 1])
        with col1:
            nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE")
        with col2:
            if st.button("AGREGAR") and nuevo_estudiante:
                if nuevo_estudiante not in st.session_state.estudiantes['Nombre'].values:
                    nuevo_df = pd.DataFrame({
                        'Nombre': [nuevo_estudiante],
                        'Participaciones': [0],
                        'Puntaje': [0]
                    })
                    st.session_state.estudiantes = pd.concat([
                        st.session_state.estudiantes, nuevo_df
                    ], ignore_index=True)
                    st.experimental_rerun()

        # Lista de estudiantes
        for idx, row in st.session_state.estudiantes.iterrows():
            with st.container():
                cols = st.columns([2, 2, 1, 1, 1])
                with cols[0]:
                    st.write(f"**{row['Nombre']}**")
                with cols[1]:
                    st.write(f"{row['Participaciones']}/{participaciones} | {row['Puntaje']:.1f}")
                with cols[2]:
                    if st.button("+1", key=f"plus_{idx}"):
                        self.actualizar_puntaje(idx, row['Participaciones'] + 1)
                        st.experimental_rerun()
                with cols[3]:
                    if st.button("-1", key=f"minus_{idx}"):
                        if row['Participaciones'] > 0:
                            self.actualizar_puntaje(idx, row['Participaciones'] - 1)
                            st.experimental_rerun()
                with cols[4]:
                    if st.button("❌", key=f"del_{idx}"):
                        st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)
                        st.experimental_rerun()

        # Eliminar todos los estudiantes
        if not st.session_state.estudiantes.empty:
            if st.button("ELIMINAR TODOS LOS ESTUDIANTES", type="primary"):
                st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Participaciones', 'Puntaje'])
                st.experimental_rerun()

    def mostrar_graficos(self):
        """Muestra los gráficos de participación."""
        if not st.session_state.estudiantes.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig_bar = px.bar(
                    st.session_state.estudiantes,
                    x='Nombre',
                    y='Participaciones',
                    title='PARTICIPACIONES POR ESTUDIANTE',
                    color='Participaciones',
                    color_continuous_scale='Viridis'
                )
                fig_bar.update_layout(title_x=0.5)
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
                        title='DISTRIBUCIÓN DE PARTICIPACIONES (%)',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_pie.update_layout(title_x=0.5)
                    st.plotly_chart(fig_pie, use_container_width=True)

    def gestionar_preguntas(self):
        """Gestiona la sección de preguntas."""
        st.markdown("### PREGUNTAS PLANIFICADAS")
        
        # Agregar pregunta
        col1, col2 = st.columns([3, 1])
        with col1:
            nueva_pregunta = st.text_input("NUEVA PREGUNTA")
        with col2:
            if st.button("AGREGAR PREGUNTA") and nueva_pregunta:
                st.session_state.preguntas.append(nueva_pregunta)
                st.experimental_rerun()

        # Cargar preguntas desde archivo
        uploaded_file = st.file_uploader("CARGAR PREGUNTAS", type=['txt'])
        if uploaded_file:
            contenido = StringIO(uploaded_file.getvalue().decode("utf-8")).read().splitlines()
            st.session_state.preguntas.extend([p.strip() for p in contenido if p.strip()])
            st.experimental_rerun()

        # Lista de preguntas
        for i, pregunta in enumerate(st.session_state.preguntas):
            with st.container():
                cols = st.columns([3, 1, 1])
                with cols[0]:
                    if i in st.session_state.preguntas_completadas:
                        st.markdown(f"<p style='text-decoration: line-through; font-weight: bold;'>{i+1}. {pregunta}</p>", unsafe_allow_html=True)
                    else:
                        st.write(f"{i+1}. {pregunta}")
                with cols[1]:
                    if st.button("✓" if i not in st.session_state.preguntas_completadas else "↩", key=f"check_{i}"):
                        if i in st.session_state.preguntas_completadas:
                            st.session_state.preguntas_completadas.remove(i)
                        else:
                            st.session_state.preguntas_completadas.add(i)
                        st.experimental_rerun()
                with cols[2]:
                    if st.button("❌", key=f"del_preg_{i}"):
                        st.session_state.preguntas.pop(i)
                        st.session_state.preguntas_completadas = {
                            x if x < i else x - 1 for x in st.session_state.preguntas_completadas if x != i
                        }
                        st.experimental_rerun()

        # Eliminar todas las preguntas
        if st.session_state.preguntas:
            if st.button("ELIMINAR TODAS LAS PREGUNTAS", type="primary"):
                st.session_state.preguntas = []
                st.session_state.preguntas_completadas = set()
                st.experimental_rerun()

    def run(self):
        """Ejecuta la aplicación."""
        self.cargar_logo()
        self.mostrar_header()
        self.mostrar_estudiantes()
        self.mostrar_graficos()
        st.markdown("---")
        self.gestionar_preguntas()
        
        # Créditos
        st.markdown("""
            <div class="credits">
                <h3>Desarrollado por:</h3>
                <p><strong>Ing. José Yván Chamache Chiong</strong></p>
                <p>Lima, Perú - 2024</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    app = ControlParticipacion()
    app.run()
