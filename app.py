import streamlit as st
import pandas as pd

class ControlParticipacion:
    def __init__(self):
        # Inicializar estado de la sesión si no existe
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Nota']
            )
        
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []

    def mostrar_interfaz(self):
        st.title("Control de Participación")

        # Sección de Estudiantes
        st.header("Gestión de Estudiantes")
        
        # Columnas para entrada de datos
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_estudiante = st.text_input("Nombre del Estudiante")
        
        with col2:
            if st.button("Agregar Estudiante"):
                self.agregar_estudiante(nombre_estudiante)

        # Subir archivo de texto
        archivo_txt = st.file_uploader("Cargar lista de estudiantes", type=['txt'])
        if archivo_txt is not None:
            # Leer archivo de texto
            contenido = archivo_txt.getvalue().decode('utf-8')
            nombres = contenido.split('\n')
            for nombre in nombres:
                nombre = nombre.strip()
                if nombre:
                    self.agregar_estudiante(nombre)

        # Mostrar tabla de estudiantes
        st.dataframe(st.session_state.estudiantes)

        # Sección de Preguntas
        st.header("Preguntas Planificadas")
        
        # Entrada de preguntas
        nueva_pregunta = st.text_area("Escribe una nueva pregunta")
        
        if st.button("Agregar Pregunta"):
            if nueva_pregunta:
                st.session_state.preguntas.append(nueva_pregunta)
        
        # Mostrar preguntas
        st.subheader("Preguntas Actuales:")
        for i, pregunta in enumerate(st.session_state.preguntas, 1):
            st.write(f"{i}. {pregunta}")
        
        # Botón para limpiar preguntas
        if st.button("Limpiar Preguntas"):
            st.session_state.preguntas = []
            st.experimental_rerun()

    def agregar_estudiante(self, nombre):
        if nombre and nombre.strip():
            # Verificar si el estudiante ya existe
            if nombre not in st.session_state.estudiantes['Nombre'].values:
                nuevo_estudiante = pd.DataFrame({
                    'Nombre': [nombre],
                    'Participaciones': [0],
                    'Nota': [0]
                })
                st.session_state.estudiantes = pd.concat([
                    st.session_state.estudiantes, 
                    nuevo_estudiante
                ], ignore_index=True)
            else:
                st.warning(f"El estudiante {nombre} ya existe en la lista")

def main():
    app = ControlParticipacion()
    app.mostrar_interfaz()

if __name__ == "__main__":
    main()

# Instrucciones para ejecutar:
# 1. Instalar Streamlit: pip install streamlit
# 2. Guardar este archivo como app.py
# 3. Ejecutar: streamlit run app.py
# 4. Se abrirá automáticamente en tu navegador predeterminado
