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
    }
    .logo-container {
        position: absolute;
        left: 10px;
        top: 10px;
        width: 100px;
    }
    </style>
""", unsafe_allow_html=True)

class ControlParticipacion:
    def __init__(self):
        # Inicializar estados de sesión
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Puntaje']
            )
        
        if 'participaciones_esperadas' not in st.session_state:
            st.session_state.participaciones_esperadas = 10
            
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []
            
        if 'logo' not in st.session_state:
            st.session_state.logo = None

    def cargar_logo(self):
        col1, col2, col3 = st.columns([1, 8, 1])
        with col1:
            logo_file = st.file_uploader("LOGO", type=['png', 'jpg', 'jpeg'])
            if logo_file is not None:
                st.session_state.logo = base64.b64encode(logo_file.read()).decode()

    def mostrar_header(self):
        if st.session_state.logo:
            st.markdown(f"""
                <div class="logo-container">
                    <img src="data:image/png;base64,{st.session_state.logo}" width="80"/>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<h1 class='title'>CONTROL DE PARTICIPACIÓN</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### GESTIÓN DE ESTUDIANTES")
        with col2:
            st.session_state.participaciones_esperadas = st.number_input(
                "PARTICIPACIONES ESPERADAS",
                min_value=1,
                value=st.session_state.participaciones_esperadas
            )

    def cargar_archivo_txt(self, tipo):
        archivo = st.file_uploader(f"CARGAR ARCHIVO {tipo.upper()}", type=['txt'])
        if archivo is not None:
            try:
                contenido = StringIO(archivo.getvalue().decode("utf-8")).read().splitlines()
                contenido = [linea.strip() for linea in contenido if linea.strip()]
                
                if tipo == "estudiantes":
                    nuevos_estudiantes = []
                    for estudiante in contenido:
                        if estudiante not in st.session_state.estudiantes['Nombre'].values:
                            nuevos_estudiantes.append({
                                'Nombre': estudiante,
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
                
                elif tipo == "preguntas":
                    st.session_state.preguntas.extend(contenido)
                    st.success("Preguntas cargadas exitosamente")
            except Exception as e:
                st.error(f"Error al cargar el archivo: {str(e)}")

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
        if not st.session_state.estudiantes.empty:
            st.dataframe(
                st.session_state.estudiantes,
                column_config={
                    "Nombre": "ESTUDIANTE",
                    "Participaciones": st.column_config.NumberColumn(
                        "PARTICIPACIONES",
                        format="%d/%d" % (0, st.session_state.participaciones_esperadas)
                    ),
                    "Puntaje": st.column_config.NumberColumn(
                        "NOTA",
                        format="%.1f"
                    )
                },
                hide_index=True
            )

            for _, estudiante in st.session_state.estudiantes.iterrows():
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("+1", key=f"plus_{estudiante['Nombre']}"):
                        idx = st.session_state.estudiantes[st.session_state.estudiantes['Nombre'] == estudiante['Nombre']].index[0]
                        st.session_state.estudiantes.loc[idx, 'Participaciones'] += 1
                        st.session_state.estudiantes.loc[idx, 'Puntaje'] = min(
                            20,
                            (st.session_state.estudiantes.loc[idx, 'Participaciones'] / 
                             st.session_state.participaciones_esperadas) * 20
                        )
                with col2:
                    if st.button("-1", key=f"minus_{estudiante['Nombre']}"):
                        idx = st.session_state.estudiantes[st.session_state.estudiantes['Nombre'] == estudiante['Nombre']].index[0]
                        if st.session_state.estudiantes.loc[idx, 'Participaciones'] > 0:
                            st.session_state.estudiantes.loc[idx, 'Participaciones'] -= 1
                            st.session_state.estudiantes.loc[idx, 'Puntaje'] = min(
                                20,
                                (st.session_state.estudiantes.loc[idx, 'Participaciones'] / 
                                 st.session_state.participaciones_esperadas) * 20
                            )

    def mostrar_graficos(self):
        if not st.session_state.estudiantes.empty:
            col1, col2 = st.columns(2)
            
            # Gráfico de barras
            with col1:
                fig_bar = px.bar(
                    st.session_state.estudiantes,
                    x='Nombre',
                    y='Participaciones',
                    title='PARTICIPACIONES POR ESTUDIANTE'
                )
                fig_bar.update_layout(
                    title_x=0.5,
                    title_font_size=20
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Gráfico de torta
            with col2:
                datos_torta = st.session_state.estudiantes.copy()
                total_participaciones = datos_torta['Participaciones'].sum()
                if total_participaciones > 0:
                    datos_torta['Porcentaje'] = (datos_torta['Participaciones'] / total_participaciones * 100)
                    
                    fig_pie = px.pie(
                        datos_torta,
                        values='Porcentaje',
                        names='Nombre',
                        title='DISTRIBUCIÓN DE PARTICIPACIONES (%)'
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

        if st.session_state.preguntas:
            for i, pregunta in enumerate(st.session_state.preguntas, 1):
                st.write(f"{i}. {pregunta}")

        if st.button("LIMPIAR PREGUNTAS"):
            st.session_state.preguntas = []

    def run(self):
        self.cargar_logo()
        self.mostrar_header()
        self.agregar_estudiante()
        st.markdown("---")
        self.mostrar_estudiantes()
        self.mostrar_graficos()
        st.markdown("---")
        self.gestionar_preguntas()

# Iniciar la aplicación
if __name__ == "__main__":
    app = ControlParticipacion()
    app.run()
