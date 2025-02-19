import streamlit as st
import pandas as pd
import plotly.express as px
import base64

class ControlParticipacion:
    def __init__(self):
        # Inicializar estados de sesión
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Puntaje']
            )
        
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []
        
        if 'preguntas_realizadas' not in st.session_state:
            st.session_state.preguntas_realizadas = []

    def cargar_archivo_txt(self, archivo, tipo='estudiantes'):
        """Cargar archivo de texto (estudiantes o preguntas)"""
        try:
            # Leer contenido del archivo
            contenido = archivo.getvalue().decode('utf-8').splitlines()
            
            # Filtrar líneas no vacías y eliminar espacios
            contenido = [linea.strip() for linea in contenido if linea.strip()]
            
            # Procesar según el tipo de archivo
            if tipo == 'estudiantes':
                # Agregar estudiantes
                for nombre in contenido:
                    if nombre not in st.session_state.estudiantes['Nombre'].values:
                        nuevo_estudiante = pd.DataFrame({
                            'Nombre': [nombre],
                            'Participaciones': [0],
                            'Puntaje': [0]
                        })
                        st.session_state.estudiantes = pd.concat([
                            st.session_state.estudiantes, 
                            nuevo_estudiante
                        ], ignore_index=True)
                
                st.success(f"Se cargaron {len(contenido)} estudiantes")
            
            elif tipo == 'preguntas':
                # Agregar preguntas
                st.session_state.preguntas = contenido
                st.success(f"Se cargaron {len(contenido)} preguntas")
        
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")

    def crear_logo_base64(self, ruta_logo):
        """Convierte una imagen a base64 para incrustarla"""
        try:
            with open(ruta_logo, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
        except Exception as e:
            st.error(f"Error al cargar el logo: {e}")
            return None

    def mostrar_interfaz(self):
        # Configuración de página con colores personalizados
        st.set_page_config(
            page_title="Control de Participación", 
            page_icon="📊",
            layout="wide"
        )

        # Estilo personalizado
        st.markdown("""
        <style>
        .reportview-container {
            background-color: #f0f2f6;
        }
        .sidebar .sidebar-content {
            background-color: #ffffff;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
        }
        .stDataFrame {
            background-color: #ffffff;
            border-radius: 10px;
        }
        .stMetric {
            background-color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f0f2f6;
        }
        </style>
        """, unsafe_allow_html=True)

        # Título principal con estilo
        st.markdown("""
        <h1 style='text-align: center; color: #2C3E50; 
        background-color: #ECF0F1; 
        padding: 10px; 
        border-radius: 10px;'>
        Control de Participación
        </h1>
        """, unsafe_allow_html=True)

        # Menú de pestañas
        tab1, tab2, tab3 = st.tabs([
            "🧑‍🎓 Gestión de Estudiantes", 
            "❓ Preguntas y Participación", 
            "📊 Estadísticas"
        ])

        with tab1:
            self.gestion_estudiantes()

        with tab2:
            self.gestion_preguntas_participacion()

        with tab3:
            self.mostrar_estadisticas()

    def gestion_estudiantes(self):
        st.subheader("Cargar Estudiantes")
        
        # Cargar archivo de estudiantes
        archivo_estudiantes = st.file_uploader(
            "Seleccionar archivo de estudiantes", 
            type=['txt']
        )
        if archivo_estudiantes is not None:
            self.cargar_archivo_txt(archivo_estudiantes, 'estudiantes')

        # Mostrar estudiantes
        st.subheader("Lista de Estudiantes")
        if not st.session_state.estudiantes.empty:
            for i, estudiante in st.session_state.estudiantes.iterrows():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{estudiante['Nombre']}**")
                
                with col2:
                    st.metric("Participaciones", estudiante['Participaciones'])
                
                with col3:
                    st.metric("Puntaje", estudiante['Puntaje'])
                
                with col4:
                    # Botones de puntaje
                    col_sumar, col_restar = st.columns(2)
                    with col_sumar:
                        if st.button(f"+1 {estudiante['Nombre']}", key=f"sumar_{i}"):
                            st.session_state.estudiantes.loc[i, 'Puntaje'] += 1
                            st.session_state.estudiantes.loc[i, 'Participaciones'] += 1
                            st.experimental_rerun()
                    
                    with col_restar:
                        if st.button(f"-1 {estudiante['Nombre']}", key=f"restar_{i}"):
                            st.session_state.estudiantes.loc[i, 'Puntaje'] -= 1
                            st.experimental_rerun()

    def gestion_preguntas_participacion(self):
        st.subheader("Cargar Preguntas")
        
        # Cargar archivo de preguntas
        archivo_preguntas = st.file_uploader(
            "Seleccionar archivo de preguntas", 
            type=['txt']
        )
        if archivo_preguntas is not None:
            self.cargar_archivo_txt(archivo_preguntas, 'preguntas')

        # Gestión de preguntas pendientes
        st.subheader("Preguntas Pendientes")
        preguntas_tmp = st.session_state.preguntas.copy()
        for i, pregunta in enumerate(preguntas_tmp):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(pregunta)
            
            with col2:
                # Botón para marcar pregunta como realizada
                if st.button(f"Realizada {i+1}", key=f"realizada_{i}"):
                    # Mover pregunta a realizadas
                    st.session_state.preguntas_realizadas.append(pregunta)
                    # Eliminar de preguntas pendientes
                    st.session_state.preguntas.remove(pregunta)
                    st.experimental_rerun()

        # Preguntas realizadas
        st.subheader("Preguntas Realizadas")
        for pregunta in st.session_state.preguntas_realizadas:
            st.markdown(f"~~{pregunta}~~")

    def mostrar_estadisticas(self):
        if st.session_state.estudiantes.empty:
            st.warning("No hay datos de estudiantes para mostrar estadísticas")
            return

        # Estadísticas generales
        st.header("Estadísticas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Estudiantes", 
                len(st.session_state.estudiantes)
            )
        
        with col2:
            st.metric(
                "Participaciones Promedio", 
                f"{st.session_state.estudiantes['Participaciones'].mean():.2f}"
            )
        
        with col3:
            st.metric(
                "Puntaje Promedio", 
                f"{st.session_state.estudiantes['Puntaje'].mean():.2f}"
            )

        # Gráficos
        col_grafico1, col_grafico2 = st.columns(2)
        
        with col_grafico1:
            st.subheader("Puntajes por Estudiante")
            fig_puntajes = px.bar(
                st.session_state.estudiantes, 
                x='Nombre', 
                y='Puntaje',
                title='Puntajes de Estudiantes',
                color='Puntaje',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_puntajes)
        
        with col_grafico2:
            st.subheader("Participaciones por Estudiante")
            fig_participaciones = px.bar(
                st.session_state.estudiantes, 
                x='Nombre', 
                y='Participaciones',
                title='Participaciones de Estudiantes',
                color='Participaciones',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_participaciones)

def main():
    app = ControlParticipacion()
    app.mostrar_interfaz()

if __name__ == "__main__":
    main()
