import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os

class VisorPresentacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Visor de Presentación")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.preguntas = []
        self.indice_actual = 0
        self.imagen_logo = None
        
        # Frame principal con padding
        self.frame_principal = tk.Frame(root, bg='#2c3e50')
        self.frame_principal.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Frame para el logo con efecto de sombra
        self.frame_logo = tk.Frame(
            self.frame_principal,
            bg='#34495e',
            highlightbackground='#1a252f',
            highlightthickness=2
        )
        self.frame_logo.pack(side='left', padx=20, fill='both')
        
        # Botón minimalista para cargar logo
        self.btn_cargar = tk.Button(
            self.frame_logo,
            text="+",
            command=self.cargar_logo,
            font=('Helvetica', 24),
            bg='#34495e',
            fg='white',
            relief='flat',
            width=2,
            height=1,
            cursor='hand2'
        )
        self.btn_cargar.pack(pady=(20,0))
        
        # Label para el logo con borde redondeado
        self.lbl_logo = tk.Label(
            self.frame_logo,
            bg='#34495e',
            width=40,
            height=20
        )
        self.lbl_logo.pack(pady=20, padx=20)
        
        # Frame para el contenido con efecto de cristal
        self.frame_contenido = tk.Frame(
            self.frame_principal,
            bg='#ecf0f1',
            highlightbackground='#bdc3c7',
            highlightthickness=1
        )
        self.frame_contenido.pack(side='right', expand=True, fill='both', padx=20)
        
        # Campo de entrada para preguntas
        self.entrada_pregunta = tk.Text(
            self.frame_contenido,
            font=('Helvetica', 32, 'bold'),
            fg='#2c3e50',
            bg='#ecf0f1',
            relief='flat',
            height=4,
            width=30
        )
        self.entrada_pregunta.pack(expand=True, padx=30, pady=30)
        
        # Frame para botones de control
        self.frame_control = tk.Frame(self.frame_contenido, bg='#ecf0f1')
        self.frame_control.pack(side='bottom', pady=20)
        
        # Botón para cargar preguntas desde archivo
        self.btn_cargar_preguntas = tk.Button(
            self.frame_control,
            text="Cargar TXT",
            command=self.cargar_preguntas,
            font=('Helvetica', 12),
            bg='#3498db',
            fg='white',
            relief='flat',
            cursor='hand2'
        )
        self.btn_cargar_preguntas.pack(side='left', padx=10)
        
        # Botones de navegación
        self.btn_anterior = tk.Button(
            self.frame_control,
            text="←",
            command=self.anterior_slide,
            font=('Helvetica', 24),
            bg='#ecf0f1',
            fg='#2c3e50',
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.btn_anterior.pack(side='left', padx=20)
        
        self.btn_siguiente = tk.Button(
            self.frame_control,
            text="→",
            command=self.siguiente_slide,
            font=('Helvetica', 24),
            bg='#ecf0f1',
            fg='#2c3e50',
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.btn_siguiente.pack(side='left', padx=20)
        
    def cargar_logo(self):
        ruta_archivo = filedialog.askopenfilename(
            filetypes=[("Archivos PNG", "*.png")]
        )
        if ruta_archivo:
            imagen = Image.open(ruta_archivo)
            imagen.thumbnail((400, 400))
            self.imagen_logo = ImageTk.PhotoImage(imagen)
            self.lbl_logo.configure(image=self.imagen_logo)
    
    def cargar_preguntas(self):
        ruta_archivo = filedialog.askopenfilename(
            filetypes=[("Archivos de texto", "*.txt")]
        )
        if ruta_archivo:
            with open(ruta_archivo, 'r', encoding='utf-8') as file:
                self.preguntas = file.readlines()
            if self.preguntas:
                self.indice_actual = 0
                self.entrada_pregunta.delete('1.0', tk.END)
                self.entrada_pregunta.insert('1.0', self.preguntas[0].strip())
                self.actualizar_estado_botones()
    
    def siguiente_slide(self):
        if self.preguntas and self.indice_actual < len(self.preguntas) - 1:
            self.indice_actual += 1
            self.entrada_pregunta.delete('1.0', tk.END)
            self.entrada_pregunta.insert('1.0', self.preguntas[self.indice_actual].strip())
            self.actualizar_estado_botones()
    
    def anterior_slide(self):
        if self.preguntas and self.indice_actual > 0:
            self.indice_actual -= 1
            self.entrada_pregunta.delete('1.0', tk.END)
            self.entrada_pregunta.insert('1.0', self.preguntas[self.indice_actual].strip())
            self.actualizar_estado_botones()
    
    def actualizar_estado_botones(self):
        self.btn_anterior['state'] = 'normal' if self.indice_actual > 0 else 'disabled'
        self.btn_siguiente['state'] = 'normal' if self.indice_actual < len(self.preguntas) - 1 else 'disabled'

if __name__ == "__main__":
    root = tk.Tk()
    app = VisorPresentacion(root)
    root.mainloop()
