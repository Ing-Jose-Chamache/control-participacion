import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="Presentación de Preguntas", layout="wide")

# Configuración de estilos
st.markdown("""
    <style>
    .css-1v0mbdj.etr89bj1 { display: none; }
    .css-10trblm.e16nr0p30 { text-align: center; }
    .stButton > button {
        background-color: #3498db;
        color: white;
        border-radius: 20px;
        padding: 10px 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Crear dos columnas
col1, col2 = st.columns(2)

# Panel izquierdo para el logo
with col1:
    st.markdown("""
        <div style='background-color: #34495e; padding: 20px; border-radius: 10px; text-align: center;'>
        """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, width=300)
    st.markdown("</div>", unsafe_allow_html=True)

# Panel derecho para las preguntas
with col2:
    st.markdown("""
        <div style='background-color: white; padding: 20px; border-radius: 10px; min-height: 400px;'>
        """, unsafe_allow_html=True)
    
    uploaded_txt = st.file_uploader("", type=["txt"], key="txt_uploader")
    
    if uploaded_txt is not None:
        preguntas = uploaded_txt.getvalue().decode().split('\n')
        preguntas = [p.strip() for p in preguntas if p.strip()]
        
        if 'pregunta_actual' not in st.session_state:
            st.session_state.pregunta_actual = 0
            
        if preguntas:
            # Mostrar pregunta actual
            st.markdown(f"""
                <h1 style='text-align: center; color: #2c3e50; font-size: 2em;'>
                {preguntas[st.session_state.pregunta_actual]}
                </h1>
            """, unsafe_allow_html=True)
            
            # Botones de navegación
            col_nav1, col_counter, col_nav2 = st.columns([1,2,1])
            
            with col_nav1:
                if st.button("←") and st.session_state.pregunta_actual > 0:
                    st.session_state.pregunta_actual -= 1
                    st.experimental_rerun()
                    
            with col_counter:
                st.markdown(f"""
                    <p style='text-align: center;'>
                    {st.session_state.pregunta_actual + 1} / {len(preguntas)}
                    </p>
                """, unsafe_allow_html=True)
                
            with col_nav2:
                if st.button("→") and st.session_state.pregunta_actual < len(preguntas) - 1:
                    st.session_state.pregunta_actual += 1
                    st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
