import streamlit as st
import pandas as pd
import plotly.express as px
import base64

class ControlParticipacion:
    def __init__(self):
        # Inicializar estados básicos
        if 'estudiantes' not in st.session_state:
            st.session_state.estudiantes = pd.DataFrame(
                columns=['Nombre', 'Participaciones', 'Puntaje']
            )
        if 'participaciones_esperadas' not in st.session_state:
            st.session_state.participaciones_esperadas = 5
        if 'iconos_estado' not in st.session_state:
            st.session_state.iconos_estado = {}
        if 'logo' not in st.session_state:
            st.session_state.logo = None
        if 'imagenes' not in st.session_state:
            st.session_state.imagenes = []
            st.session_state.imagen_actual = 0

        # Aplicar estilos
        st.markdown("""
            <style>
            /* Ocultar elementos del uploader */
            div[data-testid="stFileUploadDropzone"] > div:not(:first-child),
            div[data-testid="stFileUploadDropzone"] > span,
            div[data-testid="stFileUploadDropzone"] > small,
            .stMarkdown,
            .stAlert,
            div[role="alert"],
            .uploadedFile {
                display: none !important;
            }

            /* Uploader minimalista */
            div[data-testid="stFileUploadDropzone"] {
                width: auto !important;
                min-height: 40px !important;
                padding: 0 !important;
                background: none !important;
                border: none !important;
            }

            /* Estilos para imágenes */
            .imagen-card {
                background-color: #FFF8DC !important;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
                margin: 20px auto;
                max-width: 1200px;
                text-align: center;
                position: relative;
            }

            .imagen-card img {
                max-width: 100%;
                height: auto;
                max-height: 600px;
                object-fit: contain;
                border-radius: 10px;
            }

            .imagen-numero {
                position: absolute;
                top: 15px;
                right: 15px;
                background-color: rgba(0,0,0,0.7);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 16px;
                font-weight: 500;
            }

            /* Estilos generales */
            .stApp {
                background: #f8f9fa !important;
            }

            .student-row {
                background-color: #f8f9fa !important;
                border-bottom: 1px solid #e9ecef;
                margin: 0 !important;
                padding: 15px !important;
            }
            </style>
        """, unsafe_allow_html=True)

    def cargar_logo(self):
        with st.container():
            st.markdown('<div class="logo-upload">', unsafe_allow_html=True)
            logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="logo_upload")
            st.markdown('</div>', unsafe_allow_html=True)
            if logo_file is not None:
                st.session_state.logo = base64.b64encode(logo_file.read()).decode()

    def mostrar_header(self):
        if st.session_state.logo:
            st.markdown(f"""
                <div style="text-align: center; margin: 20px 0;">
                    <img src="data:image/png;base64,{st.session_state.logo}" style="max-width: 400px;"/>
                </div>
            """, unsafe_allow_html=True)

    def cargar_imagenes(self):
        """Carga de imágenes para las preguntas."""
        uploaded_file = st.file_uploader(
            "",
            type=["jpg", "jpeg"],  # Solo permitir JPG
            key="preguntas_img",
            label_visibility="collapsed"
        )

        if uploaded_file:
            try:
                imagen_bytes = uploaded_file.getvalue()
                imagen_b64 = base64.b64encode(imagen_bytes).decode()
                
                # Agregar nueva imagen si no existe
                if imagen_b64 not in [img.get('data') for img in st.session_state.imagenes]:
                    st.session_state.imagenes.append({
                        'data': imagen_b64,
                        'name': uploaded_file.name
                    })
                    st.session_state.imagen_actual = len(st.session_state.imagenes) - 1
            except:
                pass

    def mostrar_imagen_actual(self):
        """Muestra la imagen actual con navegación."""
        if st.session_state.imagenes:
            col1, col2, col3 = st.columns([1, 6, 1])
            
            with col1:
                if st.button("⬅️", 
                           key="prev_img", 
                           disabled=st.session_state.imagen_actual == 0):
                    st.session_state.imagen_actual = max(0, st.session_state.imagen_actual - 1)
            
            with col2:
                total_imagenes = len(st.session_state.imagenes)
                imagen_actual = st.session_state.imagenes[st.session_state.imagen_actual]
                
                st.markdown(f"""
                    <div class="imagen-card">
                        <div class="imagen-numero">{st.session_state.imagen_actual + 1}/{total_imagenes}</div>
                        <img src="data:image/jpeg;base64,{imagen_actual['data']}">
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                if st.button("➡️", 
                           key="next_img", 
                           disabled=st.session_state.imagen_actual >= total_imagenes - 1):
                    st.session_state.imagen_actual = min(total_imagenes - 1, st.session_state.imagen_actual + 1)

    def run(self):
        self.cargar_logo()
        self.mostrar_header()
        
        # Carga y visualización de imágenes
        col1, col2 = st.columns([1, 11])
        with col1:
            self.cargar_imagenes()
        
        # Mostrar imágenes si existen
        if st.session_state.imagenes:
            self.mostrar_imagen_actual()
        
        # Sección principal
        st.markdown("---")
        self.agregar_estudiante()
        self.mostrar_estudiantes()
        self.mostrar_graficos()
        
        # Footer con créditos
        st.markdown("---")
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <h3 style="color: #2c3e50; font-size: 1.5em;">Desarrollado por</h3>
                <p style="color: #34495e; font-size: 1.2em; font-weight: 600;">
                    Ing. José Yván Chamache Chiong
                </p>
                <p style="color: #7f8c8d; font-style: italic;">Lima, Perú - 2024</p>
            </div>
        """, unsafe_allow_html=True)

# Iniciar la aplicación
if __name__ == "__main__":
    app = ControlParticipacion()
    app.run()
