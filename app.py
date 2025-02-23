import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
from io import StringIO

# Configuración de la página
st.set_page_config(page_title="CONTROL DE PARTICIPACIÓN", layout="wide")

# Estilo personalizado modificado
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
        position: absolute;
        top: 10px;
        left: 10px;
        max-width: 200px;
    }
    .logo-container img {
        width: 100%;
        height: auto;
    }
    .student-row {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        border: 1px solid #dee2e6;
        display: flex;
        align-items: center;
    }
    .participation-circle {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-block;
        margin: 0 5px;
        cursor: pointer;
    }
    .circle-black {
        background-color: black;
    }
    .circle-yellow {
        background-color: yellow;
    }
    .question-slide {
        text-align: center;
        padding: 20px;
        margin: 20px 0;
        background-color: #f8f9fa;
        border-radius: 10px;
        position: relative;
    }
    .navigation-buttons {
        display: flex;
        justify-content: space-between;
        position: absolute;
        width: 100%;
        top: 50%;
        transform: translateY(-50%);
    }
    .file-upload-btn {
        width: 30px !important;
        height: 30px !important;
        padding: 0 !important;
        border-radius: 50% !important;
    }
    .config-section {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
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
                columns=['Nombre', 'Participaciones', 'Respuestas_Correctas']
            )
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []
        if 'pregunta_actual' not in st.session_state:
            st.session_state.pregunta_actual = 0
        if 'logo' not in st.session_state:
            st.session_state.logo = None
        if 'num_preguntas' not in st.session_state:
            st.session_state.num_preguntas = 5  # Valor por defecto

    def cargar_logo(self):
        st.markdown('<div style="width:30px;position:fixed;top:10px;left:10px;z-index:1000">', unsafe_allow_html=True)
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

    def configuracion_inicial(self):
        with st.container():
            st.markdown('<div class="config-section">', unsafe_allow_html=True)
            cols = st.columns([2, 1])
            with cols[0]:
                nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE", key="nuevo_estudiante")
                if st.button("AGREGAR ESTUDIANTE") and nuevo_estudiante:
                    if nuevo_estudiante not in st.session_state.estudiantes['Nombre'].values:
                        nuevo_df = pd.DataFrame({
                            'Nombre': [nuevo_estudiante],
                            'Participaciones': [0],
                            'Respuestas_Correctas': [0]
                        })
                        st.session_state.estudiantes = pd.concat(
                            [st.session_state.estudiantes, nuevo_df],
                            ignore_index=True
                        )
            with cols[1]:
                st.session_state.num_preguntas = st.number_input(
                    "NÚMERO DE PREGUNTAS",
                    min_value=1,
                    value=st.session_state.num_preguntas
                )
            st.markdown('</div>', unsafe_allow_html=True)

    def mostrar_pregunta_actual(self):
        if st.session_state.preguntas:
            st.markdown('<div class="question-slide">', unsafe_allow_html=True)
            cols = st.columns([1, 3, 1])
            with cols[0]:
                if st.button("←") and st.session_state.pregunta_actual > 0:
                    st.session_state.pregunta_actual -= 1
                    st.rerun()
            with cols[1]:
                st.markdown(f"### Pregunta {st.session_state.pregunta_actual + 1}")
                st.write(st.session_state.preguntas[st.session_state.pregunta_actual])
            with cols[2]:
                if st.button("→") and st.session_state.pregunta_actual < len(st.session_state.preguntas) - 1:
                    st.session_state.pregunta_actual += 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    def mostrar_estudiantes(self):
        for _, estudiante in st.session_state.estudiantes.iterrows():
            with st.container():
                cols = st.columns([3, 4, 1])
                with cols[0]:
                    st.write(estudiante['Nombre'])
                with cols[1]:
                    # Usar el número de preguntas definido por el profesor
                    for i in range(st.session_state.num_preguntas):
                        color = "yellow" if i < estudiante['Respuestas_Correctas'] else "black"
                        if st.button("⬤", key=f"circle_{estudiante['Nombre']}_{i}", 
                                   help="Click para marcar respuesta correcta"):
                            idx = st.session_state.estudiantes[
                                st.session_state.estudiantes['Nombre'] == estudiante['Nombre']
                            ].index[0]
                            if color == "black":
                                st.session_state.estudiantes.loc[idx, 'Respuestas_Correctas'] += 1
                                st.session_state.estudiantes.loc[idx, 'Participaciones'] += 1
                            st.rerun()
                with cols[2]:
                    if st.button("🗑️", key=f"delete_{estudiante['Nombre']}"):
                        self.eliminar_estudiante(estudiante['Nombre'])
                        st.rerun()

    def eliminar_estudiante(self, nombre):
        st.session_state.estudiantes = st.session_state.estudiantes[
            st.session_state.estudiantes['Nombre'] != nombre
        ].reset_index(drop=True)

    def cargar_preguntas(self):
        st.markdown('<div style="width:30px;position:fixed;bottom:10px;right:10px">', unsafe_allow_html=True)
        archivo = st.file_uploader("", type=['txt'])
        st.markdown('</div>', unsafe_allow_html=True)
        if archivo is not None:
            contenido = StringIO(archivo.getvalue().decode("utf-8")).read().splitlines()
            st.session_state.preguntas = [linea.strip() for linea in contenido if linea.strip()]
            st.success(f"Se cargaron {len(st.session_state.preguntas)} preguntas")

    def mostrar_estadisticas(self):
        if not st.session_state.estudiantes.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig_bar = px.bar(
                    st.session_state.estudiantes,
                    x='Nombre',
                    y=['Participaciones', 'Respuestas_Correctas'],
                    title='PARTICIPACIONES Y RESPUESTAS CORRECTAS',
                    barmode='group'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Calcular el porcentaje de respuestas correctas
                porcentaje_correctas = (st.session_state.estudiantes['Respuestas_Correctas'] / 
                                      st.session_state.num_preguntas * 100).round(2)
                
                fig_pie = px.pie(
                    st.session_state.estudiantes,
                    values=porcentaje_correctas,
                    names='Nombre',
                    title='PORCENTAJE DE RESPUESTAS CORRECTAS'
                )
                st.plotly_chart(fig_pie, use_container_width=True)

    def run(self):
        self.cargar_logo()
        self.mostrar_header()
        self.configuracion_inicial()
        self.mostrar_pregunta_actual()
        self.mostrar_estudiantes()
        self.mostrar_estadisticas()
        self.cargar_preguntas()

if __name__ == "__main__":
    app = ControlParticipacion()
    app.run()
