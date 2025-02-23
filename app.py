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
        # Inicializar estados básicos
        for key in ['estudiantes', 'preguntas', 'iconos_estado', 'file_key']:
            if key not in st.session_state:
                st.session_state[key] = [] if key in ['preguntas'] else {}
                
        # Configurar valores por defecto
        if 'participaciones_esperadas' not in st.session_state:
            st.session_state.participaciones_esperadas = 5
        if 'pregunta_actual' not in st.session_state:
            st.session_state.pregunta_actual = 0
        if 'logo' not in st.session_state:
            st.session_state.logo = None
            
        # Ocultar errores globalmente
        st.set_option('client.showErrorDetails', False)
        st.set_option('client.showWarningOnDirectExecution', False)
        
        # Aplicar estilos para ocultar elementos no deseados
        self.aplicar_estilos()
        
        # Aplicar estilos globales
        st.markdown("""
            <style>
            .main {
                background-color: #f8f9fa !important;
            }
            .stApp {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 50%, #f8f9fa 100%) !important;
            }
            div[data-testid="stAppViewContainer"] {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 50%, #f8f9fa 100%) !important;
            }
            </style>
        """, unsafe_allow_html=True)

    def cargar_logo(self):
        with st.container():
            with st.sidebar:
                logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="logo_uploader")
                if logo_file is not None:
                    st.session_state.logo = base64.b64encode(logo_file.read()).decode()

    def mostrar_imagen_actual(self):
        """Muestra la imagen actual con controles de navegación."""
        if 'imagenes' in st.session_state and st.session_state.imagenes:
            col1, col2, col3 = st.columns([1, 6, 1])
            
            with col1:
                if st.button("⬅️", 
                           key="prev_image", 
                           disabled=st.session_state.imagen_actual == 0,
                           help="Imagen anterior"):
                    st.session_state.imagen_actual = max(0, st.session_state.imagen_actual - 1)
            
            with col2:
                total_imagenes = len(st.session_state.imagenes)
                imagen_actual = st.session_state.imagenes[st.session_state.imagen_actual]
                
                st.markdown(f"""
                    <div class="imagen-card">
                        <div class="imagen-numero">{st.session_state.imagen_actual + 1}/{total_imagenes}</div>
                        <img src="data:image/jpeg;base64,{imagen_actual['data']}" 
                             style="width: 100%; height: auto; object-fit: contain;">
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                if st.button("➡️", 
                           key="next_image", 
                           disabled=st.session_state.imagen_actual >= total_imagenes - 1,
                           help="Siguiente imagen"):
                    st.session_state.imagen_actual = min(total_imagenes - 1, st.session_state.imagen_actual + 1)

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
            return True
        except Exception as e:
            st.error(f"Error al limpiar lista: {str(e)}")
            return False

    def cargar_imagenes(self):
        """Carga de imágenes desde la interfaz."""
        uploaded_file = st.file_uploader(
            "",
            type=["png", "jpg", "jpeg"],  # Solo permitir formatos de imagen
            key="uploader_imagen",
            label_visibility="collapsed"
        )

        if uploaded_file:
            try:
                # Leer y procesar la imagen
                image_bytes = uploaded_file.getvalue()
                image_base64 = base64.b64encode(image_bytes).decode()
                
                # Actualizar el estado
                if 'imagenes' not in st.session_state:
                    st.session_state.imagenes = []
                    st.session_state.imagen_actual = 0
                
                # Agregar nueva imagen
                if image_base64 not in [img.get('data') for img in st.session_state.imagenes]:
                    st.session_state.imagenes.append({
                        'data': image_base64,
                        'name': uploaded_file.name
                    })
                    st.session_state.imagen_actual = len(st.session_state.imagenes) - 1
            except:
                pass

    def eliminar_pregunta(self, index):
        if 0 <= index < len(st.session_state.preguntas):
            del st.session_state.preguntas[index]
            return True
        return False

    def limpiar_preguntas(self):
        st.session_state.preguntas = []
        return True

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

    def mostrar_preguntas(self):
        st.sidebar.markdown("### PREGUNTAS")
        
        # Cargar preguntas desde TXT
        self.cargar_preguntas_txt()
        
        if 'preguntas' in st.session_state and st.session_state.preguntas:
            # Contenedor para el carrusel de preguntas
            st.markdown("""
                <style>
                .pregunta-card {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                    position: relative;
                }
                .pregunta-numero {
                    position: absolute;
                    top: 5px;
                    right: 5px;
                    color: #6c757d;
                    font-size: 0.8em;
                }
                .pregunta-nav {
                    display: flex;
                    justify-content: center;
                    gap: 10px;
                    margin-top: 10px;
                }
                </style>
            """, unsafe_allow_html=True)

            # Control de navegación
            if 'pregunta_actual' not in st.session_state:
                st.session_state.pregunta_actual = 0

            # Mostrar pregunta actual
            total_preguntas = len(st.session_state.preguntas)
            
            col1, col2, col3 = st.columns([1, 6, 1])
            
            with col1:
                if st.button("⬅️", key="prev_question", disabled=st.session_state.pregunta_actual == 0):
                    st.session_state.pregunta_actual = max(0, st.session_state.pregunta_actual - 1)
                    st.rerun()
            
            with col2:
                st.markdown(f"""
                    <div class="pregunta-card">
                        <div class="pregunta-numero">Pregunta {st.session_state.pregunta_actual + 1}/{total_preguntas}</div>
                        <p>{st.session_state.preguntas[st.session_state.pregunta_actual]}</p>
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
        
        # Sección de preguntas arriba al centro
        if 'preguntas' in st.session_state and st.session_state.preguntas:
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

            if 'pregunta_actual' not in st.session_state:
                st.session_state.pregunta_actual = 0

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
            
            with col3:
                if st.button("➡️", key="next_question", disabled=st.session_state.pregunta_actual >= total_preguntas - 1):
                    st.session_state.pregunta_actual = min(total_preguntas - 1, st.session_state.pregunta_actual + 1)
                    st.rerun()

        # Sección principal de estudiantes
        st.markdown("---")
        self.agregar_estudiante()
        self.mostrar_estudiantes()
        self.mostrar_graficos()
        
        # Footer con carga de preguntas y créditos
        st.markdown("---")
        
        footer_col1, footer_col2 = st.columns([1, 2])
        with footer_col1:
            self.cargar_preguntas_txt()
        
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
