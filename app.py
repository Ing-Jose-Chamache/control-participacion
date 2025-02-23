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
    /* Ocultar el texto de drag and drop y límite */
    .stFileUploader [data-testid="stMarkdownContainer"] {
        display: none !important;
    }
    
    /* Estilo solo para el botón Browse files */
    .stFileUploader button {
        font-size: 9.5px !important;
        font-family: 'Helvetica Neue', Arial, sans-serif !important;
        padding: 2px 8px !important;
    }
    
    /* Ocultar el texto del límite de archivo */
    .stFileUploader p {
        display: none !important;
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
    .student-row {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        border: 1px solid #dee2e6;
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
            st.session_state.participaciones_esperadas = 10
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
        archivo = st.file_uploader(f"CARGAR ARCHIVO {tipo.upper()}", type=['txt'])
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
        st.session_state.estudiantes = st.session_state.estudiantes[
            st.session_state.estudiantes['Nombre'] != nombre
        ].reset_index(drop=True)

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
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### GESTIÓN DE ESTUDIANTES")
        with col2:
            st.session_state.participaciones_esperadas = st.number_input(
                "PARTICIPACIONES ESPERADAS",
                min_value=1,
                value=st.session_state.participaciones_esperadas
            )

        for _, estudiante in st.session_state.estudiantes.iterrows():
            with st.container():
                st.markdown(f'<div class="student-row">', unsafe_allow_html=True)
                cols = st.columns([3, 2, 2, 1, 1, 1])
                with cols[0]:
                    st.write(f"**{estudiante['Nombre']}**")
                with cols[1]:
                    st.write(f"Participaciones: {estudiante['Participaciones']}/{st.session_state.participaciones_esperadas}")
                with cols[2]:
                    st.write(f"Nota: {estudiante['Puntaje']:.1f}")
                with cols[3]:
                    if st.button("+1", key=f"plus_{estudiante['Nombre']}"):
                        idx = st.session_state.estudiantes[st.session_state.estudiantes['Nombre'] == estudiante['Nombre']].index[0]
                        st.session_state.estudiantes.loc[idx, 'Participaciones'] += 1
                        st.session_state.estudiantes.loc[idx, 'Puntaje'] = min(
                            20,
                            (st.session_state.estudiantes.loc[idx, 'Participaciones'] / 
                             st.session_state.participaciones_esperadas) * 20
                        )
                with cols[4]:
                    if st.button("-1", key=f"minus_{estudiante['Nombre']}"):
                        idx = st.session_state.estudiantes[st.session_state.estudiantes['Nombre'] == estudiante['Nombre']].index[0]
                        if st.session_state.estudiantes.loc[idx, 'Participaciones'] > 0:
                            st.session_state.estudiantes.loc[idx, 'Participaciones'] -= 1
                            st.session_state.estudiantes.loc[idx, 'Puntaje'] = min(
                                20,
                                (st.session_state.estudiantes.loc[idx, 'Participaciones'] / 
                                 st.session_state.participaciones_esperadas) * 20
                            )
                with cols[5]:
                    if st.button("🗑️", key=f"delete_{estudiante['Nombre']}"):
                        self.eliminar_estudiante(estudiante['Nombre'])
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        if st.button("LIMPIAR LISTA DE ESTUDIANTES"):
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Puntaje']
            )
            st.success("Lista de estudiantes limpiada exitosamente")

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
