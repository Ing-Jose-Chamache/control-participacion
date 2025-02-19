import streamlit as st
import pandas as pd
import plotly.express as px

class ControlParticipacion:
    def __init__(self):
        # Inicializar estado de la sesión
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Nota', 'Puntaje']
            )
        
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []
        
        if 'historial_participaciones' not in st.session_state:
            st.session_state.historial_participaciones = []

    def mostrar_interfaz(self):
        st.title("Control de Participación")

        # Menú de pestañas
        tab1, tab2, tab3, tab4 = st.tabs([
            "Gestión de Estudiantes", 
            "Registrar Participación", 
            "Estadísticas", 
            "Preguntas Planificadas"
        ])

        with tab1:
            self.gestion_estudiantes()

        with tab2:
            self.registrar_participacion()

        with tab3:
            self.mostrar_estadisticas()

        with tab4:
            self.gestion_preguntas()

    def gestion_estudiantes(self):
        # Columnas para entrada de datos
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nombre_estudiante = st.text_input("Nombre del Estudiante")
        
        with col2:
            puntaje_inicial = st.number_input(
                "Puntaje Inicial", 
                min_value=0, 
                step=1,
                value=0
            )
        
        with col3:
            nota_inicial = st.number_input(
                "Nota Inicial", 
                min_value=0.0, 
                max_value=20.0, 
                step=0.5,
                value=0.0
            )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Agregar Estudiante"):
                self.agregar_estudiante(nombre_estudiante, puntaje_inicial, nota_inicial)
        
        with col_btn2:
            archivo_txt = st.file_uploader(
                "Cargar lista de estudiantes", 
                type=['txt', 'csv']
            )
            if archivo_txt is not None:
                self.cargar_archivo(archivo_txt)

        # Mostrar tabla de estudiantes
        st.dataframe(st.session_state.estudiantes)

    def agregar_estudiante(self, nombre, puntaje, nota):
        if nombre and nombre.strip():
            # Verificar si el estudiante ya existe
            if nombre not in st.session_state.estudiantes['Nombre'].values:
                nuevo_estudiante = pd.DataFrame({
                    'Nombre': [nombre],
                    'Participaciones': [0],
                    'Nota': [nota],
                    'Puntaje': [puntaje]
                })
                st.session_state.estudiantes = pd.concat([
                    st.session_state.estudiantes, 
                    nuevo_estudiante
                ], ignore_index=True)
                st.success(f"Estudiante {nombre} agregado exitosamente")
            else:
                st.warning(f"El estudiante {nombre} ya existe en la lista")

    def registrar_participacion(self):
        st.header("Registrar Participación")
        
        # Seleccionar estudiante
        estudiantes = st.session_state.estudiantes['Nombre'].tolist()
        estudiante_seleccionado = st.selectbox("Seleccionar Estudiante", estudiantes)
        
        # Detalles de la participación
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_participacion = st.radio(
                "Tipo de Participación", 
                ["Respuesta Correcta", "Respuesta Incorrecta", "Participación"]
            )
        
        with col2:
            puntos = st.number_input(
                "Puntos", 
                min_value=-5, 
                max_value=5, 
                step=1,
                value=1
            )
        
        # Descripción de la participación
        descripcion = st.text_area("Descripción de la Participación")
        
        # Botón para registrar
        if st.button("Registrar Participación"):
            # Actualizar puntaje y participaciones
            mask = st.session_state.estudiantes['Nombre'] == estudiante_seleccionado
            
            # Incrementar participaciones
            st.session_state.estudiantes.loc[mask, 'Participaciones'] += 1
            
            # Actualizar puntaje
            st.session_state.estudiantes.loc[mask, 'Puntaje'] += puntos
            
            # Registrar en historial
            participacion = {
                'Estudiante': estudiante_seleccionado,
                'Tipo': tipo_participacion,
                'Puntos': puntos,
                'Descripción': descripcion,
                'Fecha': pd.Timestamp.now()
            }
            st.session_state.historial_participaciones.append(participacion)
            
            st.success(f"Participación de {estudiante_seleccionado} registrada")
        
        # Mostrar historial de participaciones
        st.subheader("Historial de Participaciones")
        if st.session_state.historial_participaciones:
            historial_df = pd.DataFrame(st.session_state.historial_participaciones)
            st.dataframe(historial_df)

    def cargar_archivo(self, archivo):
        try:
            # Intentar leer como CSV primero
            df = pd.read_csv(archivo)
            
            # Verificar columnas
            columnas_requeridas = ['Nombre', 'Participaciones', 'Nota', 'Puntaje']
            if all(col in df.columns for col in columnas_requeridas):
                # Concatenar y eliminar duplicados
                st.session_state.estudiantes = pd.concat([
                    st.session_state.estudiantes, 
                    df
                ]).drop_duplicates(subset=['Nombre'], keep='last')
                st.success("Archivo cargado exitosamente")
            else:
                st.error("El archivo debe contener columnas: Nombre, Participaciones, Nota, Puntaje")
        
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")

    def mostrar_estadisticas(self):
        if st.session_state.estudiantes.empty:
            st.warning("No hay datos de estudiantes para mostrar estadísticas")
            return

        # Estadísticas generales
        st.header("Estadísticas Generales")
        
        col1, col2, col3, col4 = st.columns(4)
        
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
        
        with col4:
            st.metric(
                "Nota Promedio", 
                f"{st.session_state.estudiantes['Nota'].mean():.2f}"
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

    def gestion_preguntas(self):
        # Entrada de preguntas
        nueva_pregunta = st.text_area("Escribe una nueva pregunta")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Agregar Pregunta"):
                if nueva_pregunta:
                    st.session_state.preguntas.append(nueva_pregunta)
                    st.success("Pregunta agregada exitosamente")
        
        with col2:
            if st.button("Limpiar Preguntas"):
                st.session_state.preguntas = []
                st.success("Preguntas eliminadas")
        
        # Mostrar preguntas
        st.subheader("Preguntas Actuales:")
        for i, pregunta in enumerate(st.session_state.preguntas, 1):
            st.write(f"{i}. {pregunta}")
            # Botón para eliminar pregunta individual
            if st.button(f"Eliminar Pregunta {i}"):
                del st.session_state.preguntas[i-1]
                st.experimental_rerun()

def main():
    app = ControlParticipacion()
    app.mostrar_interfaz()

if __name__ == "__main__":
    main()
