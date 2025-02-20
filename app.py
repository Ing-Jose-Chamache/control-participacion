def generar_reporte_pdf(self):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        elements.append(Paragraph("REPORTE DE PARTICIPACIONES", title_style))
        elements.append(Spacer(1, 20))
        
        # Fecha
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        elements.append(Paragraph(f"Fecha: {fecha}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Datos de estudiantes
        elements.append(Paragraph("Lista de Estudiantes", styles['Heading2']))
        if not st.session_state.estudiantes.empty:
            data = [['Nombre', 'Participaciones', 'Puntaje']]
            for _, row in st.session_state.estudiantes.iterrows():
                data.append([
                    row['Nombre'],
                    f"{row['Participaciones']}/{st.session_state.participaciones_esperadas}",
                    f"{row['Puntaje']:.1f}"
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))
        
        # Preguntas
        elements.append(Paragraph("Preguntas Planificadas", styles['Heading2']))
        if st.session_state.preguntas:
            for i, pregunta in enumerate(st.session_state.preguntas, 1):
                status = "✓" if i-1 in st.session_state.preguntas_completadas else "○"
                elements.append(Paragraph(
                    f"{i}. {pregunta} [{status}]",
                    styles['Normal']
                ))
                elements.append(Spacer(1, 5))
        
        # Pie de página
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(
            "Generado por: Control de Participación",
            styles['Normal']
        ))
        
        # Construir PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdfimport streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import StringIO, BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

# Resto de las importaciones...

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
    .logo-upload {
        width: 100px !important;
        position: fixed;
        top: 10px;
        left: 10px;
    }
    .question-completed {
        text-decoration: line-through;
        font-weight: bold;
        color: #6c757d;
    }
    .student-row {
        padding: 5px;
        margin-bottom: 5px;
        border-bottom: 1px solid #eee;
    }
    .question-box {
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
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
        col1, col2, col3 = st.columns([1, 4, 1])
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
                # Actualizar todos los puntajes
                for idx in st.session_state.estudiantes.index:
                    participaciones = st.session_state.estudiantes.at[idx, 'Participaciones']
                    st.session_state.estudiantes.at[idx, 'Puntaje'] = min(
                        20, (participaciones / st.session_state.participaciones_esperadas) * 20
                    )

        # Agregar estudiantes manualmente
        col1, col2 = st.columns([3, 1])
        with col1:
            nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE")
        with col2:
            if st.button("AGREGAR ESTUDIANTE") and nuevo_estudiante:
                if nuevo_estudiante not in st.session_state.estudiantes['Nombre'].values:
                    nuevo_df = pd.DataFrame({
                        'Nombre': [nuevo_estudiante],
                        'Participaciones': [0],
                        'Puntaje': [0]
                    })
                    st.session_state.estudiantes = pd.concat([
                        st.session_state.estudiantes, nuevo_df
                    ], ignore_index=True)

        # Cargar estudiantes desde archivo
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
                    st.session_state.estudiantes = pd.concat([
                        st.session_state.estudiantes, nuevo_df
                    ], ignore_index=True)

        # Mostrar y gestionar estudiantes
        for idx in st.session_state.estudiantes.index:
            with st.container():
                cols = st.columns([2, 2, 1, 1, 1])
                with cols[0]:
                    st.write(f"**{st.session_state.estudiantes.at[idx, 'Nombre']}**")
                with cols[1]:
                    st.write(f"Participaciones: {st.session_state.estudiantes.at[idx, 'Participaciones']}/{st.session_state.participaciones_esperadas} | Nota: {st.session_state.estudiantes.at[idx, 'Puntaje']:.1f}")
                with cols[2]:
                    if st.button("+1", key=f"plus_{idx}"):
                        participaciones = st.session_state.estudiantes.at[idx, 'Participaciones'] + 1
                        st.session_state.estudiantes.at[idx, 'Participaciones'] = participaciones
                        st.session_state.estudiantes.at[idx, 'Puntaje'] = min(
                            20, (participaciones / st.session_state.participaciones_esperadas) * 20
                        )
                        st.rerun()
                with cols[3]:
                    if st.button("-1", key=f"minus_{idx}"):
                        if st.session_state.estudiantes.at[idx, 'Participaciones'] > 0:
                            participaciones = st.session_state.estudiantes.at[idx, 'Participaciones'] - 1
                            st.session_state.estudiantes.at[idx, 'Participaciones'] = participaciones
                            st.session_state.estudiantes.at[idx, 'Puntaje'] = min(
                                20, (participaciones / st.session_state.participaciones_esperadas) * 20
                            )
                            st.rerun()
                with cols[4]:
                    if st.button("❌", key=f"delete_{idx}"):
                        st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)
                        st.rerun()

        # Botón para eliminar todos los estudiantes
        if not st.session_state.estudiantes.empty:
            if st.button("ELIMINAR TODOS LOS ESTUDIANTES"):
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
        
        # Agregar pregunta manualmente
        col1, col2 = st.columns([3, 1])
        with col1:
            nueva_pregunta = st.text_input("ESCRIBA UNA NUEVA PREGUNTA")
        with col2:
            if st.button("AGREGAR PREGUNTA") and nueva_pregunta:
                st.session_state.preguntas.append(nueva_pregunta)
                st.rerun()

        # Mostrar y gestionar preguntas
        for i, pregunta in enumerate(st.session_state.preguntas):
            with st.container():
                cols = st.columns([3, 1, 1])
                with cols[0]:
                    if i in st.session_state.preguntas_completadas:
                        st.markdown(f"<p style='text-decoration: line-through; font-weight: bold; color: #6c757d;'>{i+1}. {pregunta}</p>", unsafe_allow_html=True)
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

        # Botón para eliminar todas las preguntas
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
            pdf = self.generar_reporte_pdf()
            st.download_button(
                label="⬇️ DESCARGAR REPORTE",
                data=pdf,
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
