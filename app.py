import tkinter as tk
from tkinter import filedialog, PhotoImage
from PIL import Image, ImageTk

# Preguntas de ejemplo
questions = [
    "¿QUÉ ES UN PERFIL DE COLOR?",
    "¿CÓMO FUNCIONA RGB?",
    "¿QUÉ ES CMYK?",
    "¿POR QUÉ SE USA ICC?",
    "¿CÓMO AJUSTAR EL BALANCE DE COLOR?"
]

current_index = 0

# Función para cargar el logo
def load_logo():
    file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if file_path:
        img = Image.open(file_path)
        img = img.resize((200, 200))
        photo = ImageTk.PhotoImage(img)
        logo_label.config(image=photo)
        logo_label.image = photo

# Función para mostrar la pregunta actual
def show_question(index):
    question_label.config(text=questions[index])

# Funciones para navegar entre preguntas
def next_question():
    global current_index
    if current_index < len(questions) - 1:
        current_index += 1
        show_question(current_index)

def prev_question():
    global current_index
    if current_index > 0:
        current_index -= 1
        show_question(current_index)

# Crear ventana principal
root = tk.Tk()
root.title("Preguntas y Logo")
root.configure(bg="#d3d3d3")  # Fondo gris claro
root.geometry("800x400")

# Botón para cargar logo
logo_button = tk.Button(root, text="Cargar Logo", command=load_logo)
logo_button.place(x=20, y=20)

# Área del logo
logo_label = tk.Label(root, bg="#d3d3d3")
logo_label.place(x=20, y=70, width=200, height=200)

# Cuadro de preguntas
question_frame = tk.Frame(root, bg="#fffacd", width=500, height=200)  # Fondo amarillo suave
question_frame.place(relx=0.5, rely=0.5, anchor="center")

# Etiqueta para la pregunta
question_label = tk.Label(question_frame, text="", font=("Arial", 24, "bold"), fg="blue", bg="#fffacd")
question_label.place(relx=0.5, rely=0.5, anchor="center")

# Botones de navegación
prev_button = tk.Button(root, text="←", command=prev_question)
prev_button.place(relx=0.3, rely=0.75)

next_button = tk.Button(root, text="→", command=next_question)
next_button.place(relx=0.7, rely=0.75)

# Mostrar primera pregunta
show_question(current_index)

# Ejecutar la aplicación
root.mainloop()

