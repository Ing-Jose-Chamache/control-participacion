import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import StringIO
from datetime import datetime
import time
import json

# Configuración inicial de la página
st.set_page_config(
    page_title="CONTROL DE PARTICIPACIÓN",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS detallados
st.markdown("""
    <style>
    /* Estilos generales */
    .main {
        padding: 2rem;
        background-color: #ffffff;
    }
    
    /* Estilos para el título principal */
    .title {
        text-transform: uppercase;
        text-align: center;
        font-weight: bold;
        font-size: 2.5em;
        margin-bottom: 2rem;
        color: #1f1f1f;
    }
    
    /* Contenedor del logo */
    .logo-container {
        position: relative;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Estilos para el uploader del logo */
    .upload-button {
        position: fixed;
        top: 10px;
        left: 10px;
        width: 50px !important;
        z-index: 1000;
    }
    
    /* Estilos para filas de estudiantes */
    .student-row {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    .student-row:hover {
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Estilos para las preguntas */
    .question-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    .question-box:hover {
        background-color: #f1f3f5;
    }
    
    /* Estilo para preguntas completadas */
    .question-completed {
        text-decoration: line-through;
        font-weight: bold;
        color: #6c757d;
        background-color: #e9ecef;
    }
    
    /* Estilos para botones */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Estilo para separadores */
    .separator {
        height: 2px;
        background-color: #e9ecef;
        margin: 2rem 0;
    }
    
    /* Estilos para los créditos */
    .credits {
        text-align: center;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-top: 30px;
        border: 1px solid #dee2e6;
    }
    .credits h3 {
        color: #343a40;
        margin-bottom: 10px;
    }
    .credits p {
        color: #495057;
        margin: 5px 0;
    }
    
    /* Ocultar elementos no deseados */
    [data-testid="stFileUploadDropzone"] {
        min-height: 0 !important;
    }
    .upload-text {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

class ControlParticipacion:
    """
    Clase principal para gestionar el control de participación.
    Maneja estudiantes, preguntas, y sus interacciones.
    """
    
    def __init__(self):
        """
        Inicializa la aplicación y sus estados.
        Configura los estados iniciales si no existen.
        """
        # Inicialización de estados de la aplicación
        self.initialize_session_states()
        
    def initialize_session_states(self):
        """
        Inicializa todos los estados de la sesión necesarios.
        Crea las estructuras de datos iniciales si no existen.
        """
        # Estado para estudiantes
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame({
                'Nombre': [],
                'Participaciones': [],
                'Puntaje': []
            })
        
        # Estado para participaciones esperadas
        if 'participaciones_esperadas' not in st.session_state:
            st.session_state.participaciones_esperadas = 5
        
        # Estado para preguntas
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []
        
        # Estado para preguntas completadas
        if 'preguntas_completadas' not in st.session_state:
            st.session_state.preguntas_completadas = set()
        
        # Estado para el logo
        if 'logo' not in st.session_state:
            st.session_state.logo = None
        
        # Estado para mensajes de éxito/error
        if 'messages' not in st.session_state:
            st.session_state.messages = []

    def show_messages(self):
        """
        Muestra mensajes de éxito o error almacenados en el estado.
        Limpia los mensajes después de mostrarlos.
        """
        if st.session_state.messages:
            for msg_type, msg_text in st.session_state.messages:
                if msg_type == 'success':
                    st.success(msg_text)
                elif msg_type == 'error':
                    st.error(msg_text)
                elif msg_type == 'info':
                    st.info(msg_text)
            st.session_state.messages = []

    def add_message(self, msg_type, msg_text):
        """
        Agrega un mensaje al estado para ser mostrado.
        
        Args:
            msg_type (str): Tipo de mensaje ('success', 'error', 'info')
            msg_text (str): Texto del mensaje
        """
        st.session_state.messages.append((msg_type, msg_text))

    def cargar_logo(self):
        """
        Maneja la carga y visualización del logo.
        Permite cargar solo imágenes JPG y BMP.
        """
        col1, col2, col3 = st.columns([1, 10, 1])
        with col1:
            logo_file = st.file_uploader("", type=['jpg', 'bmp'], key='logo_upload')
            if logo_file:
                try:
                    st.session_state.logo = base64.b64encode(logo_file.getvalue()).decode()
                    self.add_message('success', 'Logo cargado exitosamente')
                    time.sleep(0.1)  # Pequeña pausa para asegurar actualización
                    st.experimental_rerun()
                except Exception as e:
                    self.add_message('error', f'Error al cargar el logo: {str(e)}')

    def mostrar_header(self):
        """
        Muestra el encabezado de la aplicación y el logo si existe.
        Aplica estilos CSS para una presentación profesional.
        """
        if st.session_state.logo:
            st.markdown(f"""
                <div class="logo-container">
                    <img src="data:image/jpeg;base64,{st.session_state.logo}" 
                         width="300" 
                         style="max-width: 100%; height: auto;"/>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("<h1 class='title'>CONTROL DE PARTICIPACIÓN</h1>", unsafe_allow_html=True)

    def calcular_puntaje(self, participaciones):
        """
        Calcula el puntaje basado en el número de participaciones.
        
        Args:
            participaciones (int): Número de participaciones del estudiante
            
        Returns:
            float: Puntaje calculado (máximo 20)
        """
        return min(20, (participaciones / st.session_state.participaciones_esperadas) * 20)

    def actualizar_estudiante(self, idx, participaciones):
        """
        Actualiza los datos de un estudiante.
        
        Args:
            idx (int): Índice del estudiante en el DataFrame
            participaciones (int): Nuevo número de participaciones
        """
        st.session_state.estudiantes.at[idx, 'Participaciones'] = participaciones
        st.session_state.estudiantes.at[idx, 'Puntaje'] = self.calcular_puntaje(participaciones)

    def mostrar_estudiantes(self):
        """
        Gestiona la sección de estudiantes.
        Incluye agregar, eliminar y modificar estudiantes.
        """
        st.markdown("### GESTIÓN DE ESTUDIANTES")
        
        # Control de participaciones esperadas
        col1, col2 = st.columns([3, 1])
        with col2:
            participaciones = st.number_input(
                "PARTICIPACIONES ESPERADAS",
                min_value=1,
                value=st.session_state.participaciones_esperadas
            )
            if participaciones != st.session_state.participaciones_esperadas:
                st.session_state.participaciones_esperadas = participaciones
                # Actualizar todos los puntajes
                for idx in st.session_state.estudiantes.index:
                    self.actualizar_estudiante(
                        idx,
                        st.session_state.estudiantes.at[idx, 'Participaciones']
                    )
                st.experimental_rerun()

        # Agregar estudiante
        col1, col2 = st.columns([3, 1])
        with col1:
            nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE")
        with col2:
            if st.button("AGREGAR"):
                if nuevo_estudiante:
                    if nuevo_estudiante not in st.session_state.estudiantes['Nombre'].values:
                        nuevo_df = pd.DataFrame({
                            'Nombre': [nuevo_estudiante],
                            'Participaciones': [0],
                            'Puntaje': [0]
                        })
                        st.session_state.estudiantes = pd.concat([
                            st.session_state.estudiantes, nuevo_df
                        ], ignore_index=True)
                        self.add_message('success', f'Estudiante {nuevo_estudiante} agregado exitosamente')
                        st.experimental_rerun()
                    else:
                        self.add_message('error', 'Este estudiante ya existe')

        # Lista de estudiantes
        if not st.session_state.estudiantes.empty:
            for idx, row in st.session_state.estudiantes.iterrows():
                with st.container():
                    cols = st.columns([2, 2, 1, 1, 1])
                    with cols[0]:
                        st.markdown(f"**{row['Nombre']}**")
                    with cols[1]:
                        st.write(f"{row['Participaciones']}/{st.session_state.participaciones_esperadas} | {row['Puntaje']:.1f}")
                    with cols[2]:
                        if st.button("+1", key=f"plus_{idx}"):
                            self.actualizar_estudiante(idx, row['Participaciones'] + 1)
                            st.experimental_rerun()
                    with cols[3]:
                        if st.button("-1", key=f"minus_{idx}"):
                            if row['Participaciones'] > 0:
                                self.actualizar_estudiante(idx, row['Participaciones'] - 1)
                                st.experimental_rerun()
                    with cols[4]:
                        if st.button("❌", key=f"del_{idx}"):
                            st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)
                            self.add_message('info', f'Estudiante {row["Nombre"]} eliminado')
                            st.experimental_rerun()

            # Eliminar todos los estudiantes
            if st.button("ELIMINAR TODOS LOS ESTUDIANTES", type="primary"):
                st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Participaciones', 'Puntaje'])
                self.add_message('info', 'Todos los estudiantes han sido eliminados')
                st.experimental_rerun()

    def mostrar_graficos(self):
        """
        Muestra los gráficos de participación.
        Incluye gráfico de barras y torta.
        """
        if not st.session_state.estudiantes.empty:
            col1, col2 = st.columns(2)
            
            # Gráfico de barras
            with col1:
                fig_bar = px.bar(
                    st.session_state.estudiantes,
                    x='Nombre',
                    y='Participaciones',
                    title='PARTICIPACIONES POR ESTUDIANTE',
                    color='Participaciones',
                    color_continuous_scale='Viridis'
                )
                fig_bar.update_layout(
                    title_x=0.5,
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis_gridcolor='rgba(0,0,0,0.1)'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Gráfico de torta
            with col2:
                total_participaciones = st.session_state.estudiantes['Participaciones'].sum()
                if total_participaciones > 0:
                    datos_torta = st.session_state.estudiantes.copy()
                    datos_torta['Porcentaje'] = (datos_torta['Participaciones'] / total_participaciones * 100)
                    fig_pie = px.pie(
                        datos_torta,
                        values='Porcentaje',
                        names='Nombre',
                        title='DISTRIBUCIÓN DE PARTICIPACIONES (%)',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_pie.update_layout(
                        title_x=0.5,
                        showlegend=True
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

    def gestionar_preguntas(self):
        """
        Gestiona la sección de preguntas.
        Incluye agregar, marcar como completadas y eliminar preguntas.
        """
        st.markdown("### PREGUN
