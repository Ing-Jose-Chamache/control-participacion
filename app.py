import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import base64
from io import StringIO
import json
import os
import streamlit.components.v1 as components

# Funciones de persistencia
def save_state():
    state_data = {
        'estudiantes': st.session_state.estudiantes.to_dict(),
        'preguntas': st.session_state.preguntas,
        'pregunta_actual': st.session_state.pregunta_actual,
        'num_preguntas': st.session_state.num_preguntas,
        'ruleta_nombres': st.session_state.ruleta_nombres if 'ruleta_nombres' in st.session_state else []
    }
    with open('app_state.json', 'w') as f:
        json.dump(state_data, f)

def load_state():
    try:
        if os.path.exists('app_state.json'):
            with open('app_state.json', 'r') as f:
                state_data = json.load(f)
            # Restaurar el DataFrame
            st.session_state.estudiantes = pd.DataFrame.from_dict(state_data['estudiantes'])
            st.session_state.preguntas = state_data['preguntas']
            st.session_state.pregunta_actual = state_data['pregunta_actual']
            st.session_state.num_preguntas = state_data['num_preguntas']
            st.session_state.ruleta_nombres = state_data.get('ruleta_nombres', [])
    except Exception as e:
        print(f"Error loading state: {e}")

def reset_state():
    if os.path.exists('app_state.json'):
        os.remove('app_state.json')
    st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Respuestas', 'Respuestas_Correctas'])
    st.session_state.preguntas = []
    st.session_state.pregunta_actual = 0
    st.session_state.num_preguntas = 5
    st.session_state.ruleta_nombres = []

# Función para cargar nombres de la ruleta
def load_wheel_names(file):
    try:
        contenido = StringIO(file.getvalue().decode("utf-8")).read().splitlines()
        nombres = [nombre.strip() for nombre in contenido if nombre.strip()]
        return nombres
    except Exception as e:
        st.error(f"Error al cargar nombres: {str(e)}")
        return []

# Configuración de la página
st.set_page_config(page_title="Control de Participación", layout="wide")

# Estilo personalizado
st.markdown("""
    <style>
    .main {
        padding: 1rem;
        background-color: #f5f5f5;
    }
    .stApp {
        background-color: #f5f5f5;
    }
    .ruleta-container {
        display: flex;
        justify-content: center;
        width: 100%;
        margin-bottom: 20px;
    }
    .upload-container.ruleta-upload {
        position: fixed;
        top: 70px;
        left: 10px;
        z-index: 1000;
    }
    /* Rest of the previous styles remain the same */
    </style>
""", unsafe_allow_html=True)

# Cargar estado al inicio
if 'state_loaded' not in st.session_state:
    load_state()
    st.session_state.state_loaded = True

# Inicialización del estado
if 'estudiantes' not in st.session_state:
    st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Respuestas', 'Respuestas_Correctas'])
if 'preguntas' not in st.session_state:
    st.session_state.preguntas = []
if 'pregunta_actual' not in st.session_state:
    st.session_state.pregunta_actual = 0
if 'num_preguntas' not in st.session_state:
    st.session_state.num_preguntas = 5
if 'ruleta_nombres' not in st.session_state:
    st.session_state.ruleta_nombres = []

# Botón de reinicio
st.markdown('<div class="reset-button">', unsafe_allow_html=True)
if st.button("🗑️ Reiniciar Todo"):
    reset_state()
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Agregar sección de Ruleta al principio
st.markdown("<div class='ruleta-container'>", unsafe_allow_html=True)

# Ruleta file upload
st.markdown('<div class="upload-container ruleta-upload">', unsafe_allow_html=True)
ruleta_names_file = st.file_uploader("", type=['txt'], key="ruleta_names")
st.markdown('</div>', unsafe_allow_html=True)

# Load ruleta names if file is uploaded
if ruleta_names_file:
    st.session_state.ruleta_nombres = load_wheel_names(ruleta_names_file)
    st.success(f"Se cargaron {len(st.session_state.ruleta_nombres)} nombres para la ruleta")

# Render Ruleta component
components.html(f"""
    <div id="ruleta-container"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/17.0.2/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/17.0.2/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/6.26.0/babel.min.js"></script>
    <script type="text/babel">
    const RuletaPreviewFinal = () => {{
      const [rotation, setRotation] = React.useState(0);
      const [nombres, setNombres] = React.useState({json.dumps(st.session_state.ruleta_nombres)});
      const [textAreaValue, setTextAreaValue] = React.useState(nombres.join('\\n'));
      const [ganador, setGanador] = React.useState('');
      const [isSpinning, setIsSpinning] = React.useState(false);
      const [indicadorAngulo, setIndicadorAngulo] = React.useState(null);
      
      const colors = ['#FF9999', '#99FF99', '#9999FF', '#FFFF99', '#FF99FF'];
      const anglePerSection = 360 / Math.max(1, nombres.length);
      
      const handleSpin = () => {{
        if (isSpinning || nombres.length === 0) return;
        
        setIsSpinning(true);
        setGanador('');
        setIndicadorAngulo(null);
        const newRotation = rotation + 1440 + Math.random() * 360;
        setRotation(newRotation);
        
        setTimeout(() => {{
          const finalAngle = newRotation % 360;
          const winnerIndex = Math.floor(finalAngle / anglePerSection);
          setGanador(nombres[winnerIndex % nombres.length]);
          setIndicadorAngulo(finalAngle + (anglePerSection / 2));
          setIsSpinning(false);
        }}, 4000);
      }};

      const handleTextChange = (e) => {{
        setTextAreaValue(e.target.value);
      }};

      const handleLoadNames = () => {{
        const newNames = textAreaValue
          .split('\\n')
          .map(name => name.trim())
          .filter(name => name.length > 0);
        if (newNames.length > 0) {{
          setNombres(newNames);
          setGanador('');
          setIndicadorAngulo(null);
        }}
      }};

      const renderWinnerArrow = () => {{
        if (!indicadorAngulo || isSpinning || nombres.length === 0) return null;

        const arrowLength = 20;
        const arrowWidth = 10;
        const centerX = 50;
        const centerY = 50;
        const radius = 45;
        
        const angle = (indicadorAngulo - 90) * (Math.PI / 180);
        const tipX = centerX + (radius + 5) * Math.cos(angle);
        const tipY = centerY + (radius + 5) * Math.sin(angle);
        
        const baseAngle = angle + Math.PI;
        const baseX = tipX + arrowLength * Math.cos(baseAngle);
        const baseY = tipY + arrowLength * Math.sin(baseAngle);
        
        const leftX = tipX + arrowWidth * Math.cos(baseAngle + Math.PI/2);
        const leftY = tipY + arrowWidth * Math.sin(baseAngle + Math.PI/2);
        const rightX = tipX + arrowWidth * Math.cos(baseAngle - Math.PI/2);
        const rightY = tipY + arrowWidth * Math.sin(baseAngle - Math.PI/2);

        return (
          <polygon
            points={`${{tipX}},{tipY} {leftX},{leftY} {baseX},{baseY} {rightX},{rightY}`}
            fill="gold"
            stroke="darkgolden"
            strokeWidth="0.5"
          />
        );
      }};

      return (
        React.createElement('div', {{ className: 'flex flex-col items-center w-full' }},
          React.createElement('div', {{ className: 'relative w-96 h-96' }},
            nombres.length === 0 ? (
              React.createElement('div', {{ className: 'w-full h-full bg-gray-200 flex items-center justify-center text-gray-500' }}, 'No hay nombres')
            ) : (
              React.createElement('svg', {{
                className: 'w-full h-full',
                viewBox: '0 0 100 100',
                style: {{
                  transform: `rotate(${{rotation}}deg)`,
                  transition: 'transform 4s cubic-bezier(0.2, 0.8, 0.2, 1)'
                }}
              }},
                nombres.map((nombre, index) => {{
                  const startAngle = index * anglePerSection;
                  const endAngle = (index + 1) * anglePerSection;
                  
                  const startRad = (startAngle - 90) * Math.PI / 180;
                  const endRad = (endAngle - 90) * Math.PI / 180;
                  
                  const startX = 50 + 45 * Math.cos(startRad);
                  const startY = 50 + 45 * Math.sin(startRad);
                  const endX = 50 + 45 * Math.cos(endRad);
                  const endY = 50 + 45 * Math.sin(endRad);
                  
                  const largeArcFlag = anglePerSection <= 180 ? 0 : 1;
                  
                  const pathData = `
                    M 50 50
                    L ${{startX}} ${{startY}}
                    A 45 45 0 ${{largeArcFlag}} 1 ${{endX}} ${{endY}}
                    Z
                  `;
                  
                  const textAngle = (startAngle + endAngle) / 2;
                  const textRad = (textAngle - 90) * Math.PI / 180;
                  const textX = 50 + 30 * Math.cos(textRad);
                  const textY = 50 + 30 * Math.sin(textRad);
                  
                  return React.createElement('g', {{ key: index }},
                    React.createElement('path', {{
                      d: pathData,
                      fill: colors[index % colors.length],
                      stroke: 'white',
                      strokeWidth: '0.5'
                    }}),
                    React.createElement('text', {{
                      x: textX,
                      y: textY,
                      fontSize: '6',
                      fill: 'black',
                      textAnchor: 'middle',
                      transform: `rotate(${{textAngle}}, ${{textX}}, ${{textY}})`
                    }}, nombre)
                  );
                }})
              )
            )
          )
        )
      );
    }};

    ReactDOM.render(
      React.createElement(RuletaPreviewFinal),
      document.getElementById('ruleta-container')
    );
    </script>
""", height=500)
st.markdown("</div>", unsafe_allow_html=True)

# Cargar logo
st.markdown('<div class="upload-container upload-logo">', unsafe_allow_html=True)
logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="logo")
st.markdown('</div>', unsafe_allow_html=True)

if logo_file:
    st.image(logo_file, width=300)

# Resto del código original continúa...
# (El resto del código de la versión original se mantiene igual)
# ... [Continúa con la configuración inicial, agregar estudiantes, 
#      mostrar preguntas, mostrar estudiantes, cargar preguntas, 
#      mostrar estadísticas, y créditos]

# Créditos
st.markdown("""
    <div class="credits">
        <h2>Créditos</h2>
        <div class="credits-divider"></div>
        <div class="credits-info">
            <strong>Desarrollador:</strong> Ing. José Yván Chamache Chiong<br>
            <strong>Lenguaje:</strong> Python<br>
            <strong>Ciudad:</strong> Lima, Febrero 2025<br>
            <strong>Escuela:</strong> Instructor de la Escuela Profesional de Artes Gráficas
        </div>
        <div class="credits-divider"></div>
    </div>
""", unsafe_allow_html=True)
