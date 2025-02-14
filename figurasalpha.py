import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt  # Para graficar las figuras
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math  # Para operaciones matemáticas avanzadas
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import importlib.util
import subprocess
import sys
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Constantes globales
UNIDADES_VALIDAS = ["cm", "m", "in", "ft"]
CONV_FACTORS = {"cm": 1, "m": 100, "in": 2.54, "ft": 30.48}


def check_dependencies(dependencies):
    missing = []
    for dep in dependencies:
        if importlib.util.find_spec(dep) is None:
            missing.append(dep)
    if missing:
        # Se crea una ventana oculta para poder usar messagebox
        root = tk.Tk()
        root.withdraw()
        msg = "Faltan las siguientes dependencias:\n" + "\n".join(missing)
        msg += "\n\n¿Desea instalarlas?"
        if messagebox.askyesno("Dependencias faltantes", msg):
            try:
                for dep in missing:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                messagebox.showinfo("Instalación completada", "Las dependencias se han instalado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al instalar las dependencias:\n{e}")
                sys.exit(1)
        else:
            messagebox.showerror("Error", "No se pueden ejecutar las funcionalidades sin las dependencias necesarias.")
            sys.exit(1)

# Lista de dependencias necesarias para tu aplicación
dependencies = ["matplotlib", "numpy", "reportlab"]
# Verificar dependencias antes de iniciar la GUI
check_dependencies(dependencies)

# convewrtir a cm  las unidades
def convertir_a_cm(valor, unidad):
    if unidad not in CONV_FACTORS:
        raise ValueError(f"Unidad no válida: {unidad}. Las unidades válidas son {UNIDADES_VALIDAS}.")
    return valor * CONV_FACTORS[unidad]

def exportar_a_pdf(resultado_texto, fig):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    if file_path:
        try:
            # Crear el canvas del PDF con ReportLab
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            # Escribir el texto en la primera página del PDF
            textobject = c.beginText(40, height - 50)
            textobject.setFont("Helvetica", 12)
            for linea in resultado_texto.split("\n"):
                textobject.textLine(linea)
            c.drawText(textobject)

            # Agregar una nueva página para la figura
            c.showPage()

            # Guardar la figura en un archivo temporal (PNG)
            img_path = file_path.replace(".pdf", "_figura.png")
            fig.savefig(img_path)

            # Insertar la imagen en el PDF, centrada en la página
            img_width = 400
            img_height = 400
            c.drawImage(img_path, (width - img_width) / 2, (height - img_height) / 2, width=img_width, height=img_height)
            c.save()

            # Eliminar el archivo temporal de la imagen
            if os.path.exists(img_path):
                os.remove(img_path)

            messagebox.showinfo("Exportación", "Resultados exportados exitosamente en PDF.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")

class Triangulo:
    def __init__(self, base, altura, unidad="cm"):
        self.unidad = unidad
        self.base = convertir_a_cm(base, unidad)
        self.altura = convertir_a_cm(altura, unidad)
        self.hipotenusa = math.sqrt(self.base ** 2 + self.altura ** 2)
        self.area = 0.5 * self.base * self.altura
        self.perimetro = self.base + self.altura + self.hipotenusa
        self.tipo = self.clasificar()  # Llama al método clasificar

    def clasificar(self):
        if self.base == self.altura:
            return "Isósceles"
        else:
            return "Escaleno"


# Ventana principal
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora Geométrica")
        self.root.geometry("900x900")

        # Inicializar el estilo global
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configurar_estilos()

        # Contenedor principal
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Mostrar el menú principal al iniciar
        self.mostrar_menu_principal()

    def configurar_estilos(self):
        """Configura estilos personalizados para los widgets."""
        self.style.configure(
            "TButton",
            font=("Arial", 12),
            padding=10,
            background="#141b1e",
            foreground="white"
        )
        self.style.map(
            "TButton",
            background=[("active", "#8ccf7e")]
        )

    def exportar_resultados(self, resultado):
        import tkinter.filedialog as filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(resultado)
                messagebox.showinfo("Exportar Resultados", "Resultados exportados exitosamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar: {e}")

    def cambiar_tema_interfaz(self):
        temas_disponibles = ["clam", "alt", "default", "classic"]
        tema_seleccionado = tk.StringVar(value=temas_disponibles[0])
        ventana_tema = tk.Toplevel(self.root)
        ventana_tema.title("Cambiar Tema")
        ventana_tema.geometry("300x200")
        ttk.Label(ventana_tema, text="Selecciona un tema:").pack(pady=10)
        for tema in temas_disponibles:
            ttk.Radiobutton(ventana_tema, text=tema.capitalize(), variable=tema_seleccionado, value=tema).pack(
                anchor=tk.W)

        def aplicar_tema():
            self.style.theme_use(tema_seleccionado.get())
            ventana_tema.destroy()

        ttk.Button(ventana_tema, text="Aplicar", command=aplicar_tema).pack(pady=10)

    # Dividir el frame para mostrar resultados en en el mismo frame
    def dividir_frame(self):
        resultados_frame = ttk.Frame(self.main_frame)
        resultados_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # Columna izquierda

        figura_frame = ttk.Frame(self.main_frame)
        figura_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")  # Columna derecha

        # Configurar las proporciones de las columnas
        self.main_frame.grid_columnconfigure(0, weight=1)  # Resultados
        self.main_frame.grid_columnconfigure(1, weight=2)  # Figura (más ancho)

        return resultados_frame, figura_frame

    def limpiar_contenido(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    """Muestra el menú principal."""
    def mostrar_menu_principal(self):
        self.limpiar_contenido()

        ttk.Label(self.main_frame, text="Selecciona una categoría:", font=("Arial", 14)).pack(pady=10)
        ttk.Button(self.main_frame, text="Figuras 2D", command=self.mostrar_menu_2d).pack(pady=5)
        ttk.Button(self.main_frame, text="Figuras 3D", command=self.mostrar_menu_3d).pack(pady=5)
        ttk.Button(self.main_frame, text="Cambiar Tema", command=self.cambiar_tema_interfaz).pack(pady=5)
        ttk.Button(self.main_frame, text="Contacto", command=self.mostrar_contacto).pack(pady=5)
        ttk.Button(self.main_frame, text="Salir", command=self.root.quit).pack(pady=5)


    """Muestra el menú de figuras 2D."""
    def mostrar_menu_2d(self):
        self.limpiar_contenido()
        ttk.Label(self.main_frame, text="Selecciona una figura 2D:", font=("Arial", 12)).pack(pady=10)
        ttk.Button(self.main_frame, text="Triángulo", command=self.calcular_triangulo).pack(pady=5)
        ttk.Button(self.main_frame, text="Cuadrilátero", command=self.calcular_cuadrilatero).pack(pady=5)
        ttk.Button(self.main_frame, text="Círculo", command=self.calcular_circulo).pack(pady=5)
        ttk.Button(self.main_frame, text="Polígono Regular", command=self.calcular_poligono_regular).pack(pady=5)
        ttk.Button(self.main_frame, text="Elipse", command=self.calcular_elipse).pack(pady=5)
        ttk.Button(self.main_frame, text="Trapecio", command=self.calcular_trapecio).pack(pady=5)
        ttk.Button(self.main_frame, text="Paralelogramo", command=self.calcular_paralelogramo).pack(pady=5)
        ttk.Button(self.main_frame, text="Rombo", command=self.calcular_rombo).pack(pady=5)
        ttk.Button(self.main_frame, text="Sector Circular", command=self.calcular_sector_circular).pack(pady=5)
        ttk.Button(self.main_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=5)

    """Muestra el menú de figuras 3D."""
    def mostrar_menu_3d(self):
        self.limpiar_contenido()
        ttk.Label(self.main_frame, text="Selecciona una figura 3D:", font=("Arial", 12)).pack(pady=10)
        ttk.Button(self.main_frame, text="Cubo", command=self.calcular_cubo).pack(pady=5)
        ttk.Button(self.main_frame, text="Esfera", command=self.calcular_esfera).pack(pady=5)
        ttk.Button(self.main_frame, text="Pirámide", command=self.calcular_piramide).pack(pady=5)
        ttk.Button(self.main_frame, text="Prisma", command=self.calcular_prisma).pack(pady=5)
        ttk.Button(self.main_frame, text="Cono", command=self.calcular_cono).pack(pady=5)
        ttk.Button(self.main_frame, text="Cilindro", command=self.calcular_cilindro).pack(pady=5)
        ttk.Button(self.main_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=5)

    # contacyo
    def mostrar_contacto(self):
        self.limpiar_contenido()
        ttk.Label(self.main_frame, text="Información de Contacto", font=("Arial", 14)).pack(pady=10)
        ttk.Label(self.main_frame, text="Nombre: José Ángel Sebastián").pack(pady=5)
        ttk.Label(self.main_frame, text="WhatsApp: 6367000992").pack(pady=5)
        ttk.Label(self.main_frame, text="Correo: nooker106@gmail.com").pack(pady=5)
        ttk.Label(self.main_frame, text="Más proyectos: ", font=("Arial", 12)).pack(pady=5)
        link = ttk.Label(self.main_frame, text="GitHub", foreground="blue", cursor="hand2")
        link.pack(pady=5)
        link.bind("<Button-1>", lambda e: self.abrir_github())
        ttk.Button(self.main_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=5)

    def abrir_github(self):
        import webbrowser
        webbrowser.open("https://github.com/MNooker")


#calculos figuras 2d
    def calcular_triangulo(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        resultados_frame, figura_frame = self.dividir_frame()
        ttk.Label(resultados_frame, text="Base:").pack()
        self.base_entry = ttk.Entry(resultados_frame)
        self.base_entry.pack()
        ttk.Label(resultados_frame, text="Altura:").pack()
        self.altura_entry = ttk.Entry(resultados_frame)
        self.altura_entry.pack()
        ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_triangulo(resultados_frame, figura_frame)).pack(pady=10)
        ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=5)

    def mostrar_resultado_triangulo(self, resultados_frame, figura_frame):
        try:
            base = float(self.base_entry.get())
            altura = float(self.altura_entry.get())
            if base <= 0 or altura <= 0:
                messagebox.showerror("Error", "Los valores deben ser mayores que cero.")
                return
            area = 0.5 * base * altura
            perimetro = base + altura + math.sqrt(base ** 2 + altura ** 2)
            resultado_texto = f"Área: {area:.2f} cm²\nPerímetro: {perimetro:.2f} cm"
            for widget in resultados_frame.winfo_children(): widget.destroy()
            ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
            ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
            botones_frame = ttk.Frame(resultados_frame)
            botones_frame.pack(pady=10)
            ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_triangulo).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_2d).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
            self.dibujar_triangulo(figura_frame, base, altura)
        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_triangulo(self, frame, base, altura):
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.plot([0, base, 0, 0], [0, 0, altura, 0], marker="o")
        ax.set_title("Triángulo Rectángulo")
        ax.set_xlabel("Base (cm)")
        ax.set_ylabel("Altura (cm)")
        ax.grid(True)
        ax.axis("equal")
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return fig


    def calcular_cuadrilatero(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        resultados_frame, figura_frame = self.dividir_frame()
        ttk.Label(resultados_frame, text="Lado 1:").pack(pady=5)
        self.lado1_entry = ttk.Entry(resultados_frame)
        self.lado1_entry.pack()
        ttk.Label(resultados_frame, text="Lado 2:").pack(pady=5)
        self.lado2_entry = ttk.Entry(resultados_frame)
        self.lado2_entry.pack()
        ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_cuadrilatero(resultados_frame, figura_frame)).pack(pady=10)
        ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=5)

    def mostrar_resultado_cuadrilatero(self, resultados_frame, figura_frame):
        try:
            lado1 = float(self.lado1_entry.get())
            lado2 = float(self.lado2_entry.get())
            if lado1 <= 0 or lado2 <= 0:
                messagebox.showerror("Error", "Los valores deben ser mayores que cero.")
                return
            area = lado1 * lado2
            perimetro = 2 * (lado1 + lado2)
            resultado_texto = f"Área: {area:.2f} cm²\nPerímetro: {perimetro:.2f} cm"
            for widget in resultados_frame.winfo_children(): widget.destroy()
            ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
            ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
            botones_frame = ttk.Frame(resultados_frame)
            botones_frame.pack(pady=10)
            ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_cuadrilatero).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_2d).pack(side=tk.LEFT, padx=5)
            fig = self.dibujar_cuadrilatero(figura_frame, lado1, lado2)
            ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_cuadrilatero(self, frame, lado1, lado2):
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.plot([0, lado1, lado1, 0, 0], [0, 0, lado2, lado2, 0], marker="o")
        ax.set_title("Cuadrilátero")
        ax.set_xlabel("Lado 1 (cm)")
        ax.set_ylabel("Lado 2 (cm)")
        ax.grid(True)
        ax.axis("equal")
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return fig


    def calcular_circulo(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        resultados_frame, figura_frame = self.dividir_frame()
        ttk.Label(resultados_frame, text="Radio:").pack(pady=5)
        self.radio_entry = ttk.Entry(resultados_frame)
        self.radio_entry.pack()
        ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_circulo(resultados_frame, figura_frame)).pack(pady=10)
        ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_2d).pack(pady=5)

    def mostrar_resultado_circulo(self, resultados_frame, figura_frame):
        try:
            radio = float(self.radio_entry.get())
            if radio <= 0:
                messagebox.showerror("Error", "El radio debe ser mayor que cero.")
                return
            area = math.pi * radio ** 2
            perimetro = 2 * math.pi * radio
            resultado_texto = f"Área: {area:.2f} cm²\nPerímetro: {perimetro:.2f} cm"
            for widget in resultados_frame.winfo_children(): widget.destroy()
            ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
            ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
            botones_frame = ttk.Frame(resultados_frame)
            botones_frame.pack(pady=10)
            ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_circulo).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_2d).pack(side=tk.LEFT, padx=5)
            fig = self.dibujar_circulo(figura_frame, radio)
            ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_circulo(self, frame, radio):
        fig, ax = plt.subplots(figsize=(4, 4))
        circulo = plt.Circle((0, 0), radio, color='b', fill=False)
        ax.add_patch(circulo)
        ax.set_xlim(-radio - 1, radio + 1)
        ax.set_ylim(-radio - 1, radio + 1)
        ax.set_aspect('equal', adjustable='datalim')
        ax.set_title("Círculo")
        ax.grid(True)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return fig


    def calcular_poligono_regular(self):
        self.limpiar_contenido()
        resultados_frame, figura_frame = self.dividir_frame()
        ttk.Label(resultados_frame, text="Número de lados:").pack(pady=5)
        self.n_lados_entry = ttk.Entry(resultados_frame)
        self.n_lados_entry.pack()
        ttk.Label(resultados_frame, text="Longitud del lado:").pack(pady=5)
        self.longitud_lado_entry = ttk.Entry(resultados_frame)
        self.longitud_lado_entry.pack()
        ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_poligono_regular(resultados_frame, figura_frame)).pack(pady=10)
        ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_2d).pack(pady=5)

    def calcular_datos_poligono_regular(self, n_lados, longitud_lado):
        area = (n_lados * longitud_lado ** 2) / (4 * math.tan(math.pi / n_lados))
        perimetro = n_lados * longitud_lado
        return longitud_lado, area, perimetro

    def mostrar_resultado_poligono_regular(self, resultados_frame, figura_frame):
        try:
            n_lados = int(self.n_lados_entry.get())
            longitud_lado = float(self.longitud_lado_entry.get())
            if n_lados < 3:
                messagebox.showerror("Error", "El número de lados debe ser al menos 3.")
                return
            if longitud_lado <= 0:
                messagebox.showerror("Error", "La longitud del lado debe ser mayor que cero.")
                return

            longitud_cm, area, perimetro = self.calcular_datos_poligono_regular(n_lados, longitud_lado)
            resultado_texto = (
                f"Área: {area:.2f} cm²\n"
                f"Perímetro: {perimetro:.2f} cm"
            )
            for widget in resultados_frame.winfo_children(): widget.destroy()
            ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
            ttk.Label(resultados_frame, text=resultado_texto, justify="left").pack(pady=5)
            botones_frame = ttk.Frame(resultados_frame)
            botones_frame.pack(pady=10)
            ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_2d).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_poligono_regular).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
            self.dibujar_poligono_regular(figura_frame, n_lados, longitud_cm)

        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_poligono_regular(self, frame, n_lados, longitud_lado):
        angulo = 2 * np.pi / n_lados
        x = [longitud_lado * np.cos(i * angulo) for i in range(n_lados)]
        y = [longitud_lado * np.sin(i * angulo) for i in range(n_lados)]
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.plot(x + [x[0]], y + [y[0]], marker="o")
        ax.set_title(f"Polígono Regular ({n_lados} lados)")
        ax.set_xlabel("X (cm)")
        ax.set_ylabel("Y (cm)")
        ax.grid(True)
        ax.axis("equal")

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()


    def calcular_elipse(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        resultados_frame, figura_frame = self.dividir_frame()
        ttk.Label(resultados_frame, text="Semieje Mayor:").pack(pady=5)
        self.semieje_mayor_entry = ttk.Entry(resultados_frame)
        self.semieje_mayor_entry.pack()
        ttk.Label(resultados_frame, text="Semieje Menor:").pack(pady=5)
        self.semieje_menor_entry = ttk.Entry(resultados_frame)
        self.semieje_menor_entry.pack()
        ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_elipse(resultados_frame, figura_frame)).pack(pady=10)
        ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_2d).pack(pady=5)

    def mostrar_resultado_elipse(self, resultados_frame, figura_frame):
        try:
            a = float(self.semieje_mayor_entry.get())
            b = float(self.semieje_menor_entry.get())
            if a <= 0 or b <= 0:
                messagebox.showerror("Error", "Los valores deben ser mayores que cero.")
                return
            area = math.pi * a * b
            # Aproximación para el perímetro de una elipse (fórmula de Ramanujan)
            perimetro = math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))
            resultado_texto = f"Área: {area:.2f} cm²\nPerímetro aproximado: {perimetro:.2f} cm"
            for widget in resultados_frame.winfo_children(): widget.destroy()
            ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
            ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
            botones_frame = ttk.Frame(resultados_frame)
            botones_frame.pack(pady=10)
            ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_elipse).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
            fig = self.dibujar_elipse(figura_frame, a, b)
            ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_elipse(self, frame, a, b):
        theta = np.linspace(0, 2 * np.pi, 100)
        x = a * np.cos(theta)
        y = b * np.sin(theta)
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.plot(x, y)
        ax.set_title("Elipse")
        ax.set_xlabel("Semieje Mayor (cm)")
        ax.set_ylabel("Semieje Menor (cm)")
        ax.grid(True)
        ax.axis("equal")
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return fig


    def calcular_trapecio(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        resultados_frame, figura_frame = self.dividir_frame()
        ttk.Label(resultados_frame, text="Base Mayor:").pack(pady=5)
        self.base_mayor_entry = ttk.Entry(resultados_frame)
        self.base_mayor_entry.pack()
        ttk.Label(resultados_frame, text="Base Menor:").pack(pady=5)
        self.base_menor_entry = ttk.Entry(resultados_frame)
        self.base_menor_entry.pack()
        ttk.Label(resultados_frame, text="Altura:").pack(pady=5)
        self.altura_entry = ttk.Entry(resultados_frame)
        self.altura_entry.pack()
        ttk.Label(resultados_frame, text="Lado No Paralelo:").pack(pady=5)
        self.lado_no_paralelo_entry = ttk.Entry(resultados_frame)
        self.lado_no_paralelo_entry.pack()
        ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_trapecio(resultados_frame, figura_frame)).pack(pady=10)
        ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_2d).pack(pady=5)

    def mostrar_resultado_trapecio(self, resultados_frame, figura_frame):
        try:
            base_mayor = float(self.base_mayor_entry.get())
            base_menor = float(self.base_menor_entry.get())
            altura = float(self.altura_entry.get())
            lado_no_paralelo = float(self.lado_no_paralelo_entry.get())
            if base_mayor <= 0 or base_menor <= 0 or altura <= 0 or lado_no_paralelo <= 0:
                messagebox.showerror("Error", "Los valores deben ser mayores que cero.")
                return
            area = ((base_mayor + base_menor) * altura) / 2
            perimetro = base_mayor + base_menor + 2 * lado_no_paralelo
            resultado_texto = f"Área: {area:.2f} cm²\nPerímetro: {perimetro:.2f} cm"
            for widget in resultados_frame.winfo_children(): widget.destroy()
            ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
            ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
            botones_frame = ttk.Frame(resultados_frame)
            botones_frame.pack(pady=10)
            ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_trapecio).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
            fig = self.dibujar_trapecio(figura_frame, base_mayor, base_menor, altura)
            ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_trapecio(self, frame, base_mayor, base_menor, altura):
        x = [0, base_mayor, base_mayor - (base_mayor - base_menor) / 2, (base_mayor - base_menor) / 2, 0]
        y = [0, 0, altura, altura, 0]
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.plot(x, y, marker="o")
        ax.set_title("Trapecio")
        ax.set_xlabel("Base (cm)")
        ax.set_ylabel("Altura (cm)")
        ax.grid(True)
        ax.axis("equal")
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return fig


    def calcular_rombo(self):
            for widget in self.main_frame.winfo_children(): widget.destroy()
            resultados_frame, figura_frame = self.dividir_frame()
            ttk.Label(resultados_frame, text="Diagonal Mayor:").pack(pady=5)
            self.diagonal_mayor_entry = ttk.Entry(resultados_frame)
            self.diagonal_mayor_entry.pack()
            ttk.Label(resultados_frame, text="Diagonal Menor:").pack(pady=5)
            self.diagonal_menor_entry = ttk.Entry(resultados_frame)
            self.diagonal_menor_entry.pack()
            ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_rombo(resultados_frame, figura_frame)).pack(pady=10)
            ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_2d).pack(pady=5)

    def mostrar_resultado_rombo(self, resultados_frame, figura_frame):
            try:
                d_mayor = float(self.diagonal_mayor_entry.get())
                d_menor = float(self.diagonal_menor_entry.get())
                if d_mayor <= 0 or d_menor <= 0:
                    messagebox.showerror("Error", "Los valores deben ser mayores que cero.")
                    return
                area = (d_mayor * d_menor) / 2
                lado = math.sqrt((d_mayor / 2) ** 2 + (d_menor / 2) ** 2)
                perimetro = 4 * lado
                resultado_texto = f"Área: {area:.2f} cm²\nPerímetro: {perimetro:.2f} cm"
                for widget in resultados_frame.winfo_children(): widget.destroy()
                ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
                ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
                botones_frame = ttk.Frame(resultados_frame)
                botones_frame.pack(pady=10)
                ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_rombo).pack(side=tk.LEFT, padx=5)
                ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
                fig = self.dibujar_rombo(figura_frame, d_mayor, d_menor)
                ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
            except ValueError:
                messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_rombo(self, frame, d_mayor, d_menor):
            x = [0, d_mayor / 2, 0, -d_mayor / 2, 0]
            y = [d_menor / 2, 0, -d_menor / 2, 0, d_menor / 2]
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.plot(x, y, marker="o")
            ax.set_title("Rombo")
            ax.set_xlabel("Diagonal Mayor (cm)")
            ax.set_ylabel("Diagonal Menor (cm)")
            ax.grid(True)
            ax.axis("equal")
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
            return fig


    def calcular_sector_circular(self):
            for widget in self.main_frame.winfo_children(): widget.destroy()
            resultados_frame, figura_frame = self.dividir_frame()
            ttk.Label(resultados_frame, text="Radio:").pack(pady=5)
            self.radio_entry = ttk.Entry(resultados_frame)
            self.radio_entry.pack()
            ttk.Label(resultados_frame, text="Ángulo Central (grados):").pack(pady=5)
            self.angulo_entry = ttk.Entry(resultados_frame)
            self.angulo_entry.pack()
            ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_sector(resultados_frame, figura_frame)).pack(pady=10)
            ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_2d).pack(pady=5)

    def mostrar_resultado_sector(self, resultados_frame, figura_frame):
            try:
                radio = float(self.radio_entry.get())
                angulo = float(self.angulo_entry.get())
                if radio <= 0 or angulo <= 0 or angulo > 360:
                    messagebox.showerror("Error", "El radio debe ser mayor que cero y el ángulo entre 0 y 360 grados.")
                    return
                area = (math.pi * radio ** 2 * angulo) / 360
                longitud_arco = (2 * math.pi * radio * angulo) / 360
                resultado_texto = f"Área: {area:.2f} cm²\nLongitud del Arco: {longitud_arco:.2f} cm"
                for widget in resultados_frame.winfo_children(): widget.destroy()
                ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
                ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
                botones_frame = ttk.Frame(resultados_frame)
                botones_frame.pack(pady=10)
                ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_sector_circular).pack( side=tk.LEFT, padx=5)
                ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
                fig = self.dibujar_sector_circular(figura_frame, radio, angulo)
                ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
            except ValueError:
                messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_sector_circular(self, frame, radio, angulo):
            theta = np.linspace(0, np.radians(angulo), 100)
            x = radio * np.cos(theta)
            y = radio * np.sin(theta)
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.plot(x, y, color="b")
            # Dibujar los radios del sector
            ax.plot([0, radio], [0, 0], color="b")
            ax.plot([0, radio * np.cos(np.radians(angulo))], [0, radio * np.sin(np.radians(angulo))], color="b")
            ax.set_title("Sector Circular")
            ax.set_xlabel("X (cm)")
            ax.set_ylabel("Y (cm)")
            ax.grid(True)
            ax.axis("equal")
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
            return fig


    def calcular_paralelogramo(self):
            for widget in self.main_frame.winfo_children(): widget.destroy()
            resultados_frame, figura_frame = self.dividir_frame()
            ttk.Label(resultados_frame, text="Base:").pack(pady=5)
            self.base_entry = ttk.Entry(resultados_frame)
            self.base_entry.pack()
            ttk.Label(resultados_frame, text="Altura:").pack(pady=5)
            self.altura_entry = ttk.Entry(resultados_frame)
            self.altura_entry.pack()
            ttk.Label(resultados_frame, text="Ángulo (grados):").pack(pady=5)
            self.angulo_entry = ttk.Entry(resultados_frame)
            self.angulo_entry.pack()
            ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_paralelogramo(resultados_frame, figura_frame)).pack(pady=10)
            ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_2d).pack(pady=5)

    def mostrar_resultado_paralelogramo(self, resultados_frame, figura_frame):
            try:
                base = float(self.base_entry.get())
                altura = float(self.altura_entry.get())
                angulo = float(self.angulo_entry.get())
                if base <= 0 or altura <= 0 or angulo <= 0 or angulo >= 180:
                    messagebox.showerror("Error","La base y la altura deben ser mayores que cero y el ángulo debe estar entre 0 y 180 grados.")
                    return
                area = base * altura
                angulo_rad = math.radians(angulo)
                lado_lateral = altura / math.sin(angulo_rad)
                perimetro = 2 * (base + lado_lateral)
                resultado_texto = f"Área: {area:.2f} cm²\nPerímetro: {perimetro:.2f} cm"
                for widget in resultados_frame.winfo_children():
                    widget.destroy()
                ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
                ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
                botones_frame = ttk.Frame(resultados_frame)
                botones_frame.pack(pady=10)
                ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_paralelogramo).pack(
                    side=tk.LEFT, padx=5)
                ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT,
                                                                                                     padx=5)
                fig = self.dibujar_paralelogramo(figura_frame, base, altura, angulo)
                ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
            except ValueError:
                messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_paralelogramo(self, frame, base, altura, angulo):
            angulo_rad = math.radians(angulo)
            x1, y1 = 0, 0
            x2, y2 = base, 0
            x3, y3 = base + altura * math.cos(angulo_rad), altura * math.sin(angulo_rad)
            x4, y4 = altura * math.cos(angulo_rad), altura * math.sin(angulo_rad)
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.plot([x1, x2, x3, x4, x1], [y1, y2, y3, y4, y1], marker="o")
            ax.set_title("Paralelogramo")
            ax.set_xlabel("Base (cm)")
            ax.set_ylabel("Altura (cm)")
            ax.grid(True)
            ax.axis("equal")
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
            return fig

    #calculos figuras 3d
    def calcular_cubo(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        resultados_frame, figura_frame = self.dividir_frame()
        ttk.Label(resultados_frame, text="Lado:").pack(pady=5)
        self.lado_entry = ttk.Entry(resultados_frame)
        self.lado_entry.pack()
        ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_cubo(resultados_frame, figura_frame)).pack(pady=10)
        ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=5)

    def mostrar_resultado_cubo(self, resultados_frame, figura_frame):
        try:
            lado = float(self.lado_entry.get())
            if lado <= 0:
                messagebox.showerror("Error", "El lado debe ser mayor que cero.")
                return
            area = 6 * (lado ** 2)
            volumen = lado ** 3
            resultado_texto = (f"Lado: {lado:.2f} cm\n"
                               f"Área superficial: {area:.2f} cm²\n"
                               f"Volumen: {volumen:.2f} cm³")
            for widget in resultados_frame.winfo_children(): widget.destroy()
            ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
            ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
            botones_frame = ttk.Frame(resultados_frame)
            botones_frame.pack(pady=10)
            ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_cubo).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
            fig = self.dibujar_cubo(figura_frame, lado)
            ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
        except ValueError:
            messagebox.showerror("Error", "Ingresa un valor numérico válido.")

    def dibujar_cubo(self, frame, lado):
        fig = plt.figure(figsize=(4, 4))
        ax = fig.add_subplot(111, projection='3d')
        r = [-lado / 2, lado / 2]
        vertices = [
            [r[0], r[0], r[0]], [r[1], r[0], r[0]],
            [r[1], r[1], r[0]], [r[0], r[1], r[0]],
            [r[0], r[0], r[1]], [r[1], r[0], r[1]],
            [r[1], r[1], r[1]], [r[0], r[1], r[1]]
        ]
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],
            [4, 5], [5, 6], [6, 7], [7, 4],
            [0, 4], [1, 5], [2, 6], [3, 7]
        ]
        for edge in edges:
         ax.plot3D(*zip(vertices[edge[0]], vertices[edge[1]]), color="b")
        ax.set_title("Cubo")
        ax.set_xlabel("X (cm)")
        ax.set_ylabel("Y (cm)")
        ax.set_zlabel("Z (cm)")
        ax.set_xlim(-lado, lado)
        ax.set_ylim(-lado, lado)
        ax.set_zlim(-lado, lado)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return fig


    def calcular_esfera(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        resultados_frame, figura_frame = self.dividir_frame()
        ttk.Label(resultados_frame, text="Radio:").pack(pady=5)
        self.radio_entry = ttk.Entry(resultados_frame)
        self.radio_entry.pack()
        ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_esfera(resultados_frame, figura_frame)).pack(pady=10)
        ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=5)

    def mostrar_resultado_esfera(self, resultados_frame, figura_frame):
        try:
            radio = float(self.radio_entry.get())
            if radio <= 0:
                messagebox.showerror("Error", "El radio debe ser mayor que cero.")
                return
            area = 4 * math.pi * (radio ** 2)
            volumen = (4 / 3) * math.pi * (radio ** 3)
            resultado_texto = (f"Radio: {radio:.2f} cm\n"
                               f"Área superficial: {area:.2f} cm²\n"
                               f"Volumen: {volumen:.2f} cm³")
            for widget in resultados_frame.winfo_children(): widget.destroy()
            ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
            ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
            botones_frame = ttk.Frame(resultados_frame)
            botones_frame.pack(pady=10)
            ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_esfera).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
            fig = self.dibujar_esfera(figura_frame, radio)
            ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
        except ValueError:
            messagebox.showerror("Error", "Ingresa un valor numérico válido.")

    def dibujar_esfera(self, frame, radio):
        fig = plt.figure(figsize=(4, 4))
        ax = fig.add_subplot(111, projection='3d')
        u = np.linspace(0, 2 * math.pi, 100)
        v = np.linspace(0, math.pi, 100)
        x = radio * np.outer(np.cos(u), np.sin(v))
        y = radio * np.outer(np.sin(u), np.sin(v))
        z = radio * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x, y, z, color="b", alpha=0.6)
        ax.set_title("Esfera")
        ax.set_xlabel("X (cm)")
        ax.set_ylabel("Y (cm)")
        ax.set_zlabel("Z (cm)")
        ax.set_xlim(-radio, radio)
        ax.set_ylim(-radio, radio)
        ax.set_zlim(-radio, radio)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return fig


    def calcular_piramide(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        resultados_frame, figura_frame = self.dividir_frame()
        ttk.Label(resultados_frame, text="Lado de la base:").pack(pady=5)
        self.lado_base_entry = ttk.Entry(resultados_frame)
        self.lado_base_entry.pack()
        ttk.Label(resultados_frame, text="Altura:").pack(pady=5)
        self.altura_entry = ttk.Entry(resultados_frame)
        self.altura_entry.pack()
        ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_piramide(resultados_frame, figura_frame)).pack(pady=10)
        ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=5)

    def mostrar_resultado_piramide(self, resultados_frame, figura_frame):
        try:
            lado_base = float(self.lado_base_entry.get())
            altura = float(self.altura_entry.get())
            if lado_base <= 0 or altura <= 0:
                messagebox.showerror("Error", "Los valores deben ser mayores que cero.")
                return
            area_base = lado_base ** 2
            apotema = math.sqrt((lado_base / 2) ** 2 + altura ** 2)
            area_lateral = 4 * (0.5 * lado_base * apotema)
            area_total = area_base + area_lateral
            volumen = (area_base * altura) / 3
            resultado_texto = (f"Lado base: {lado_base:.2f} cm\n"
                               f"Altura: {altura:.2f} cm\n"
                               f"Área total: {area_total:.2f} cm²\n"
                               f"Volumen: {volumen:.2f} cm³")
            for widget in resultados_frame.winfo_children(): widget.destroy()
            ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
            ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
            botones_frame = ttk.Frame(resultados_frame)
            botones_frame.pack(pady=10)
            ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_piramide).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
            fig = self.dibujar_piramide(figura_frame, lado_base, altura)
            ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_piramide(self, frame, lado_base, altura):
        fig = plt.figure(figsize=(4, 4))
        ax = fig.add_subplot(111, projection='3d')
        vertices = [
            [-lado_base / 2, -lado_base / 2, 0],
            [lado_base / 2, -lado_base / 2, 0],
            [lado_base / 2, lado_base / 2, 0],
            [-lado_base / 2, lado_base / 2, 0],
            [0, 0, altura]
        ]
        faces = [
            [vertices[0], vertices[1], vertices[4]],
            [vertices[1], vertices[2], vertices[4]],
            [vertices[2], vertices[3], vertices[4]],
            [vertices[3], vertices[0], vertices[4]],
            vertices[:4]
        ]
        ax.add_collection3d(Poly3DCollection(faces, facecolors='cyan', linewidths=1, edgecolors='r', alpha=0.25))
        ax.set_title("Pirámide")
        ax.set_xlabel("X (cm)")
        ax.set_ylabel("Y (cm)")
        ax.set_zlabel("Z (cm)")
        ax.set_xlim(-lado_base, lado_base)
        ax.set_ylim(-lado_base, lado_base)
        ax.set_zlim(0, altura + 1)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return fig


    def calcular_cono(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        resultados_frame, figura_frame = self.dividir_frame()
        ttk.Label(resultados_frame, text="Radio de la base:").pack(pady=5)
        self.radio_entry = ttk.Entry(resultados_frame)
        self.radio_entry.pack()
        ttk.Label(resultados_frame, text="Altura:").pack(pady=5)
        self.altura_entry = ttk.Entry(resultados_frame)
        self.altura_entry.pack()
        ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_cono(resultados_frame, figura_frame)).pack(pady=10)
        ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=5)

    def mostrar_resultado_cono(self, resultados_frame, figura_frame):
        try:
            radio = float(self.radio_entry.get())
            altura = float(self.altura_entry.get())
            if radio <= 0 or altura <= 0:
                messagebox.showerror("Error", "Los valores deben ser mayores que cero.")
                return
            generatriz = math.sqrt(radio**2 + altura**2)
            area_base = math.pi * radio**2
            area_lateral = math.pi * radio * generatriz
            area_total = area_base + area_lateral
            volumen = (1/3) * area_base * altura
            resultado_texto = (f"Radio: {radio:.2f} cm\n"
                               f"Altura: {altura:.2f} cm\n"
                               f"Generatriz: {generatriz:.2f} cm\n"
                               f"Área total: {area_total:.2f} cm²\n"
                               f"Volumen: {volumen:.2f} cm³")
            for widget in resultados_frame.winfo_children():
                widget.destroy()
            ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
            ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
            botones_frame = ttk.Frame(resultados_frame)
            botones_frame.pack(pady=10)
            ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_cono).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
            fig = self.dibujar_cono(figura_frame, radio, altura)
            ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_cono(self, frame, radio, altura):
        fig = plt.figure(figsize=(4, 4))
        ax = fig.add_subplot(111, projection='3d')
        theta = np.linspace(0, 2 * math.pi, 100)
        x = radio * np.cos(theta)
        y = radio * np.sin(theta)
        z = np.zeros_like(x)
        ax.plot(x, y, z, color="b")
        ax.plot([0], [0], [altura], color="b", marker="o")
        for i in range(len(x)):
            ax.plot([x[i], 0], [y[i], 0], [0, altura], color="b")
        ax.set_title("Cono")
        ax.set_xlabel("X (cm)")
        ax.set_ylabel("Y (cm)")
        ax.set_zlabel("Z (cm)")
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return fig


    def calcular_prisma(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        resultados_frame, figura_frame = self.dividir_frame()
        ttk.Label(resultados_frame, text="Número de lados de la base:").pack(pady=5)
        self.n_lados_entry = ttk.Entry(resultados_frame)
        self.n_lados_entry.pack()
        ttk.Label(resultados_frame, text="Longitud de cada lado:").pack(pady=5)
        self.longitud_entry = ttk.Entry(resultados_frame)
        self.longitud_entry.pack()
        ttk.Label(resultados_frame, text="Altura del prisma:").pack(pady=5)
        self.altura_entry = ttk.Entry(resultados_frame)
        self.altura_entry.pack()
        ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_prisma(resultados_frame, figura_frame)).pack(pady=10)
        ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=5)

    def mostrar_resultado_prisma(self, resultados_frame, figura_frame):
        try:
            n_lados = int(self.n_lados_entry.get())
            longitud = float(self.longitud_entry.get())
            altura = float(self.altura_entry.get())
            if n_lados < 3 or longitud <= 0 or altura <= 0:
                messagebox.showerror("Error", "El número de lados debe ser >= 3 y los valores positivos.")
                return
            area_base = (n_lados * (longitud ** 2)) / (4 * math.tan(math.pi/n_lados))
            perimetro_base = n_lados * longitud
            area_lateral = perimetro_base * altura
            area_total = 2 * area_base + area_lateral
            volumen = area_base * altura
            resultado_texto = (f"Número de lados: {n_lados}\n"
                               f"Longitud: {longitud:.2f} cm\n"
                               f"Altura: {altura:.2f} cm\n"
                               f"Área total: {area_total:.2f} cm²\n"
                               f"Volumen: {volumen:.2f} cm³")
            for widget in resultados_frame.winfo_children():
                widget.destroy()
            ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
            ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
            botones_frame = ttk.Frame(resultados_frame)
            botones_frame.pack(pady=10)
            ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_prisma).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
            fig = self.dibujar_prisma(figura_frame, n_lados, longitud, altura)
            ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_prisma(self, frame, n_lados, longitud, altura):
        fig = plt.figure(figsize=(4, 4))
        ax = fig.add_subplot(111, projection='3d')
        angulo = 2 * math.pi / n_lados
        x = [longitud * math.cos(i * angulo) for i in range(n_lados)]
        y = [longitud * math.sin(i * angulo) for i in range(n_lados)]
        z_base = [0] * n_lados
        z_top = [altura] * n_lados
        ax.plot(x + [x[0]], y + [y[0]], z_base + [z_base[0]], color="b")
        ax.plot(x + [x[0]], y + [y[0]], z_top + [z_top[0]], color="b")
        for i in range(n_lados):
            ax.plot([x[i], x[i]], [y[i], y[i]], [0, altura], color="b")
        ax.set_title("Prisma")
        ax.set_xlabel("X (cm)")
        ax.set_ylabel("Y (cm)")
        ax.set_zlabel("Z (cm)")
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return fig


    def calcular_cilindro(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        resultados_frame, figura_frame = self.dividir_frame()
        ttk.Label(resultados_frame, text="Radio de la base:").pack(pady=5)
        self.radio_entry = ttk.Entry(resultados_frame)
        self.radio_entry.pack()
        ttk.Label(resultados_frame, text="Altura:").pack(pady=5)
        self.altura_entry = ttk.Entry(resultados_frame)
        self.altura_entry.pack()
        ttk.Button(resultados_frame, text="Calcular", command=lambda: self.mostrar_resultado_cilindro(resultados_frame, figura_frame) ).pack(pady=10)
        ttk.Button(resultados_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=5)

    def mostrar_resultado_cilindro(self, resultados_frame, figura_frame):
        try:
            radio = float(self.radio_entry.get())
            altura = float(self.altura_entry.get())
            if radio <= 0 or altura <= 0:
                messagebox.showerror("Error", "Los valores deben ser mayores que cero.")
                return
            area_base = math.pi * radio**2
            area_lateral = 2 * math.pi * radio * altura
            area_total = 2 * area_base + area_lateral
            volumen = area_base * altura
            resultado_texto = (f"Radio: {radio:.2f} cm\n"
                               f"Altura: {altura:.2f} cm\n"
                               f"Área total: {area_total:.2f} cm²\n"
                               f"Volumen: {volumen:.2f} cm³")
            for widget in resultados_frame.winfo_children():
                widget.destroy()
            ttk.Label(resultados_frame, text="Resultados:", font=("Arial", 12)).pack(pady=5)
            ttk.Label(resultados_frame, text=resultado_texto).pack(pady=5)
            botones_frame = ttk.Frame(resultados_frame)
            botones_frame.pack(pady=10)
            ttk.Button(botones_frame, text="Volver a Calcular", command=self.calcular_cilindro).pack(side=tk.LEFT, padx=5)
            ttk.Button(botones_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
            fig = self.dibujar_cilindro(figura_frame, radio, altura)
            ttk.Button(botones_frame, text="Exportar PDF", command=lambda: exportar_a_pdf(resultado_texto, fig)).pack(side=tk.LEFT, padx=5)
        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

    def dibujar_cilindro(self, frame, radio, altura):
        fig = plt.figure(figsize=(4, 4))
        ax = fig.add_subplot(111, projection='3d')
        theta = np.linspace(0, 2 * math.pi, 100)
        x = radio * np.cos(theta)
        y = radio * np.sin(theta)
        z_base = np.zeros_like(x)
        z_top = np.full_like(x, altura)
        ax.plot(x, y, z_base, color="b")
        ax.plot(x, y, z_top, color="b")
        for i in range(len(x)):
            ax.plot([x[i], x[i]], [y[i], y[i]], [0, altura], color="b")
        ax.set_title("Cilindro")
        ax.set_xlabel("X (cm)")
        ax.set_ylabel("Y (cm)")
        ax.set_zlabel("Z (cm)")
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return fig



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()