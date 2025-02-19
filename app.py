import streamlit as st
import pandas as pd
import plotly.express as px
import os

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
        
        if 'historial_participaciones' not in st.session_state:
            st.session_state.historial_participaciones = []

    def cargar_estudiantes_desde_txt(self, archivo):
        """Cargar estudiantes desde un archivo de texto plano"""
        try:
            # Leer nombres de estudiantes
            nombres = archivo.getvalue().decode('utf-8').splitlines()
            
            # Filtrar nombres no vacíos
            nombres = [nombre.strip() for nombre in nombres if nombre.strip()]
            
            # Agregar estudiantes
            for nombre in nombres:
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
            
            st.success(f"Se cargaron {len(nombres)} estudiantes")
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")

    def cargar_preguntas_desde_txt(self, archivo):
        """Cargar preguntas desde un archivo de texto plano"""
        try:
            # Leer preguntas
            preguntas = archivo.getvalue().decode('utf-8').splitlines()
            
            # Filtrar preguntas no vacías
            preguntas = [pregunta.strip() for pregunta in preguntas if pregunta.strip()]
            
            # Agregar preguntas
            st.session_state.preguntas = preguntas
            st.success(f"Se cargaron {len(preguntas)} preguntas")
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")

    def mostrar_interfaz(self):
        # Configuración de página
        st.set_page_config(page_title="Control de Participación", page_icon="📊")
        
        # Logo (si existe)
        logo_path = 'logo.jpg'  # Puedes cambiar la extensión
        if os.path.exists(logo_path):
            st.sidebar.image(logo_path, use_column_width=True)

        # Título principal
        st.title("Control de Participación")

        # Menú de pestañas
        tab1, tab2, tab3 = st.tabs([
            "Gestión de Estudiantes", 
            "Preguntas y Participación", 
            "Estadísticas"
        ])

        with tab1:
            self.gestion_estudiantes()

        with tab2:
            self.gestion_preguntas_participacion()

        with tab3:
            self.mostrar_estadisticas()

    def gestion_estudiantes(self):
        # Cargar archivo de estudiantes
        st.subheader("Cargar Estudiantes")
        archivo_estudiantes = st.file_uploader(
            "Cargar lista de estudiantes (txt)", 
            type=['txt']
        )
        if archivo_estudiantes is not None:
            self.cargar_estudiantes_desde_txt(archivo_estudiantes)

        # Mostrar y gestionar estudiantes
        st.subheader("Lista de Estudiantes")
        if not st.session_state.estudiantes.empty:
            # Crear una copia modificable del DataFrame
            df_editado = st.session_state.estudiantes.copy()
            
            # Crear columnas para cada estudiante
            for i, estudiante in df_editado.iterrows():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(estudiante['Nombre'])
                
                with col2:
                    st.write(f"Participaciones: {estudiante['Participaciones']}")
                
                with col3:
                    st.write(f"Puntaje: {estudiante['Puntaje']}")
                
                with col4:
                    # Botones para ajustar puntaje
                    col_sumar, col_restar = st.columns(2)
                    with col_sumar:
                        if st.button(f"+1 a {estudiante['Nombre']}", key=f"sumar_{i}"):
                            st.session_state.estudiantes.loc[i, 'Puntaje'] += 1
                            st.session_state.estudiantes.loc[i, 'Participaciones'] += 1
                            st.experimental_rerun()
                    
                    with col_restar:
                        if st.button(f"-1 a {estudiante['Nombre']}", key=f"restar_{i}"):
                            st.session_state.estudiantes.loc[i, 'Puntaje'] -= 1
                            st.experimental_rerun()

    def gestion_preguntas_participacion(self):
        # Cargar archivo de preguntas
        st.subheader("Cargar Preguntas")
        archivo_preguntas = st.file_uploader(
            "Cargar lista de preguntas (txt)", 
            type=['txt']
        )
        if archivo_preguntas is not None:
            self.cargar_preguntas_desde_txt(archivo_preguntas)

        # Gestión de preguntas
        st.subheader("Preguntas Pendientes")
        for i, pregunta in enumerate(st.session_state.preguntas):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(pregunta)
            
            with col2:
                # Botón para marcar pregunta como realizada
                if st.button(f"Realizada {i+1}", key=f"realizada_{i}"):
                    # Mover pregunta a preguntas realizadas
                    st.session_state.preguntas_realizadas.append(pregunta)
                    # Eliminar de preguntas pendientes
                    del st.session_state.preguntas[i]
                    st.experimental_rerun()

        # Preguntas realizadas
        st.subheader("Preguntas Realizadas")
        for pregunta in st.session_state.preguntas_realizadas:
            st.write(f"~~{pregunta}~~")

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
                title='Puntajes de Estudiantes'
            )
            st.plotly_chart(fig_puntajes)
        
        with col_grafico2:
            st.subheader("Participaciones por Estudiante")
            fig_participaciones = px.bar(
                st.session_state.estudiantes, 
                x='Nombre', 
                y='Participaciones',
                title='Participaciones de Estudiantes'
            )
            st.plotly_chart(fig_participaciones)

        # Tabla de mejores estudiantes
        st.subheader("Top Estudiantes")
        mejores_estudiantes = st.session_state.estudiantes.sort_values(
            by=['Puntaje', 'Participaciones'], 
            ascending=False
        ).head(5)
        st.dataframe(mejores_estudiantes)

def main():
    app = ControlParticipacion()
    app.mostrar_interfaz()

if __name__ == "__main__":
    main()

# Nota: Para el logo, coloca un archivo llamado logo.jpg o logo.bmp 
# en el mismo directorio que el script
