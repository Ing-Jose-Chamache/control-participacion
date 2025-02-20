import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# requirements.txt
# streamlit
# pandas
# matplotlib

# Inicializar listas vacías para estudiantes y preguntas
datos = []
preguntas = []

st.markdown('<h1 style="text-align: center;">CONTROL DE PARTICIPACIÓN</h1>', unsafe_allow_html=True)

# Cargar logo
col_logo1, col_logo2, col_logo3 = st.columns([1, 6, 1])
with col_logo1:
    logo_pequeno = st.file_uploader("Cargar logo pequeño", type=["png", "jpg", "jpeg"])
with col_logo2:
    logo_central = st.file_uploader("Cargar logo central", type=["png", "jpg", "jpeg"])

if logo_central:
    st.image(logo_central, width=300)

# Formulario para agregar estudiantes
nombre = st.text_input('Nombre del estudiante')
if st.button('Agregar Estudiante'):
    if nombre:
        datos.append({'nombre': nombre, 'participaciones': 0, 'nota': 0})
        st.success('Estudiante agregado correctamente.')

# Mostrar lista de estudiantes
st.subheader('Lista de Estudiantes')
for estudiante in datos:
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.write(estudiante['nombre'])
    with col2:
        if st.button(f"➕ {estudiante['nombre']}"):
            estudiante['participaciones'] += 1
            estudiante['nota'] += 1
    with col3:
        if st.button(f"➖ {estudiante['nombre']}"):
            if estudiante['participaciones'] > 0:
                estudiante['participaciones'] -= 1
                estudiante['nota'] -= 1
    with col4:
        if st.button(f"❌ {estudiante['nombre']}"):
            datos.remove(estudiante)

# Cargar archivo TXT para estudiantes
st.subheader('Cargar Estudiantes desde TXT')
archivo_estudiantes = st.file_uploader('Selecciona un archivo TXT para estudiantes', type=['txt'])
if archivo_estudiantes:
    contenido = archivo_estudiantes.read().decode('utf-8').split('\n')
    for linea in contenido:
        if linea:
            datos.append({'nombre': linea, 'participaciones': 0, 'nota': 0})
    st.success('Estudiantes cargados correctamente.')

# Cargar archivo TXT para preguntas
st.subheader('Cargar Preguntas desde TXT')
archivo_preguntas = st.file_uploader('Selecciona un archivo TXT para preguntas', type=['txt'])
if archivo_preguntas:
    contenido = archivo_preguntas.read().decode('utf-8').split('\n')
    for linea in contenido:
        if linea:
            preguntas.append(linea)
    st.success('Preguntas cargadas correctamente.')

# Mostrar preguntas
st.subheader('Lista de Preguntas')
for pregunta in preguntas:
    col_p1, col_p2 = st.columns([4, 1])
    with col_p1:
        st.write(pregunta)
    with col_p2:
        if st.button(f"❌ Eliminar {pregunta}"):
            preguntas.remove(pregunta)

# Mostrar estadísticas
st.subheader('Estadísticas')
df = pd.DataFrame(datos)
if not df.empty:
    st.write(df)

    # Gráfico de barras
    st.bar_chart(df.set_index('nombre')['participaciones'])

    # Gráfico circular
    fig, ax = plt.subplots()
    ax.pie(df['participaciones'], labels=df['nombre'], autopct='%1.1f%%')
    st.pyplot(fig)

# Archivo requirements.txt
txt_requirements = """
streamlit
pandas
matplotlib
"""
st.download_button(label="Descargar requirements.txt", data=txt_requirements, file_name="requirements.txt")
