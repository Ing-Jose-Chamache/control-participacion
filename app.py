from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Datos simulados de estudiantes
datos = [
    {'nombre': 'JOSE CHAMACHE', 'participaciones': 4, 'nota': 8},
    {'nombre': 'NILTON GUEVARA', 'participaciones': 1, 'nota': 2},
    {'nombre': 'MARLON MUGUERZA', 'participaciones': 1, 'nota': 2},
    {'nombre': 'FORTUANDO OJEDA', 'participaciones': 1, 'nota': 2},
    {'nombre': 'JUAN SEMINARIO', 'participaciones': 1, 'nota': 2},
    {'nombre': 'LUIS SARAVIA', 'participaciones': 1, 'nota': 2}
]

@app.route('/')
def index():
    return render_template('index.html', estudiantes=datos)

@app.route('/agregar', methods=['POST'])
def agregar_estudiante():
    nombre = request.form['nombre']
    if nombre:
        datos.append({'nombre': nombre, 'participaciones': 0, 'nota': 0})
        flash('Estudiante agregado correctamente.')
    return redirect(url_for('index'))

@app.route('/incrementar/<nombre>')
def incrementar(nombre):
    for estudiante in datos:
        if estudiante['nombre'] == nombre:
            estudiante['participaciones'] += 1
            estudiante['nota'] += 1
    return redirect(url_for('index'))

@app.route('/decrementar/<nombre>')
def decrementar(nombre):
    for estudiante in datos:
        if estudiante['nombre'] == nombre and estudiante['participaciones'] > 0:
            estudiante['participaciones'] -= 1
            estudiante['nota'] -= 1
    return redirect(url_for('index'))

@app.route('/cargar_txt', methods=['POST'])
def cargar_txt():
    archivo = request.files['archivo']
    if archivo and archivo.filename.endswith('.txt'):
        contenido = archivo.read().decode('utf-8').split('\n')
        for linea in contenido:
            if linea:
                datos.append({'nombre': linea, 'participaciones': 0, 'nota': 0})
        flash('Archivo cargado correctamente.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
