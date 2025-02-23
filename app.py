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
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .stTextInput>div>div>input {
        padding: 0.5rem;
    }
    /* Eliminar textos de todos los uploaders */
    div[data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"],
    div[data-testid="stFileUploader"] p,
    div[data-testid="stFileUploader"] span[data-testid="stMarkdownContainer"] {
        display: none !important;
    }

    /* Ajustar el contenedor del uploader */
    div[data-testid="stFileUploader"] section {
        min-height: unset !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    /* Estilo para el botón de Browse files */
    div[data-testid="stFileUploader"] button {
        font-size: 9.5px !important;
        padding: 2px 8px !important;
    }

    /* Eliminar espacio adicional */
    div[data-testid="stFileUploader"] > div:first-child {
        margin: 0 !important;
        padding: 0 !important;
    }
    .uploadedFile {
        width: 15%;
    }
    .stFileUploader > section {
        width: 15%;
        padding: 1px;
    }
    .stFileUploader > div > div {
        width: 15%;
        padding: 1px;
    }
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
    .student-section {
        font-size: 1.1em;
    }
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
    /* Estilos para los iconos de participación */
    .icon-container {
        display: inline-flex;
        gap: 5px;
        align-items: center;
    }
    
    .stButton button {
        padding: 0 10px;
    }
    
    /* Estilo para los botones de puntos */
    .stButton button:contains("⬤") {
        color: #000000 !important;  /* Puntos inactivos en negro */
        background-color: transparent !important;
        border: none !important;
        transition: color 0.3s ease;
        padding: 0 5px;
        font-size: 24px;
    }
    
    /* Puntos activos en amarillo */
    .stButton button[data-testid="secondary"]:contains("⬤") {
        color: #FFD700 !important;
    }
    
    /* Botón de eliminar individual */
    .stButton button:contains("🗑️") {
        color: #ff4b4b !important;
        background-color: transparent !important;
        border: 1px solid #ff4b4b !important;
        border-radius: 4px;
    }
    
    /* Botón de eliminar todos */
    .stButton button:contains("ELIMINAR TODOS") {
        background-color: #ff4b4b !important;
        color: white !important;
        margin-top: 20px;
    }
    
    /* Botón de reiniciar puntos */
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
    .student-controls {
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
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Puntaje']
            )
        if 'participaciones_esperadas' not in st.session_state:
            st.session_state.participaciones_esperadas = 5
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []
        if 'preguntas_completadas' not in st.session_state:
            st.session_state.preguntas_completadas = set()
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
                <div class="logo-container">
                    <img src="data:image/png;base64,{st.session_state.logo}" width="300"/>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<h1 class='title'>CONTROL DE PARTICIPACIÓN</h1>", unsafe_allow_html=True)

    def cargar_archivo_txt(self, tipo):
        archivo = st.file_uploader(f"SUBE DATA AMIGO ({tipo})", type=['txt'], key=f"uploader_{tipo}")
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
                
                elif tipo == "preguntas":
                    st.session_state.preguntas.extend(contenido)
                    st.success("Preguntas cargadas exitosamente")
            except Exception as e:
                st.error(f"Error al cargar el archivo: {str(e)}")

    def eliminar_estudiante(self, nombre):
        try:
            # Primero verificar si el estudiante existe
            if nombre in st.session_state.iconos_estado:
                # Eliminar el estado de los iconos primero
                del st.session_state.iconos_estado[nombre]
                
            # Luego eliminar del DataFrame
            st.session_state.estudiantes = st.session_state.estudiantes[
                st.session_state.estudiantes['Nombre'] != nombre
            ].reset_index(drop=True)
            
            return True
        except Exception as e:
            st.error(f"Error al eliminar estudiante: {str(e)}")
            return False

    def limpiar_lista_estudiantes(self):
        try:
            # Limpiar DataFrame
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Puntaje']
            )
            # Limpiar estados de iconos
            st.session_state.iconos_estado = {}
            
            st.success("Lista de estudiantes eliminada completamente")
            
        except Exception as e:
            st.error(f"Error al limpiar lista: {str(e)}")

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
            if st.button("🔄 REINICIAR PUNTOS", type="secondary", help="Reiniciar todos los puntos a cero"):
                for nombre in st.session_state.iconos_estado:
                    st.session_state.iconos_estado[nombre] = [False] * st.session_state.participaciones_esperadas
                # Reiniciar puntajes en el DataFrame
                st.session_state.estudiantes['Participaciones'] = 0
                st.session_state.estudiantes['Puntaje'] = 0.0
                st.rerun()

        # Inicializar el estado de los iconos si no existe
        if 'iconos_estado' not in st.session_state:
            st.session_state.iconos_estado = {}

        for _, estudiante in st.session_state.estudiantes.iterrows():
            nombre = estudiante['Nombre']
            
            # Inicializar estado de iconos para este estudiante si no existe
            if nombre not in st.session_state.iconos_estado:
                st.session_state.iconos_estado[nombre] = [False] * st.session_state.participaciones_esperadas

            with st.container():
                st.markdown(f'<div class="student-row">', unsafe_allow_html=True)
                cols = st.columns([3, 4, 2, 1])
                
                with cols[0]:
                    st.write(f"**{nombre}**")
                
                with cols[1]:
                    # Mostrar iconos interactivos
                    for i in range(st.session_state.participaciones_esperadas):
                        icon_key = f"icon_{nombre}_{i}"
                        is_active = st.session_state.iconos_estado[nombre][i]
                        if st.button("⬤", key=icon_key, 
                                   help="Click para marcar participación correcta",
                                   type="secondary" if is_active else "primary"):
                            if not is_active:  # Solo permitir activar, no desactivar
                                st.session_state.iconos_estado[nombre][i] = True
                                # Recalcular participaciones y puntaje
                                participaciones = sum(st.session_state.iconos_estado[nombre])
                                idx = st.session_state.estudiantes[st.session_state.estudiantes['Nombre'] == nombre].index[0]
                                st.session_state.estudiantes.loc[idx, 'Participaciones'] = participaciones
                                puntaje = (participaciones * 20) / st.session_state.participaciones_esperadas
                                st.session_state.estudiantes.loc[idx, 'Puntaje'] = round(puntaje, 1)
                                st.rerun()
                
                with cols[2]:
                    participaciones = sum(st.session_state.iconos_estado[nombre])
                    puntaje = (participaciones * 20) / st.session_state.participaciones_esperadas
                    st.write(f"Nota: {round(puntaje, 1)}")
                
                with cols[3]:
                    if st.button("🗑️", key=f"delete_{nombre}", help="Eliminar estudiante"):
                        if self.eliminar_estudiante(nombre):
                            st.success(f"Estudiante {nombre} eliminado exitosamente")
                            time.sleep(0.1)  # Pequeña pausa para asegurar que el mensaje se muestre
                            st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

        # Botones de control al final
        col1, col2 = st.columns(2)
        with col1:
            if len(st.session_state.estudiantes) > 0:
                if st.button("❌ ELIMINAR TODOS", type="secondary", 
                           help="Eliminar todos los estudiantes",
                           use_container_width=True):
                    self.limpiar_lista_estudiantes()
                    st.rerun()

    def mostrar_graficos(self):
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
                fig_bar.update_layout(
                    title_x=0.5,
                    title_font_size=20
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                datos_torta = st.session_state.estudiantes.copy()
                total_participaciones = datos_torta['Participaciones'].sum()
                if total_participaciones > 0:
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
                        title_font_size=20
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

    def gestionar_preguntas(self):
        st.markdown("### PREGUNTAS PLANIFICADAS")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            nueva_pregunta = st.text_input("ESCRIBA UNA NUEVA PREGUNTA")
        with col2:
            if st.button("AGREGAR PREGUNTA"):
                if nueva_pregunta:
                    st.session_state.preguntas.append(nueva_pregunta)
        with col3:
            self.cargar_archivo_txt("preguntas")

        for i, pregunta in enumerate(st.session_state.preguntas):
            with st.container():
                st.markdown(
                    f'<div class="question-box{" question-completed" if i in st.session_state.preguntas_completadas else ""}">',
                    unsafe_allow_html=True
                )
                cols = st.columns([4, 1])
                with cols[0]:
                    st.write(f"{i+1}. {pregunta}")
                with cols[1]:
                    if i in st.session_state.preguntas_completadas:
                        if st.button("Desmarcar", key=f"uncheck_{i}"):
                            st.session_state.preguntas_completadas.remove(i)
                    else:
                        if st.button("Completar", key=f"check_{i}"):
                            st.session_state.preguntas_completadas.add(i)
                st.markdown('</div>', unsafe_allow_html=True)

        if st.button("LIMPIAR PREGUNTAS"):
            st.session_state.preguntas = []
            st.session_state.preguntas_completadas = set()
            st.success("Lista de preguntas limpiada exitosamente")

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
        st.markdown("---")
        self.mostrar_estudiantes()
        self.mostrar_graficos()
        st.markdown("---")
        self.gestionar_preguntas()
        self.mostrar_creditos()

# Iniciar la aplicación
if __name__ == "__main__":
    app = ControlParticipacion()
    app.run()
