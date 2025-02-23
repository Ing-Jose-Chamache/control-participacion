import streamlit as st
import base64

# Configuración de la página
st.set_page_config(page_title="LOGO IMPONENTE", layout="wide")

# Estilos personalizados
st.markdown("""
    <style>
    .main {
        padding: 0;
        margin: 0;
    }
    .hidden-upload {
        position: absolute;
        top: 10px;
        left: 10px;
        width: 30px;
        height: 30px;
        opacity: 0.2;
        cursor: pointer;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 90vh;
    }
    .logo-container img {
        max-width: 50%;
        max-height: 70vh;
        animation: fadeIn 2s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

# Inicialización de estado
if 'logo' not in st.session_state:
    st.session_state.logo = None

# Cargar logo oculto
logo_file = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
if logo_file is not None:
    st.session_state.logo = base64.b64encode(logo_file.read()).decode()

# Botón oculto
st.markdown('<input type="file" class="hidden-upload" accept="image/png, image/jpeg">', unsafe_allow_html=True)

# Mostrar logo
if st.session_state.logo:
    st.markdown(f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{st.session_state.logo}" alt="Logo Imponente">
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<div class='logo-container'><h1>SUBA SU LOGO</h1></div>", unsafe_allow_html=True)
