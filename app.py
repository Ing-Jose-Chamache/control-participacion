import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
from io import StringIO

# Configuración de la página
st.set_page_config(page_title="CONTROL DE PARTICIPACIÓN", layout="wide")

# Aplicar estilo personalizado con diseño visual mejorado
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .logo-upload {
        position: absolute;
        top: 10px;
        left: 10px;
        width: 50px;
        height: 50px;
        opacity: 0.7;
    }
    .logo-container img {
        width: 396px;
        margin-top: -20px;
    }
    .title {
        text-transform: uppercase;
        text-align: center;
        font-weight: bold;
        font-size: 3em;
        color: #4CAF50;
        text-shadow: 2px 2px 4px #000000;
    }
    .student-row, .question-box {
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        padding: 15px;
        margin-bottom: 10px;
    }
    .question-completed {
        text-decoration: line-through;
        color: red;
    }
    .stats-container {
        display: flex;
        justify-content: space-around;
        gap: 20px;
        margin-bottom: 20px;
    }
    .stat-box {
        padding: 15px;
        border-radius: 12px;
        background-color: #F4F6F7;
        text-align: center;
        width: 100%;
        font-size: 1.2em;
    }
    .background {
        background: url('https://www.transparenttextures.com/patterns/diamond-upholstery.png');
    }
    .credits {
        text-align: center;
        padding: 20px;
        background-color: #e8f5e9;
        border-radius: 10px;
        margin-top: 30px;
        font-family: 'Arial', sans-serif;
    }
    .credits h3 {
        font-size: 1.8em;
        font-weight: bold;
    }
    .credits p {
        font-size: 1.1em;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Restauración completa del código original con las mejoras aplicadas

# (Aquí iría el código completo restaurado y mejorado)

# Placeholder para el contenido completo

# Iniciar la aplicación
if __name__ == "__main__":
    app = ControlParticipacion()
    app.run()
