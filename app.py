import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
from io import StringIO

# Configuración de la página
st.set_page_config(page_title="CONTROL DE PARTICIPACIÓN", layout="wide")

# Estilos CSS
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
        margin-top: 1rem;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 1rem;
    }
    .logo-button {
        position: absolute;
        top: 10px;
        left: 10px;
        width: 100px;
    }
    .student-row {
        background-color: #ffffff;
        padding: 8px;
        border-radius: 5px;
        margin-bottom: 5px;
        border: 1px solid #dee2e6;
        font-size: 0.9em;
    }
    .question-box {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .question-completed {
        text-decoration: line-through;
        font-weight: bold;
        color: #6c757d;
        background-color: #e9ecef;
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
        # Inicializar estados si no existen
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
        # Botón simple para cargar logo
        if st.button("📷 LOGO", key="btn_logo"):
            file = st.file_uploader("", type=['png', 'jpg', 'jpeg'])
            if file is not None:
                st.session_state.logo = base64.b64encode(file.read()).decode()

    def mostrar_header(self):
        # Mostrar logo si existe
        if st.session_state.logo:
            st.markdown(f"""
                <div class="logo-container">
                    <img src="data:image/png;base64,{st.session_state.logo}" width="300"/>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<h1 class='title'>CONTROL DE PARTICIPACIÓN</h1>", unsafe_allow_html=True)

    def agregar_estudiante(self):
        col1, col2 = st.columns([3, 1])
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
                        st.success("Estudiante agregado con éxito")
                    else:
                        st.info("Este estudiante ya existe")

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

        for idx, estudiante in st.session_state.estudiantes.iterrows():
            with st.container():
                cols = st.columns([2, 2, 1, 1, 1])
                
                with cols[0]:
                    st.markdown(f"**{estudiante['Nombre']}**")
                
                with cols[1]:
                    st.write(f"Part: {estudiante['Participaciones']}/{st.session_state.participaciones_esperadas} | Nota: {estudiante['Puntaje']:.1f}")
                
                with cols[2]:
                    if st.button("+1", key=f"plus_{idx}"):
                        participaciones = estudiante['Participaciones'] + 1
                        st.session_state.estudiantes.at[idx, 'Participaciones'] = participaciones
                        st.session_state.estudiantes.at[idx, 'Puntaje'] = min(
                            20, (participaciones / st.session_state.participaciones_esperadas) * 20
                        )
                
                with cols[3]:
                    if st.button("-1", key=f"minus_{idx}"):
                        if estudiante['Participaciones'] > 0:
                            participaciones = estudiante['Participaciones'] - 1
                            st.session_state.estudiantes.at[idx, 'Participaciones'] = participaciones
                            st.session_state.estudiantes.at[idx, 'Puntaje'] = min(
                                20, (participaciones / st.session_state.participaciones_esperadas) * 20
                            )
                
                with cols[4]:
                    if st.button("❌", key=f"delete_{idx}"):
                        st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)

        # Sección para cargar estudiantes desde archivo
        col1, col2 = st.columns(2)
        with col1:
            if st.button("ELIMINAR TODOS LOS ESTUDIANTES"):
                st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Participaciones', 'Puntaje'])
                st.success("Lista de estudiantes eliminada")
        
        with col2:
            uploaded_file = st.file_uploader("CARGAR LISTA DE ESTUDIANTES", type=['txt'])
            if uploaded_file:
                contenido = StringIO(uploaded_file.getvalue().decode("utf-8")).read().splitlines()
                for estudiante in contenido:
                    if estudiante.strip() and estudiante not in st.session_state.estudiantes['Nombre'].values:
                        nuevo_df = pd.DataFrame({
                            'Nombre': [estudiante.strip()],
                            'Participaciones': [0],
                            'Puntaje': [0]
                        })
                        st.session_state.estudiantes = pd.concat(
                            [st.session_state.estudiantes, nuevo_df],
                            ignore_index=True
                        )
                st.success("Estudiantes cargados exitosamente")

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
                fig_bar.update_layout(title_x=0.5, title_font_size=20)
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
                    fig_pie.update_layout(title_x=0.5, title_font_size=20)
                    st.plotly_chart(fig_pie, use_container_width=True)

    def gestionar_preguntas(self):
        st.markdown("### PREGUNTAS PLANIFICADAS")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            nueva_pregunta = st.text_input("ESCRIBA UNA NUEVA PREGUNTA")
            if nueva_pregunta and st.button("AGREGAR PREGUNTA"):
                st.session_state.preguntas.append(nueva_pregunta)
                st.success("Pregunta agregada exitosamente")
        
        with col2:
            uploaded_file = st.file_uploader("CARGAR PREGUNTAS", type=['txt'])
            if uploaded_file:
                contenido = StringIO(uploaded_file.getvalue().decode("utf-8")).read().splitlines()
                st.session_state.preguntas.extend([p.strip() for p in contenido if p.strip()])
                st.success("Preguntas cargadas exitosamente")

        for i, pregunta in enumerate(st.session_state.preguntas):
            with st.container():
                esta_completada = i in st.session_state.preguntas_completadas
                cols = st.columns([3, 1, 1])
                
                with cols[0]:
                    if esta_completada:
                        st.markdown(f"~~**{i+1}. {pregunta}**~~")
                    else:
                        st.write(f"{i+1}. {pregunta}")
                
                with cols[1]:
                    if st.button("✓" if not esta_completada else "↩", key=f"complete_{i}"):
                        if esta_completada:
                            st.session_state.preguntas_completadas.remove(i)
                        else:
                            st.session_state.preguntas_completadas.add(i)
                
                with cols[2]:
                    if st.button("❌", key=f"delete_pregunta_{i}"):
                        st.session_state.preguntas.pop(i)
                        if i in st.session_state.preguntas_completadas:
                            st.session_state.preguntas_completadas.remove(i)

        if st.session_state.preguntas:
            if st.button("ELIMINAR TODAS LAS PREGUNTAS"):
                st.session_state.preguntas = []
                st.session_state.preguntas_completadas = set()
                st.success("Todas las preguntas han sido eliminadas")

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
