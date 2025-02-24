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
        'num_preguntas': st.session_state.num_preguntas
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
    except Exception as e:
        print(f"Error loading state: {e}")

def reset_state():
    if os.path.exists('app_state.json'):
        os.remove('app_state.json')
    st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Respuestas', 'Respuestas_Correctas'])
    st.session_state.preguntas = []
    st.session_state.pregunta_actual = 0
    st.session_state.num_preguntas = 5

# Función para cargar nombres de la ruleta
def cargar_nombres_ruleta(archivo):
    try:
        contenido = StringIO(archivo.getvalue().decode("utf-8")).read().splitlines()
        nombres = [nombre.strip() for nombre in contenido if nombre.strip()]
        return nombres
    except Exception as e:
        st.error(f"Error al cargar nombres: {e}")
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
    .stButton>button {
        background-color: transparent;
        border: none;
    }
    div[data-testid="stFileUploader"] {
        width: 50px;
        height: 50px;
        overflow: hidden;
        background-color: #9b9b9b;
    }
    div[data-testid="stFileUploader"] div {
        padding: 0 !important;
    }
    .question-container {
        background-color: #FFFACD;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .question-text {
        color: #0066cc;
        font-size: 1.2em;
        font-weight: bold;
        margin: 10px 0;
    }
    .question-number {
        font-size: 1.1em;
        color: #333;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .student-row {
        display: flex;
        align-items: center;
        padding: 15px;
        margin: 20px 0;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .student-separator {
        text-align: center;
        padding: 10px 0;
    }
    .separator-dots {
        color: #0066cc;
        letter-spacing: 3px;
        font-size: 20px;
    }
    .separator-line {
        height: 2px;
        background: linear-gradient(to right, transparent, #0066cc, transparent);
        margin: 5px auto;
        width: 80%;
    }
    .upload-container {
        position: fixed;
        z-index: 1000;
        width: 50px;
    }
    .upload-logo {
        top: 10px;
        left: 10px;
    }
    .upload-students {
        bottom: 10px;
        right: 70px;
    }
    .upload-questions {
        bottom: 10px;
        right: 10px;
    }
    .reset-button {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 1000;
    }
    .reset-button button {
        background-color: #dc3545 !important;
        color: white !important;
        padding: 8px 16px !important;
        border-radius: 4px !important;
        border: none !important;
    }
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { 
        -webkit-appearance: none;
        margin: 0;
    }
    input[type=number] {
        -moz-appearance: textfield;
        padding: 5px;
        font-size: 16px;
    }
    .performance-stats {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stats-title {
        color: #0066cc;
        font-size: 1.2em;
        margin-bottom: 15px;
        text-align: center;
    }
    .stats-subtitle {
        color: #333;
        font-size: 1.1em;
        margin: 12px 0;
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
    }
    .stats-highlight {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 8px 0;
    }
    .credits {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 12px;
        border-radius: 8px;
        margin-top: 25px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        font-size: 0.85em;
    }
    .credits h2 {
        color: #0066cc;
        font-size: 1.1em;
        margin-bottom: 12px;
        font-weight: bold;
    }
    .credits-info {
        color: #666;
        font-size: 0.9em;
        line-height: 1.5;
        margin: 6px 0;
    }
    .credits-divider {
        height: 1px;
        background: linear-gradient(to right, transparent, #0066cc, transparent);
        margin: 8px auto;
        width: 35%;
        opacity: 0.4;
    }
    </style>
""", unsafe_allow_html=True)

# Agregar sección de Ruleta al principio
st.markdown("<div class='ruleta-container'>", unsafe_allow_html=True)

# Ruleta file upload
st.markdown('<div class="upload-container ruleta-upload">', unsafe_allow_html=True)
ruleta_names_file = st.file_uploader("", type=['txt'], key="ruleta_names")
st.markdown('</div>', unsafe_allow_html=True)

# Load ruleta names if file is uploaded
nombres_ruleta = []
if ruleta_names_file:
    nombres_ruleta = cargar_nombres_ruleta(ruleta_names_file)
    st.success(f"Se cargaron {len(nombres_ruleta)} nombres para la Ruleta")

# Render Ruleta component
components.html(f"""
    <div id="ruleta-container"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/17.0.2/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/17.0.2/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/6.26.0/babel.min.js"></script>
    <script type="text/babel">
    const RuletaPreviewFinal = () => {{
      const [rotation, setRotation] = React.useState(0);
      const [nombres, setNombres] = React.useState({json.dumps(nombres_ruleta)});
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
          React.createElement('polygon', {{
            points: `${{tipX}},${{tipY}} ${{leftX}},${{leftY}} ${{baseX}},${{baseY}} ${{rightX}},${{rightY}}`,
            fill: 'gold',
            stroke: 'darkgold',
            strokeWidth: '0.5'
          }})
        );
      }};

      return React.createElement('div', {{ className: 'flex flex-col items-center w-full' }},
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
                const textX = 50
+ 30 * Math.cos(textRad);
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
        ),
        React.createElement('div', {{ className: 'absolute right-0 top-1/2 -mt-2 w-0 h-0 border-t-8 border-t-transparent border-l-[16px] border-l-red-600 border-b-8 border-b-transparent' }})
      ),
      React.createElement('div', {{ className: 'mt-4' }},
        React.createElement('textarea', {{
          className: 'w-full p-2 border rounded mb-2 h-24',
          value: textAreaValue,
          onChange: handleTextChange,
          placeholder: 'Ingrese nombres aquí, uno por línea'
        }}),
        React.createElement('div', {{ className: 'flex space-x-2' }},
          React.createElement('button', {{
            onClick: handleLoadNames,
            className: 'flex-grow bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600'
          }}, 'Cargar Nombres'),
          React.createElement('button', {{
            onClick: handleSpin,
            disabled: isSpinning || nombres.length === 0,
            className: `flex-grow px-4 py-2 rounded text-white transition-colors ${{
              isSpinning || nombres.length === 0 ? 'bg-gray-400' : 'bg-green-500 hover:bg-green-600'
            }}`
          }}, isSpinning ? 'Girando...' : 'Girar Ruleta')
        ),
        ganador && React.createElement('div', {{ className: 'mt-4 text-center' }},
          React.createElement('h3', {{ className: 'text-xl font-bold' }}, '¡GANADOR!'),
          React.createElement('p', {{ className: 'text-2xl font-bold text-blue-600' }}, ganador)
        )
      )
    }};

    ReactDOM.render(
      React.createElement(RuletaPreviewFinal),
      document.getElementById('ruleta-container')
    );
    </script>
""", height=600)
st.markdown("</div>", unsafe_allow_html=True)

# Cargar estado al inicio
if 'state_loaded' not in st.session_state:
    load_state()
    st.session_state.state_loaded = True

# Botón de reinicio
st.markdown('<div class="reset-button">', unsafe_allow_html=True)
if st.button("🗑️ Reiniciar Todo"):
    reset_state()
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Inicialización del estado
if 'estudiantes' not in st.session_state:
    st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Respuestas', 'Respuestas_Correctas'])
if 'preguntas' not in st.session_state:
    st.session_state.preguntas = []
if 'pregunta_actual' not in st.session_state:
    st.session_state.pregunta_actual = 0
if 'num_preguntas' not in st.session_state:
    st.session_state.num_preguntas = 5
  # Cargar logo
st.markdown('<div class="upload-container upload-logo">', unsafe_allow_html=True)
logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="logo")
st.markdown('</div>', unsafe_allow_html=True)

if logo_file:
    st.image(logo_file, width=300)

# Configuración inicial
col1, col2, _ = st.columns([2, 1, 1])
with col1:
    nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE")
with col2:
    num_preguntas = st.text_input("NÚMERO DE PREGUNTAS", value="5", key="num_preguntas_input")
    try:
        st.session_state.num_preguntas = int(num_preguntas)
        save_state()
    except ValueError:
        st.error("Por favor ingrese un número válido")

# Botón para agregar estudiante
if st.button("AGREGAR ESTUDIANTE") and nuevo_estudiante:
    if nuevo_estudiante not in st.session_state.estudiantes['Nombre'].values:
        nuevo_df = pd.DataFrame({
            'Nombre': [nuevo_estudiante],
            'Respuestas': ['0' * st.session_state.num_preguntas],
            'Respuestas_Correctas': [0]
        })
        st.session_state.estudiantes = pd.concat([st.session_state.estudiantes, nuevo_df], ignore_index=True)
        save_state()

# Cargar estudiantes desde archivo
st.markdown('<div class="upload-container upload-students">', unsafe_allow_html=True)
students_file = st.file_uploader("", type=['txt'], key="students")
st.markdown('</div>', unsafe_allow_html=True)

if students_file:
    try:
        contenido = StringIO(students_file.getvalue().decode("utf-8")).read().splitlines()
        for estudiante in contenido:
            if estudiante.strip() and estudiante not in st.session_state.estudiantes['Nombre'].values:
                nuevo_df = pd.DataFrame({
                    'Nombre': [estudiante.strip()],
                    'Respuestas': ['0' * st.session_state.num_preguntas],
                    'Respuestas_Correctas': [0]
                })
                st.session_state.estudiantes = pd.concat([st.session_state.estudiantes, nuevo_df], ignore_index=True)
        save_state()
        st.success(f"Se cargaron {len(contenido)} estudiantes")
    except Exception as e:
        st.error(f"Error al cargar estudiantes: {str(e)}")

# Mostrar preguntas
if st.session_state.preguntas:
    st.markdown("<div class='question-container'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("←") and st.session_state.pregunta_actual > 0:
            st.session_state.pregunta_actual -= 1
            save_state()
            st.rerun()
    with col2:
        st.markdown(f"<div class='question-number'>Pregunta {st.session_state.pregunta_actual + 1}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='question-text'>{st.session_state.preguntas[st.session_state.pregunta_actual]}</div>", unsafe_allow_html=True)
    with col3:
        if st.button("→") and st.session_state.pregunta_actual < len(st.session_state.preguntas) - 1:
            st.session_state.pregunta_actual += 1
            save_state()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Mostrar estudiantes
for idx, estudiante in st.session_state.estudiantes.iterrows():
    st.markdown("<div class='student-row'>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([2, 6, 1, 1])
    with col1:
        st.write(estudiante['Nombre'])
    with col2:
        for i in range(st.session_state.num_preguntas):
            respuestas = list(estudiante['Respuestas'])
            if st.button("⬤", key=f"circle_{estudiante['Nombre']}_{i}", 
                        help="Click para marcar respuesta",
                        type="secondary" if respuestas[i] == '0' else "primary"):
                respuestas[i] = '1' if respuestas[i] == '0' else '0'
                st.session_state.estudiantes.loc[idx, 'Respuestas'] = ''.join(respuestas)
                st.session_state.estudiantes.loc[idx, 'Respuestas_Correctas'] = sum(1 for r in respuestas if r == '1')
                save_state()
                st.rerun()
    with col3:
        nota = (sum(1 for r in estudiante['Respuestas'] if r == '1') / st.session_state.num_preguntas) * 20
        nota = round(nota, 1)
        if nota >= 14:
            color = '#28a745'  # Verde
        elif nota >= 11:
            color = '#ffc107'  # Amarillo
        else:
            color = '#dc3545'  # Rojo
        st.markdown(f"<span style='color:{color};font-weight:bold;font-size:1.1em'>{nota}</span>", unsafe_allow_html=True)
    with col4:
        if st.button("🗑️", key=f"delete_{estudiante['Nombre']}"):
            st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)
            save_state()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Separador decorativo entre estudiantes
    st.markdown("""
        <div class="student-separator">
            <div class="separator-dots">• • •</div>
            <div class="separator-line"></div>
        </div>
    """, unsafe_allow_html=True)

# Cargar preguntas
st.markdown('<div class="upload-container upload-questions">', unsafe_allow_html=True)
questions_file = st.file_uploader("", type=['txt'], key="questions")
st.markdown('</div>', unsafe_allow_html=True)

if questions_file:
    contenido = StringIO(questions_file.getvalue().decode("utf-8")).read().splitlines()
    st.session_state.preguntas = [linea.strip() for linea in contenido if linea.strip()]
    save_state()
    st.success(f"Se cargaron {len(st.session_state.preguntas)} preguntas")

# Estadísticas
if not st.session_state.estudiantes.empty:
    st.markdown("### Estadísticas de Participación")
    
    # Preparar datos para estadísticas
    df_stats = pd.DataFrame({
        'Nombre': st.session_state.estudiantes['Nombre'],
        'Respuestas_Correctas': st.session_state.estudiantes['Respuestas'].apply(lambda x: sum(1 for r in x if r == '1')),
        'Porcentaje': st.session_state.estudiantes['Respuestas'].apply(lambda x: sum(1 for r in x if r == '1') / st.session_state.num_preguntas * 100)
    })
    
    col1, col2, col3, col4 = st.columns([3, 3, 3, 3])
    
    with col1:
        fig = px.bar(df_stats, x='Nombre', y='Respuestas_Correctas',
                    title='Respuestas Correctas por Estudiante',
                    color='Respuestas_Correctas',
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig)
    
    with col2:
        fig = px.pie(df_stats, values='Porcentaje', names='Nombre',
                    title='Distribución de Participación (%)')
        st.plotly_chart(fig)
    
    with col3:
        st.markdown("<div class='performance-stats'>", unsafe_allow_html=True)
        st.markdown("<div class='stats-title'>Análisis de Rendimiento</div>", unsafe_allow_html=True)
        
        # Mejor estudiante
        mejor_estudiante = df_stats.loc[df_stats['Porcentaje'].idxmax()]
        st.markdown("<div class='stats-highlight'>", unsafe_allow_html=True)
        st.markdown(f"🏆 **Mejor estudiante**: **{mejor_estudiante['Nombre']}** ({mejor_estudiante['Porcentaje']:.1f}%)")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Clasificación por niveles
        st.markdown('<div class="stats-subtitle">Niveles de Rendimiento:</div>', unsafe_allow_html=True)
        niveles = {
            'Excelente (90-100%)': df_stats[df_stats['Porcentaje'] >= 90]['Nombre'].tolist(),
            'Bueno (70-89%)': df_stats[(df_stats['Porcentaje'] >= 70) & (df_stats['Porcentaje'] < 90)]['Nombre'].tolist(),
            'Regular (60-69%)': df_stats[(df_stats['Porcentaje'] >= 60) & (df_stats['Porcentaje'] < 70)]['Nombre'].tolist(),
            'En riesgo (<60%)': df_stats[df_stats['Porcentaje'] < 60]['Nombre'].tolist()
        }

        for nivel, estudiantes in niveles.items():
            st.write(f"{nivel}: **{len(estudiantes)}** estudiantes")
            if estudiantes:
                st.write(f"_{', '.join(estudiantes)}_")
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='performance-stats'>", unsafe_allow_html=True)
        st.markdown("<div class='stats-title'>Notas Vigesimales (0-20)</div>", unsafe_allow_html=True)
        
        # Notas por estudiante
        st.markdown("<div class='stats-subtitle'>Calificaciones:</div>", unsafe_allow_html=True)
        
        # Calcular y mostrar notas
        for _, estudiante in df_stats.iterrows():
            nota = (estudiante['Respuestas_Correctas'] / st.session_state.num_preguntas) * 20
            nota = round(nota, 1)
            
            # Determinar color según la nota
            if nota >= 14:
                color = '#28a745'  # Verde (Aprobado)
                estado = "✓ APROBADO"
            elif nota >= 11:
                color = '#ffc107'  # Amarillo (Regular)
                estado = "⚠ REGULAR"
            else:
                color = '#dc3545'  # Rojo (Desaprobado)
                estado = "✗ DESAPROBADO"
            
            # Mostrar cada nota con formato
            st.markdown(f"""
                <div style='
                    background-color: #f8f9fa;
                    padding: 8px;
                    border-radius: 5px;
                    margin: 5px 0;
                    border-left: 4px solid {color};
                '>
                    <strong>{estudiante['Nombre']}</strong><br/>
                    Nota: <span style='color:{color};font-size:1.1em;font-weight:bold'>{nota}</span><br/>
                    <span style='color:{color};font-size:0.9em'>{estado}</span>
                </div>
            """, unsafe_allow_html=True)
        
        # Mostrar promedio del aula
        promedio = df_stats['Respuestas_Correctas'].mean() * 20 / st.session_state.num_preguntas
        st.markdown("<div class='stats-highlight' style='margin-top:15px'>", unsafe_allow_html=True)
        st.markdown(f"📊 **Promedio del aula**: {promedio:.1f}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

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
