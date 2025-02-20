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
        margin-top: 1rem;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 1rem;
    }
    .logo-upload {
        max-width: 25%;
        position: absolute;
        top: 10px;
        left: 10px;
    }
    .credits {
        text-align: center;
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-top: 30px;
    }
    .completed {
        text-decoration: line-through;
        color: #808080;
    }
    .student-table {
        font-size: 1.1em;
    }
    .question-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .question-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .student-controls {
        display: flex;
        gap: 10px;
        margin-top: 5px;
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
            logo_file = st.file_uploader("LOGO", type=['png', 'jpg', 'jpeg'], key="logo_upload")
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

    def eliminar_estudiante(self, nombre):
        st.session_state.estudiantes = st.session_state.estudiantes[
            st.session_state.estudiantes['Nombre'] != nombre
        ].reset_index(drop=True)

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
                cols = st.columns([3, 1, 1, 1, 1, 1])
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

    def gestionar_preguntas(self):
        st.markdown("### PREGUNTAS PLANIFICADAS")
        
        for i, pregunta in enumerate(st.session_state.preguntas):
            with st.container():
                st.markdown(f"""
                    <div class="question-card" style="background-color: {'#f8f9fa' if i in st.session_state.preguntas_completadas else '#ffffff'}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="{'text-decoration: line-through; color: #808080;' if i in st.session_state.preguntas_completadas else ''}">
                                {i+1}. {pregunta}
                            </div>
                            <div>
                                <button onclick="handleComplete({i})" style="margin-right: 10px;">
                                    {'✓' if i in st.session_state.preguntas_completadas else '○'}
                                </button>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([4, 1])
                with col2:
                    if i in st.session_state.preguntas_completadas:
                        if st.button("Desmarcar", key=f"uncheck_{i}"):
                            st.session_state.preguntas_completadas.remove(i)
                            st.rerun()
                    else:
                        if st.button("Completar", key=f"check_{i}"):
                            st.session_state.preguntas_completadas.add(i)
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
                    title_font_size=20,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
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

    def run(self):
        st.markdown('<div class="logo-upload">', unsafe_allow_html=True)
        self.cargar_logo()
        st.markdown('</div>', unsafe_allow_html=True)
        
        self.mostrar_header()
        self.mostrar_estudiantes()
        st.markdown("---")
        self.mostrar_graficos()
        st.markdown("---")
        self.gestionar_preguntas()
        
        st.markdown("""
        <div class="credits">
            <h3>Desarrollado por:</h3>
            <p><strong>Ing. José Yván Chamache Chiong</strong></p>
            <p>Lima, Perú - 2024</p>
        </div>
        """, unsafe_allow_html=True)

# Iniciar la aplicación
if __name__ == "__main__":
    app = ControlParticipacion()
    app.run()
