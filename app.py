import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os

class VisorPresentacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Presentación de Preguntas")
        
        # Configurar tema y colores
        self.root.configure(bg='#2c3e50')
        self.root.state('zoomed')  # Iniciar maximizado
        
        # Variables
        self.preguntas = []
        self.indice_actual = 0
        self.imagen_logo = None
        
        # Frame principal
        self.frame_principal = tk.Frame(root, bg='#2c3e50')
        self.frame_principal.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Panel izquierdo (Logo)
        self.frame_logo = tk.Frame(
            self.frame_principal,
            bg='#34495e',
            highlightbackground='#1a252f',
            highlightthickness=2
        )
        self.frame_logo.pack(side='left', fill='both', expand=True, padx=(0,20))
        
        # Botón de carga de logo
        self.btn_cargar = tk.Button(
            self.frame_logo,
            text="+",
            command=self.cargar_logo,
            font=('Helvetica', 30, 'bold'),
            bg='#3498db',
            fg='white',
            relief='flat',
            width=2,
            cursor='hand2'
        )
        self.btn_cargar.pack(pady=(20,0))
        
        # Área del logo
        self.lbl_logo = tk.Label(
            self.frame_logo,
            bg='#34495e',
            width=50,
            height=25
        )
        self.lbl_logo.pack(pady=20, padx=20, expand=True)
        
        # Panel derecho (Preguntas)
        self.frame_preguntas = tk.Frame(
            self.frame_principal,
            bg='#ecf0f1',
            highlightbackground='#bdc3c7',
            highlightthickness=1
        )
        self.frame_preguntas.pack(side='right', fill='both', expand=True)
        
        # Área de texto para preguntas
        self.texto_pregunta = tk.Text(
            self.frame_preguntas,
            font=('Helvetica', 36, 'bold'),
            fg='#2c3e50',
            bg='#ecf0f1',
            relief='flat',
            height=8,
            width=30,
            wrap='word'
        )
        self.texto_pregunta.pack(expand=True, fill='both', padx=30, pady=30)
        self.texto_pregunta.tag_configure('center', justify='center')
        self.texto_pregunta.tag_add('center', '1.0', 'end')
        
        # Panel de control
        self.frame_control = tk.Frame(self.frame_preguntas, bg='#ecf0f1')
        self.frame_control.pack(side='bottom', fill='x', pady=20)
        
        # Botón cargar preguntas
        self.btn_cargar_txt = tk.Button(
            self.frame_control,
            text="Cargar TXT",
            command=self.cargar_preguntas,
            font=('Helvetica', 12),
            bg='#3498db',
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10
        )
        self.btn_cargar_txt.pack(side='left', padx=30)
        
        # Navegación
        self.frame_nav = tk.Frame(self.frame_control, bg='#ecf0f1')
        self.frame_nav.pack(side='right', padx=30)
        
        self.btn_anterior = tk.Button(
            self.frame_nav,
            text="←",
            command=self.anterior_pregunta,
            font=('Helvetica', 24),
            bg='#2c3e50',
            fg='white',
            relief='flat',
            cursor='hand2',
            width=2,
            state='disabled'
        )
        self.btn_anterior.pack(side='left', padx=10)
        
        self.lbl_contador = tk.Label(
            self.frame_nav,
            text="0 / 0",
            font=('Helvetica', 14),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.lbl_contador.pack(side='left', padx=20)
        
        self.btn_siguiente = tk.Button(
            self.frame_nav,
            text="→",
            command=self.siguiente_pregunta,
            font=('Helvetica', 24),
            bg='#2c3e50',
            fg='white',
            relief='flat',
            cursor='hand2',
            width=2,
            state='disabled'
        )
        self.btn_siguiente.pack(side='left', padx=10)

    def cargar_logo(self):
        """Cargar y mostrar logo"""
        tipos = [("Archivos PNG", "*.png"), ("Todos los archivos", "*.*")]
        ruta = filedialog.askopenfilename(filetypes=tipos)
        if ruta:
            try:
                imagen = Image.open(ruta)
                # Calcular tamaño manteniendo proporción
                ancho = self.frame_logo.winfo_width() - 40
                alto = self.frame_logo.winfo_height() - 100
                ratio = min(ancho/imagen.width, alto/imagen.height)
                nuevo_ancho = int(imagen.width * ratio)
                nuevo_alto = int(imagen.height * ratio)
                imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
                self.imagen_logo = ImageTk.PhotoImage(imagen)
                self.lbl_logo.config(image=self.imagen_logo)
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")

    def cargar_preguntas(self):
        """Cargar preguntas desde archivo TXT"""
        tipos = [("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        ruta = filedialog.askopenfilename(filetypes=tipos)
        if ruta:
            try:
                with open(ruta, 'r', encoding='utf-8') as archivo:
                    self.preguntas = [linea.strip() for linea in archivo if linea.strip()]
                if self.preguntas:
                    self.indice_actual = 0
                    self.mostrar_pregunta_actual()
                    self.actualizar_botones()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error al cargar el archivo: {str(e)}")

    def mostrar_pregunta_actual(self):
        """Mostrar la pregunta actual"""
        if 0 <= self.indice_actual < len(self.preguntas):
            self.texto_pregunta.delete('1.0', tk.END)
            self.texto_pregunta.insert('1.0', self.preguntas[self.indice_actual])
            self.texto_pregunta.tag_add('center', '1.0', 'end')
            self.lbl_contador.config(text=f"{self.indice_actual + 1} / {len(self.preguntas)}")

    def siguiente_pregunta(self):
        """Mostrar siguiente pregunta"""
        if self.indice_actual < len(self.preguntas) - 1:
            self.indice_actual += 1
            self.mostrar_pregunta_actual()
            self.actualizar_botones()

    def anterior_pregunta(self):
        """Mostrar pregunta anterior"""
        if self.indice_actual > 0:
            self.indice_actual -= 1
            self.mostrar_pregunta_actual()
            self.actualizar_botones()

    def actualizar_botones(self):
        """Actualizar estado de los botones de navegación"""
        self.btn_anterior['state'] = 'normal' if self.indice_actual > 0 else 'disabled'
        self.btn_siguiente['state'] = 'normal' if self.indice_actual < len(self.preguntas) - 1 else 'disabled'

if __name__ == "__main__":
    root = tk.Tk()
    app = VisorPresentacion(root)
    root.mainloop()
