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
    .header-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 40px;
        padding: 20px;
        margin-bottom: 30px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .logo-section {
        width: 373px;
        display: flex;
        justify-content: center;
    }
    .ruleta-section {
        flex-grow: 1;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 450px;
    }
    .divider {
        height: 2px;
        background: linear-gradient(to right, transparent, #0066cc, transparent);
        margin: 40px auto;
        width: 80%;
    }
    [Aquí van todos los estilos anteriores sin modificar...]
    </style>
""", unsafe_allow_html=True)

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
# Inicio del header container
st.markdown('<div class="header-container">', unsafe_allow_html=True)

# Sección del logo
st.markdown('<div class="logo-section">', unsafe_allow_html=True)
logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="logo")
if logo_file:
    st.image(logo_file, width=373)
st.markdown('</div>', unsafe_allow_html=True)

# Sección de la ruleta
st.markdown('<div class="ruleta-section">', unsafe_allow_html=True)
components.html("""
<!DOCTYPE html>
<html>
<head>
    <script src="https://unpkg.com/react@17/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@17/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/babel-standalone@6/babel.min.js"></script>
    <style>
        .ruleta-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 2rem;
            padding: 1rem;
            height: 100%;
        }
        .ruleta-left-panel {
            width: 200px;
        }
        .ruleta-right-panel {
            width: 450px;
        }
    </style>
</head>
<body>
    <div id="ruleta-root"></div>
    <script type="text/babel">
        const RuletaPreviewFinal = () => {
          const [rotation, setRotation] = React.useState(0);
          const [nombres, setNombres] = React.useState(["TUPIA", "ALVITES", "CHAVEZ", "ESPINOZA", "TORRES"]);
          const [textAreaValue, setTextAreaValue] = React.useState(nombres.join('\\n'));
          const [ganador, setGanador] = React.useState('');
          const [isSpinning, setIsSpinning] = React.useState(false);
          const [indicadorAngulo, setIndicadorAngulo] = React.useState(null);
          
          const colors = ['#FF9999', '#99FF99', '#9999FF', '#FFFF99', '#FF99FF'];
          const anglePerSection = 360 / nombres.length;
          
          const handleSpin = () => {
            if (isSpinning) return;
            setIsSpinning(true);
            setGanador('');
            setIndicadorAngulo(null);
            const newRotation = rotation + 1440 + Math.random() * 360;
            setRotation(newRotation);
            
            setTimeout(() => {
              const finalAngle = newRotation % 360;
              const winnerIndex = Math.floor(finalAngle / anglePerSection);
              setGanador(nombres[winnerIndex % nombres.length]);
              setIndicadorAngulo(finalAngle + (anglePerSection / 2));
              setIsSpinning(false);
            }, 4000);
          };

          const handleTextChange = (e) => {
            setTextAreaValue(e.target.value);
          };

          const handleLoadNames = () => {
            const newNames = textAreaValue
              .split('\\n')
              .map(name => name.trim())
              .filter(name => name.length > 0);
            if (newNames.length > 0) {
              setNombres(newNames);
              setGanador('');
              setIndicadorAngulo(null);
            }
          };

          return (
            <div className="ruleta-container">
              <div className="ruleta-left-panel">
                <div style={{marginBottom: '10px', fontWeight: 'bold'}}>Lista para Ruleta:</div>
                <textarea 
                  style={{
                    width: '100%',
                    height: '200px',
                    padding: '8px',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    marginBottom: '10px'
                  }}
                  value={textAreaValue}
                  onChange={handleTextChange}
                  placeholder="Ingrese nombres&#10;uno por línea"
                />
                <button 
                  onClick={handleLoadNames}
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#0066cc',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Cargar Nombres
                </button>
              </div>

              <div className="ruleta-right-panel">
                <svg 
                  viewBox="0 0 100 100"
                  style={{
                    width: '100%',
                    height: '100%',
                    transform: `rotate(${rotation}deg)`,
                    transition: 'transform 4s cubic-bezier(0.2, 0.8, 0.2, 1)'
                  }}
                >
                  {nombres.map((nombre, index) => {
                    const startAngle = index * anglePerSection;
                    const endAngle = (index + 1) * anglePerSection;
                    const startRad = (startAngle - 90) * Math.PI / 180;
                    const endRad = (endAngle - 90) * Math.PI / 180;
                    const startX = 50 + 45 * Math.cos(startRad);
                    const startY = 50 + 45 * Math.sin(startRad);
                    const endX = 50 + 45 * Math.cos(endRad);
                    const endY = 50 + 45 * Math.sin(endRad);
                    const largeArcFlag = anglePerSection <= 180 ? 0 : 1;

                    const textAngle = (startAngle + endAngle) / 2;
                    const textRad = (textAngle - 90) * Math.PI / 180;
                    const textX = 50 + 30 * Math.cos(textRad);
                    const textY = 50 + 30 * Math.sin(textRad);

                    return (
                      <g key={index}>
                        <path
                          d={`M 50 50 L ${startX} ${startY} A 45 45 0 ${largeArcFlag} 1 ${endX} ${endY} Z`}
                          fill={colors[index % colors.length]}
                          stroke="white"
                        />
                        <text
                          x={textX}
                          y={textY}
                          fill="black"
                          fontSize="4"
                          textAnchor="middle"
                          transform={`rotate(${textAngle}, ${textX}, ${textY})`}
                        >
                          {nombre}
                        </text>
                      </g>
                    );
                  })}
                  <circle cx="50" cy="50" r="5" fill="white" stroke="black" />
                </svg>
                
                <div style={{textAlign: 'center', marginTop: '20px'}}>
                  <button 
                    onClick={handleSpin}
                    disabled={isSpinning}
                    style={{
                      padding: '10px 20px',
                      backgroundColor: isSpinning ? '#ccc' : '#0066cc',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: isSpinning ? 'default' : 'pointer'
                    }}
                  >
                    {isSpinning ? 'Girando...' : 'Girar Ruleta'}
                  </button>
                  
                  {ganador && (
                    <div style={{marginTop: '20px'}}>
                      <h3 style={{margin: '0', color: '#0066cc'}}>¡GANADOR!</h3>
                      <p style={{
                        fontSize: '24px',
                        fontWeight: 'bold',
                        margin: '10px 0',
                        color: '#28a745'
                      }}>
                        {ganador}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        };

        ReactDOM.render(<RuletaPreviewFinal />, document.getElementById('ruleta-root'));
    </script>
</body>
</html>
""", height=450)
st.markdown('</div>', unsafe_allow_html=True)

# Cerrar header container
st.markdown('</div>', unsafe_allow_html=True)

# Divisor
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
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
