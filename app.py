import streamlit as st
import pandas as pd

# Datos simulados de estudiantes
datos = [
    {'nombre': 'JOSE CHAMACHE', 'participaciones': 4, 'nota': 8},
    {'nombre': 'NILTON GUEVARA', 'participaciones': 1, 'nota': 2},
    {'nombre': 'MARLON MUGUERZA', 'participaciones': 1, 'nota': 2},
    {'nombre': 'FORTUANDO OJEDA', 'participaciones': 1, 'nota': 2},
    {'nombre': 'JUAN SEMINARIO', 'participaciones': 1, 'nota': 2},
    {'nombre': 'LUIS SARAVIA', 'participaciones': 1, 'nota': 2}
]

st.title('Control de Participación')

# Mostrar tabla de estudiantes
df = pd.DataFrame(datos)
st.dataframe(df)

# Formulario para agregar estudiantes
nombre = st.text_input('Nombre del estudiante')
if st.button('Agregar Estudiante'):
    if nombre:
        datos.append({'nombre': nombre, 'participaciones': 0, 'nota': 0})
        st.success('Estudiante agregado correctamente.')

# Incrementar y decrementar participaciones
for estudiante in datos:
    col1, col2, col3 = st.columns([3, 1, 1])
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

# Cargar archivo TXT
archivo = st.file_uploader('Cargar archivo TXT', type=['txt'])
if archivo:
    contenido = archivo.read().decode('utf-8').split('\n')
    for linea in contenido:
        if linea:
            datos.append({'nombre': linea, 'participaciones': 0, 'nota': 0})
    st.success('Archivo cargado correctamente.')

# Mostrar gráfico de barras
st.bar_chart(pd.DataFrame(datos)['participaciones'])
