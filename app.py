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
    .title {
        text-transform: uppercase;
        text-align: center;
        font-weight: bold;
        font-size: 2.5em;
    }
    .logo-upload {
        position: absolute;
        top: 5px;
        left: 5px;
        width: 150px;
        z-index: 100;
    }
    .logo-upload .stUploadUploader {
        width: 150px !important;
    }
    .logo-upload label {
        font-size: 0.8em;
    }
    /* Hacer el área de carga más compacta */
    .logo-upload div[data-testid="stFileUploader"] {
        width: 150px !important;
        padding: 0.5rem !important;
    }
    .logo-upload div[data-testid="stFileUploader"] small {
        font-size: 0.6em;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 1rem;
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
        font-weight: bold;
        color: #6c757d;
        background-color: #e9ecef;
    }
    .student-row {
        background-color: #ffffff;
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 3px;
        border: 1px solid #dee2e6;
        font-size: 0.9em;
    }
    .delete-button {
        color: white;
        background-color: #dc3545;
        border: none;
        border-radius: 4px;
        padding: 2px 8px;
        cursor: pointer;
    }
    .delete-button:hover {
        background-color: #c82333;
    }
    .student-controls {
        display: flex;
        gap: 5px;
    }
    .student-info {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .compact-button {
        padding: 0.2rem 0.5rem !important;
        font-size: 0.8em !important;
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
            if st.button("LOGO", use_container_width=False):
                file = st.file_uploader("", type=['png', 'jpg', 'jpeg'])
                if file is not None:
                    st.session_state.logo = base64.b64encode(file.read()).decode()

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
        if nombre in st.session_state.estudiantes['Nombre'].values:
            st.session_state.estudiantes = st.session_state.estudiantes[
                st.session_state.estudiantes['Nombre'] != nombre
            ].reset_index(drop=True)
            return True
        return False

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

        # Crear contenedor para todos los estudiantes
        container = st.container()
        
        with container:
            for idx, estudiante in st.session_state.estudiantes.iterrows():
                with st.container():
                    st.markdown(f'<div class="student-row">', unsafe_allow_html=True)
                    cols = st.columns([2, 2, 1, 1, 1])
                    
                    # Columna nombre
                    with cols[0]:
                        st.markdown(f"<div style='font-size:0.9em'><b>{estudiante['Nombre']}</b></div>", unsafe_allow_html=True)
                    
                    # Columna participaciones y nota
                    with cols[1]:
                        st.markdown(
                            f"<div style='font-size:0.9em'>Part: {estudiante['Participaciones']}/{st.session_state.participaciones_esperadas} | Nota: {estudiante['Puntaje']:.1f}</div>",
                            unsafe_allow_html=True
                        )
                    
                    # Botones de control
                    with cols[2]:
                        if st.button("+1", key=f"plus_{idx}", help="Aumentar participación"):
                            participaciones = st.session_state.estudiantes.at[idx, 'Participaciones'] + 1
                            st.session_state.estudiantes.at[idx, 'Participaciones'] = participaciones
                            st.session_state.estudiantes.at[idx, 'Puntaje'] = min(
                                20,
                                (participaciones / st.session_state.participaciones_esperadas) * 20
                            )
                            st.rerun()
                    
                    with cols[3]:
                        if st.button("-1", key=f"minus_{idx}", help="Disminuir participación"):
                            if st.session_state.estudiantes.at[idx, 'Participaciones'] > 0:
                                participaciones = st.session_state.estudiantes.at[idx, 'Participaciones'] - 1
                                st.session_state.estudiantes.at[idx, 'Participaciones'] = participaciones
                                st.session_state.estudiantes.at[idx, 'Puntaje'] = min(
                                    20,
                                    (participaciones / st.session_state.participaciones_esperadas) * 20
                                )
                                st.rerun()
                    
                    with cols[4]:
                        if st.button("❌", key=f"delete_{idx}"):
                            st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Botones de control general
            if not st.session_state.estudiantes.empty:
                cols = st.columns([1, 1])
                with cols[0]:
                    if st.button("ELIMINAR TODOS LOS ESTUDIANTES", type="primary"):
                        st.session_state.estudiantes = pd.DataFrame(
                            columns=['Nombre', 'Participaciones', 'Puntaje']
                        )
                        st.rerun()
                with cols[1]:
                    archivo = st.file_uploader("CARGAR ESTUDIANTES", type=['txt'])
                    if archivo is not None:
                        try:
                            contenido = StringIO(archivo.getvalue().decode("utf-8")).read().splitlines()
                            nuevos_estudiantes = []
                            for estudiante in contenido:
                                if estudiante.strip() and estudiante not in st.session_state.estudiantes['Nombre'].values:
                                    nuevos_estudiantes.append({
                                        'Nombre': estudiante.strip(),
                                        'Participaciones': 0,
                                        'Puntaje': 0
                                    })
                            if nuevos_estudiantes:
                                nuevo_df = pd.DataFrame(nuevos_estudiantes)
                                st.session_state.estudiantes = pd.concat(
                                    [st.session_state.estudiantes, nuevo_df],
                                    ignore_index=True
                                )
                                st.success("Estudiantes cargados exitosamente")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error al cargar el archivo: {str(e)}")

    def agregar_estudiante(self):
        col1, col2 = st.columns([3, 1])
        with col1:
            nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE")
        with col2:
            if st.button("AGREGAR ESTUDIANTE"):
                if nuevo_estudiante:
                    estudiantes_actuales = st.session_state.estudiantes['Nombre'].values
                    if nuevo_estudiante not in estudiantes_actuales:
                        nuevo_df = pd.DataFrame({
                            'Nombre': [nuevo_estudiante],
                            'Participaciones': [0],
                            'Puntaje': [0]
                        })
                        st.session_state.estudiantes = pd.concat(
                            [st.session_state.estudiantes, nuevo_df],
                            ignore_index=True
                        )
                        st.success("Estudiante agregado con éxito")
                    else:
                        st.write("Este estudiante ya existe")
                    time.sleep(0.1)
                    st.rerun())
                    
                    # Columna participaciones y nota
                    with cols[1]:
                        st.markdown(
                            f"<div style='font-size:0.9em'>Part: {estudiante['Participaciones']}/{st.session_state.participaciones_esperadas} | Nota: {estudiante['Puntaje']:.1f}</div>",
                            unsafe_allow_html=True
                        )
                    
                    # Botones de control
                    with cols[2]:
                        if st.button("+1", key=f"plus_{estudiante['Nombre']}", help="Aumentar participación"):
                            participaciones = st.session_state.estudiantes.at[idx, 'Participaciones'] + 1
                            st.session_state.estudiantes.at[idx, 'Participaciones'] = participaciones
                            st.session_state.estudiantes.at[idx, 'Puntaje'] = min(
                                20,
                                (participaciones / st.session_state.participaciones_esperadas) * 20
                            )
                            st.rerun()
                    
                    with cols[3]:
                        if st.button("-1", key=f"minus_{estudiante['Nombre']}", help="Disminuir participación"):
                            if st.session_state.estudiantes.at[idx, 'Participaciones'] > 0:
                                participaciones = st.session_state.estudiantes.at[idx, 'Participaciones'] - 1
                                st.session_state.estudiantes.at[idx, 'Participaciones'] = participaciones
                                st.session_state.estudiantes.at[idx, 'Puntaje'] = min(
                                    20,
                                    (participaciones / st.session_state.participaciones_esperadas) * 20
                                )
                                st.rerun()
                    
                    with cols[4]:
                        if st.button("❌", key=f"delete_{idx}"):
                            st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Botón para limpiar lista de estudiantes
            if not st.session_state.estudiantes.empty:
                if st.button("LIMPIAR LISTA DE ESTUDIANTES", type="primary"):
                    st.session_state.estudiantes = pd.DataFrame(
                        columns=['Nombre', 'Participaciones', 'Puntaje']
                    )
                    st.rerun()

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
        
        col1, col2 = st.columns([4, 1])
        with col1:
            nueva_pregunta = st.text_input("ESCRIBA UNA NUEVA PREGUNTA")
            if nueva_pregunta and st.button("AGREGAR PREGUNTA"):
                st.session_state.preguntas.append(nueva_pregunta)
                st.success("Pregunta agregada exitosamente")
        
        with col2:
            archivo = st.file_uploader("CARGAR PREGUNTAS", type=['txt'])
            if archivo is not None:
                try:
                    contenido = StringIO(archivo.getvalue().decode("utf-8")).read().splitlines()
                    contenido = [linea.strip() for linea in contenido if linea.strip()]
                    st.session_state.preguntas.extend(contenido)
                    st.success("Preguntas cargadas exitosamente")
                except Exception as e:
                    st.error(f"Error al cargar el archivo: {str(e)}")

        # Mostrar preguntas
        if st.session_state.preguntas:
            for i, pregunta in enumerate(st.session_state.preguntas):
                with st.container():
                    esta_completada = i in st.session_state.preguntas_completadas
                    clase_css = "question-box" + (" question-completed" if esta_completada else "")
                    
                    st.markdown(f'<div class="{clase_css}">', unsafe_allow_html=True)
                    
                    cols = st.columns([3, 1, 1])
                    with cols[0]:
                        if esta_completada:
                            st.markdown(f"<p style='text-decoration: line-through; font-weight: bold;'>{i+1}. {pregunta}</p>", unsafe_allow_html=True)
                        else:
                            st.write(f"{i+1}. {pregunta}")
                    
                    with cols[1]:
                        button_label = "Desmarcar" if esta_completada else "Completar"
                        button_type = "secondary" if esta_completada else "primary"
                        if st.button(button_label, key=f"complete_{i}", type=button_type):
                            if esta_completada:
                                st.session_state.preguntas_completadas.remove(i)
                            else:
                                st.session_state.preguntas_completadas.add(i)
                            st.rerun()
                    
                    with cols[2]:
                        if st.button("❌", key=f"delete_pregunta_{i}"):
                            st.session_state.preguntas.pop(i)
                            if i in st.session_state.preguntas_completadas:
                                st.session_state.preguntas_completadas.remove(i)
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Botón para eliminar todas las preguntas
            if st.button("ELIMINAR TODAS LAS PREGUNTAS", type="primary"):
                st.session_state.preguntas = []
                st.session_state.preguntas_completadas = set()
                st.rerun()

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
