import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# Configuración de la página
st.set_page_config(page_title="CONTROL DE PARTICIPACIÓN", layout="wide")

# Inicialización de estados
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

# Cargar logo (solo botón pequeño)
col1, col2, col3 = st.columns([1, 10, 1])
with col1:
    logo_file = st.file_uploader("", type=['jpg', 'bmp'])
    if logo_file:
        st.session_state.logo = base64.b64encode(logo_file.getvalue()).decode()

# Mostrar logo si existe
if st.session_state.logo:
    st.markdown(f"""
        <div style='text-align: center;'>
            <img src="data:image/jpeg;base64,{st.session_state.logo}" width="300"/>
        </div>
    """, unsafe_allow_html=True)

st.title("CONTROL DE PARTICIPACIÓN")

# Sección de Estudiantes
st.subheader("ESTUDIANTES")

# Participaciones esperadas
participaciones = st.number_input("PARTICIPACIONES ESPERADAS", min_value=1, value=st.session_state.participaciones_esperadas)
if participaciones != st.session_state.participaciones_esperadas:
    st.session_state.participaciones_esperadas = participaciones
    # Actualizar puntajes
    for idx in st.session_state.estudiantes.index:
        part = st.session_state.estudiantes.at[idx, 'Participaciones']
        st.session_state.estudiantes.at[idx, 'Puntaje'] = (part / participaciones) * 20

# Agregar estudiante
col1, col2 = st.columns([3, 1])
with col1:
    nuevo_estudiante = st.text_input("NOMBRE DEL ESTUDIANTE")
with col2:
    if st.button("AGREGAR") and nuevo_estudiante:
        if nuevo_estudiante not in st.session_state.estudiantes['Nombre'].values:
            nuevo_df = pd.DataFrame([[nuevo_estudiante, 0, 0]], columns=['Nombre', 'Participaciones', 'Puntaje'])
            st.session_state.estudiantes = pd.concat([st.session_state.estudiantes, nuevo_df], ignore_index=True)

# Lista de estudiantes
for idx, row in st.session_state.estudiantes.iterrows():
    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
    with col1:
        st.write(f"**{row['Nombre']}**")
    with col2:
        st.write(f"{row['Participaciones']}/{participaciones} | {row['Puntaje']:.1f}")
    with col3:
        if st.button("+1", key=f"+_{idx}"):
            st.session_state.estudiantes.at[idx, 'Participaciones'] += 1
            st.session_state.estudiantes.at[idx, 'Puntaje'] = (st.session_state.estudiantes.at[idx, 'Participaciones'] / participaciones) * 20
    with col4:
        if st.button("-1", key=f"-_{idx}"):
            if st.session_state.estudiantes.at[idx, 'Participaciones'] > 0:
                st.session_state.estudiantes.at[idx, 'Participaciones'] -= 1
                st.session_state.estudiantes.at[idx, 'Puntaje'] = (st.session_state.estudiantes.at[idx, 'Participaciones'] / participaciones) * 20
    with col5:
        if st.button("❌", key=f"del_{idx}"):
            st.session_state.estudiantes = st.session_state.estudiantes.drop(idx).reset_index(drop=True)

# Eliminar todos los estudiantes
if not st.session_state.estudiantes.empty:
    if st.button("ELIMINAR TODOS LOS ESTUDIANTES"):
        st.session_state.estudiantes = pd.DataFrame(columns=['Nombre', 'Participaciones', 'Puntaje'])

# Gráficos
if not st.session_state.estudiantes.empty:
    col1, col2 = st.columns(2)
    with col1:
        fig_bar = px.bar(
            st.session_state.estudiantes,
            x='Nombre',
            y='Participaciones',
            title='PARTICIPACIONES POR ESTUDIANTE'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        total = st.session_state.estudiantes['Participaciones'].sum()
        if total > 0:
            datos_torta = st.session_state.estudiantes.copy()
            datos_torta['Porcentaje'] = (datos_torta['Participaciones'] / total * 100)
            fig_pie = px.pie(
                datos_torta,
                values='Porcentaje',
                names='Nombre',
                title='DISTRIBUCIÓN DE PARTICIPACIONES (%)'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# Sección de Preguntas
st.subheader("PREGUNTAS")

# Agregar pregunta
col1, col2 = st.columns([3, 1])
with col1:
    nueva_pregunta = st.text_input("NUEVA PREGUNTA")
with col2:
    if st.button("AGREGAR PREGUNTA") and nueva_pregunta:
        st.session_state.preguntas.append(nueva_pregunta)

# Lista de preguntas
for i, pregunta in enumerate(st.session_state.preguntas):
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        if i in st.session_state.preguntas_completadas:
            st.markdown(f"<p style='text-decoration: line-through; font-weight: bold;'>{i+1}. {pregunta}</p>", unsafe_allow_html=True)
        else:
            st.write(f"{i+1}. {pregunta}")
    with col2:
        if st.button("✓" if i not in st.session_state.preguntas_completadas else "↩", key=f"check_{i}"):
            if i in st.session_state.preguntas_completadas:
                st.session_state.preguntas_completadas.remove(i)
            else:
                st.session_state.preguntas_completadas.add(i)
    with col3:
        if st.button("❌", key=f"del_preg_{i}"):
            st.session_state.preguntas.pop(i)
            st.session_state.preguntas_completadas = {x if x < i else x - 1 for x in st.session_state.preguntas_completadas if x != i}

# Eliminar todas las preguntas
if st.session_state.preguntas:
    if st.button("ELIMINAR TODAS LAS PREGUNTAS"):
        st.session_state.preguntas = []
        st.session_state.preguntas_completadas = set()

# Créditos
st.markdown("""
    <div style="text-align: center; padding: 20px; margin-top: 30px;">
        <h3>Desarrollado por:</h3>
        <p><strong>Ing. José Yván Chamache Chiong</strong></p>
        <p>Lima, Perú - 2024</p>
    </div>
""", unsafe_allow_html=True)
