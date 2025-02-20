import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Datos simulados de estudiantes
datos = [
    {'nombre': 'JOSE CHAMACHE', 'participaciones': 4, 'nota': 8},
    {'nombre': 'NILTON GUEVARA', 'participaciones': 1, 'nota': 2},
    {'nombre': 'MARLON MUGUERZA', 'participaciones': 1, 'nota': 2},
    {'nombre': 'FORTUANDO OJEDA', 'participaciones': 1, 'nota': 2},
    {'nombre': 'JUAN SEMINARIO', 'participaciones': 1, 'nota': 2},
    {'nombre': 'LUIS SARAVIA', 'participaciones': 1, 'nota': 2}
]

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

# Cargar archivo TXT
archivo = st.file_uploader('Cargar archivo TXT', type=['txt'])
if archivo:
    contenido = archivo.read().decode('utf-8').split('\n')
    for linea in contenido:
        if linea:
            datos.append({'nombre': linea, 'participaciones': 0, 'nota': 0})
    st.success('Archivo cargado correctamente.')

# Sección de Preguntas
st.subheader('Gestión de Preguntas')
preguntas = []
nueva_pregunta = st.text_input('Escriba una nueva pregunta')
if st.button('Agregar Pregunta'):
    if nueva_pregunta:
        preguntas.append(nueva_pregunta)

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
