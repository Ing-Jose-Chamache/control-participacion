import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import StringIO
from fpdf import FPDF
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="CONTROL DE PARTICIPACIÓN", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .title {
        text-transform: uppercase;
        text-align: center;
        font-weight: bold;
        font-size: 2.5em;
    }
    .student-row {
        padding: 5px;
        margin-bottom: 5px;
        border-bottom: 1px solid #eee;
    }
    .question-completed {
        text-decoration: line-through;
        font-weight: bold;
        color: #6c757d;
    }
    </style>
""", unsafe_allow_html=True)

class ControlParticipacion:
    def __init__(self):
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Participaciones', 'Puntaje'])
        if 'participaciones_esperadas' not in st.session_state:
            st.session_state.participaciones_esperadas = 5
        if 'preguntas' not in st.session_state:
            st.session_state.preguntas = []
        if 'preguntas_completadas' not in st.session_state:
            st.session_state.preguntas_completadas = set()
        if 'logo' not in st.session_state:
            st.session_state.logo = None

    def cargar_logo(self):
        col1, col2, col3 = st.columns([1, 8, 1])
        with col1:
            uploaded_file = st.file_uploader("LOGO", type=['png', 'jpg', 'jpeg'])
            if uploaded_file is not None:
                st.session_state.logo = base64.b64encode(uploaded_file.getvalue()).decode()

    def mostrar_header(self):
        if st.session_state.logo:
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 1rem;">
                    <img src="data:image/png;base64,{st.session_state.logo}" width="300"/>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("<h1 class='title'>CONTROL DE PARTICIPACIÓN</h1>", unsafe_allow_html=True)

    def generar_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        
        # Configuración
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(190, 10, 'REPORTE DE PARTICIPACIONES', 0, 1, 'C')
        pdf.ln(10)
        
        # Fecha
        pdf.set_font('Arial', '', 12)
        pdf.cell(190, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1)
        pdf.ln(10)
        
        # Lista de estudiantes
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(190, 10, 'Lista de Estudiantes', 0, 1)
        pdf.ln(5)
        
        # Encabezados de tabla
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(70, 10, 'Nombre', 1)
        pdf.cell(60, 10, 'Participaciones', 1)
        pdf.cell(60, 10, 'Puntaje', 1)
        pdf.ln()
        
        # Datos de estudiantes
        pdf.set_font('Arial', '', 12)
        for _, estudiante in st.session_state.estudiantes.iterrows():
            pdf.cell(70, 10, estudiante['Nombre'], 1)
            pdf.cell(60, 10, f"{estudiante['Participaciones']}/{st.session_state.participaciones_esperadas}", 1)
            pdf.cell(60, 10, f"{estudiante['Puntaje']:.1f}", 1)
            pdf.ln()
        
        pdf.ln(10)
        
        # Lista de preguntas
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(190, 10, 'Preguntas Planificadas', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        for i, pregunta in enumerate(st.session_state.preguntas, 1):
            status = "✓" if i-1 in st.session_state.preguntas_completadas else "○"
            pdf.multi_cell(190, 10, f"{i}. {pregunta} [{status}]", 0)
        
        return pdf.output(dest='S').encode('latin1')

    def mostrar_estudiantes(self):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### GESTIÓN DE ESTUDIANTES")
        with col2:
            participaciones = st.number_input(
                "PARTICIPACIONES ESPERADAS",
                min_value=1,
                value=st.session_state.participaciones_esperadas
            )
            if participaciones != st.session_state.participaciones_esperadas:
                st.session_state.participaciones_esperadas = participaciones
                for idx in st.session_state.estudiantes.index:
                    part = st.session_state.estudiantes.at[idx, 'Participaciones']
                    st.session_state.estudiantes.at[idx, 'Puntaje'] = (part / participaciones) * 20
                st.rerun()

        # Agregar estudiante
        col1, col2 = st.columns([3, 1])
        with col1:
            nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE")
        with col2:
            if st.button("AGREGAR") and nuevo_estudiante:
                if nuevo_estudiante not in st.session_state.estudiantes['Nombre'].values:
                    nuevo_df = pd.DataFrame({
                        'Nombre': [nuevo_estudiante],
                        'Participaciones': [0],
                        'Puntaje': [0]
                    })
                    st.session_state.estudiantes = pd.concat([
                        st.session_state.estudiantes, nuevo_df
                    ], ignore_index=True)

        # Lista de estudiantes
        for idx in st.session_state.estudiantes.index:
            cols = st.columns([2, 2, 1, 1, 1])
            with cols[0]:
                st.write(f"**{st.session_state.estudiantes.at[idx, 'Nombre']}**")
            with cols[1]:
                st.write(f"Participaciones: {st.session_state.estudiantes.at[idx, 'Participaciones']}/{st.session_state.participaciones_esperadas} | Nota: {st.session_state.estudiantes.at[idx, 'Puntaje']:.1f}")
            with cols[2]:
                if st.button("+1", key=f"plus_{idx}"):
                    st.session_state.estudiantes.at[idx, 'Participaciones'] += 1
                    part = st.session_state.estudiantes.at[idx, 'Participaciones']
                    st.session_state.estudiantes.at[idx, 'Puntaje'] = (part / st.session_state.participaciones_esperadas) * 20
                    st.rerun()
            with cols[3]:
                if st.button("-1", key=f"minus_{idx}"):
                    if st.session_state.estudiantes.at[idx, 'Participaciones'] > 0:
                        st.session_state.estudiantes.at[idx, 'Participaciones'] -= 1
                        part = st.session_state.estudiantes.at[idx, 'Participaciones']
                        st.session_state.estudiantes.at[idx, 'Puntaje'] = (part / st.session_state.participaciones_esperadas) * 20
                        st.rerun()
            with cols[4]:
                if st.button("❌", key=f"delete_{idx}"):
                    st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)
                    st.rerun()

        # Eliminar todos
        if not st.session_state.estudiantes.empty:
            if st.button("❌ ELIMINAR TODOS LOS ESTUDIANTES", type="primary"):
                st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Participaciones', 'Puntaje'])
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
                fig_bar.update_layout(title_x=0.5)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                total_participaciones = st.session_state.estudiantes['Participaciones'].sum()
                if total_participaciones > 0:
                    datos_torta = st.session_state.estudiantes.copy()
                    datos_torta['Porcentaje'] = (datos_torta['Participaciones'] / total_participaciones * 100)
                    fig_pie = px.pie(
                        datos_torta,
                        values='Porcentaje',
                        names='Nombre',
                        title='DISTRIBUCIÓN DE PARTICIPACIONES (%)'
                    )
                    fig_pie.update_layout(title_x=0.5)
                    st.plotly_chart(fig_pie, use_container_width=True)

    def gestionar_preguntas(self):
        st.markdown("### PREGUNTAS PLANIFICADAS")
        
        # Agregar pregunta
        col1, col2 = st.columns([3, 1])
        with col1:
            nueva_pregunta = st.text_input("ESCRIBA UNA NUEVA PREGUNTA")
        with col2:
            if st.button("AGREGAR PREGUNTA") and nueva_pregunta:
                st.session_state.preguntas.append(nueva_pregunta)
                st.rerun()

        # Cargar preguntas
        uploaded_file = st.file_uploader("CARGAR PREGUNTAS", type=['txt'])
        if uploaded_file:
            contenido = StringIO(uploaded_file.getvalue().decode("utf-8")).read().splitlines()
            for pregunta in contenido:
                if pregunta.strip():
                    st.session_state.preguntas.append(pregunta.strip())
            st.rerun()

        # Lista de preguntas
        for i, pregunta in enumerate(st.session_state.preguntas):
            cols = st.columns([3, 1, 1])
            with cols[0]:
                if i in st.session_state.preguntas_completadas:
                    st.markdown(f"<p style='text-decoration: line-through; font-weight: bold;'>{i+1}. {pregunta}</p>", unsafe_allow_html=True)
                else:
                    st.write(f"{i+1}. {pregunta}")
            with cols[1]:
                if st.button("✓" if i not in st.session_state.preguntas_completadas else "↩", key=f"complete_{i}"):
                    if i in st.session_state.preguntas_completadas:
                        st.session_state.preguntas_completadas.remove(i)
                    else:
                        st.session_state.preguntas_completadas.add(i)
                    st.rerun()
            with cols[2]:
                if st.button("❌", key=f"delete_pregunta_{i}"):
                    st.session_state.preguntas.pop(i)
                    st.session_state.preguntas_completadas = {
                        x if x < i else x - 1 for x in st.session_state.preguntas_completadas if x != i
                    }
                    st.rerun()

        # Eliminar todas las preguntas
        if st.session_state.preguntas:
            if st.button("❌ ELIMINAR TODAS LAS PREGUNTAS", type="primary"):
                st.session_state.preguntas = []
                st.session_state.preguntas_completadas = set()
                st.rerun()

    def run(self):
        self.cargar_logo()
        self.mostrar_header()
        self.mostrar_estudiantes()
        self.mostrar_graficos()
        st.markdown("---")
        self.gestionar_preguntas()
        
        # Botón para descargar reporte
        if st.button("📄 DESCARGAR REPORTE PDF"):
            pdf_data = self.generar_pdf()
            st.download_button(
                label="⬇️ DESCARGAR PDF",
                data=pdf_data,
                file_name=f"reporte_participaciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
        
        st.markdown("""
            <div style="text-align: center; padding: 20px; margin-top: 30px;">
                <h3>Desarrollado por:</h3>
                <p><strong>Ing. José Yván Chamache Chiong</strong></p>
                <p>Lima, Perú - 2024</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    app = ControlParticipacion()
    app.run()
