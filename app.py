import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
from io import StringIO
import time

# Configuración de la página
st.set_page_config(page_title="CONTROL DE PARTICIPACIÓN", layout="wide")

# [El resto de los estilos CSS se mantiene igual...]

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
        if 'pregunta_actual' not in st.session_state:
            st.session_state.pregunta_actual = 0
        if 'iconos_estado' not in st.session_state:
            st.session_state.iconos_estado = {}
        if 'logo' not in st.session_state:
            st.session_state.logo = None

    # [Los métodos existentes se mantienen igual hasta mostrar_preguntas]

    def agregar_pregunta(self):
        st.sidebar.markdown("### AGREGAR PREGUNTA")
        nueva_pregunta = st.sidebar.text_area("Nueva pregunta", key="nueva_pregunta")
        if st.sidebar.button("Agregar Pregunta"):
            if nueva_pregunta.strip():
                st.session_state.preguntas.append(nueva_pregunta.strip())
                st.success("Pregunta agregada exitosamente")
                st.session_state.pregunta_actual = len(st.session_state.preguntas) - 1
                st.rerun()
            else:
                st.error("Por favor, ingrese una pregunta válida")

    def mostrar_preguntas(self):
        # Agregar la funcionalidad de agregar preguntas manualmente
        self.agregar_pregunta()
        
        if st.session_state.preguntas:
            # Contenedor para el carrusel de preguntas
            st.markdown("""
                <style>
                .pregunta-card {
                    background-color: #ffffff;
                    border: 2px solid #e1e4e8;
                    border-radius: 12px;
                    padding: 30px;
                    margin: 20px auto;
                    max-width: 900px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    position: relative;
                }
                .pregunta-numero {
                    position: absolute;
                    top: 15px;
                    right: 20px;
                    color: #4a90e2;
                    font-weight: 500;
                    font-size: 1.1em;
                }
                .pregunta-texto {
                    font-size: 1.4em;
                    line-height: 1.6;
                    color: #2e86de;
                    padding: 15px 0;
                    text-align: center;
                    font-weight: 500;
                }
                </style>
            """, unsafe_allow_html=True)

            # Navegación y visualización de preguntas
            col1, col2, col3 = st.columns([1, 6, 1])
            
            with col1:
                if st.button("⬅️", key="prev_question", disabled=st.session_state.pregunta_actual == 0):
                    st.session_state.pregunta_actual = max(0, st.session_state.pregunta_actual - 1)
                    st.rerun()
            
            with col2:
                total_preguntas = len(st.session_state.preguntas)
                st.markdown(f"""
                    <div class="pregunta-card">
                        <div class="pregunta-numero">{st.session_state.pregunta_actual + 1}/{total_preguntas}</div>
                        <div class="pregunta-texto">{st.session_state.preguntas[st.session_state.pregunta_actual]}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Botones de control para la pregunta actual
                col_del, col_clear = st.columns(2)
                with col_del:
                    if st.button("🗑️ Eliminar Pregunta", key="del_current", type="secondary"):
                        if self.eliminar_pregunta(st.session_state.pregunta_actual):
                            if st.session_state.pregunta_actual >= len(st.session_state.preguntas):
                                st.session_state.pregunta_actual = max(0, len(st.session_state.preguntas) - 1)
                            st.success("Pregunta eliminada")
                            st.rerun()
                
                with col_clear:
                    if st.button("🗑️ Eliminar Todas", key="clear_questions", type="secondary"):
                        if self.limpiar_preguntas():
                            st.session_state.pregunta_actual = 0
                            st.success("Todas las preguntas eliminadas")
                            st.rerun()
            
            with col3:
                if st.button("➡️", key="next_question", disabled=st.session_state.pregunta_actual >= total_preguntas - 1):
                    st.session_state.pregunta_actual = min(total_preguntas - 1, st.session_state.pregunta_actual + 1)
                    st.rerun()

    def run(self):
        self.cargar_logo()
        self.mostrar_header()
        
        # Sección de preguntas arriba al centro
        if 'preguntas' in st.session_state and st.session_state.preguntas:
            # Mostrar preguntas
            self.mostrar_preguntas()

        # Sección principal de estudiantes
        st.markdown("---")
        self.agregar_estudiante()
        self.mostrar_estudiantes()
        self.mostrar_graficos()
        
        # Footer con créditos
        st.markdown("---")
        
        footer_col1, footer_col2 = st.columns([1, 2])
        
        with footer_col2:
            st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    padding: 25px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    margin-top: 20px;
                ">
                    <h3 style="
                        color: #2c3e50;
                        font-size: 1.5em;
                        margin-bottom: 10px;
                    ">Desarrollado por</h3>
                    <p style="
                        color: #34495e;
                        font-size: 1.2em;
                        font-weight: 600;
                        margin: 5px 0;
                    ">Ing. José Yván Chamache Chiong</p>
                    <p style="
                        color: #7f8c8d;
                        font-style: italic;
                    ">Lima, Perú - 2024</p>
                </div>
            """, unsafe_allow_html=True)

# Iniciar la aplicación
if __name__ == "__main__":
    app = ControlParticipacion()
    app.run()
