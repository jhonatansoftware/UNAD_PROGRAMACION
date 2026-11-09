# =============================================================================
# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (213023) - Fase 2: Diseno y Programacion Orientada a Objetos
# Ejercicio 3: Sistema para Control de Lavado (Car Wash Control System)
#
# Descripcion:
#   Aplicacion de escritorio con interfaz grafica (Tkinter) que registra los
#   autos que ingresan a un autolavado, permite seleccionar un auto para
#   registrar su salida y calcula automaticamente el valor a pagar segun el
#   tiempo que permanecio en el proceso de lavado.
#
#   Antes de acceder al sistema se muestra un modulo de inicio de sesion
#   (login) que valida el usuario "programacion" y la contrasena "programacion".
#
# Requisitos de la guia:
#   - Lenguaje Python y biblioteca estandar Tkinter.
#   - Todas las interfaces graficas en idioma ingles.
#
# Conceptos de POO aplicados:
#   - Clase y objetos: cada auto es un objeto de la clase AutoLavado.
#   - Encapsulamiento: atributos privados (_placa, _hora_ingreso, _tarifa_hora)
#     que solo se manejan a traves de metodos.
#   - Abstraccion: la interfaz solo usa metodos sencillos (registrar_ingreso,
#     registrar_salida, calcular_pago, obtener_placa) sin conocer los detalles
#     internos del calculo.
#   - Las ventanas tambien son clases (LoginWindow y CarWashApp).
#
# Entorno de desarrollo: Visual Studio Code - Lenguaje: Python 3
# =============================================================================

import tkinter as tk                    # Biblioteca estandar para interfaces graficas
from tkinter import ttk, messagebox     # ttk: widgets modernos; messagebox: ventanas emergentes
from datetime import datetime           # Para sugerir la hora actual del sistema
import unicodedata                      # Para comparar textos con o sin tilde


# =============================================================================
# CLASE DEL MODELO: AutoLavado
# =============================================================================
class AutoLavado:
    """Representa un auto que ingresa al servicio de lavado."""

    def __init__(self, placa, tarifa_hora):
        """Constructor: se ejecuta al crear cada objeto AutoLavado.

        Parametros:
            placa (str): placa del vehiculo.
            tarifa_hora (float): valor que se cobra por cada hora de servicio.
        """
        # Atributos privados: en Python se indican con un guion bajo al inicio.
        self._placa = placa.upper()       # Se guarda en mayusculas para uniformidad
        self._tarifa_hora = tarifa_hora   # Tarifa por hora del servicio
        self._hora_ingreso = None         # Se asigna con registrar_ingreso()
        self._hora_salida = None          # Se asigna con registrar_salida()
        self._pago = None                 # Valor cobrado al registrar la salida

    # -------------------------------------------------------------------------
    # Método auxiliar (privado): convierte una hora "HH:MM" a minutos.
    # Ejemplo: "08:30" -> 8*60 + 30 = 510 minutos.
    # Trabajar en minutos permite comparar y restar horas como nuumeros enteros.
    # -------------------------------------------------------------------------
    @staticmethod
    def _a_minutos(hora):
        try:
            h, m = hora.split(":")        # Separa horas y minutos
            h, m = int(h), int(m)
        except ValueError:
            # Ocurre si no hay ":" o si las partes no son numeros
            raise ValueError("Invalid format. Use HH:MM (e.g. 08:30).")

        # Validacion del rango permitido
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Time out of range (00:00 to 23:59).")

        return h * 60 + m

    # -------------------------------------------------------------------------
    # Métodos solicitados en el enunciado
    # -------------------------------------------------------------------------
    def registrar_ingreso(self, hora):
        """Registra la hora en que el auto ingresa al lavado."""
        self._a_minutos(hora)             # Valida el formato antes de guardar
        self._hora_ingreso = hora

    def registrar_salida(self, hora):
        """Registra la salida del auto y retorna el valor a pagar."""
        if self._hora_ingreso is None:
            raise ValueError("This car has no entry time.")
        if self._hora_salida is not None:
            raise ValueError("This car has already checked out.")

        # calcular_pago() tambien valida que la salida sea posterior al ingreso
        self._pago = self.calcular_pago(hora)
        self._hora_salida = hora
        return self._pago

    def calcular_pago(self, hora_salida):
        """Calcula el costo segun el tiempo de permanencia.

        Fórmula: pago = (minutos de permanencia / 60) * tarifa por hora
        """
        ingreso = self._a_minutos(self._hora_ingreso)
        salida = self._a_minutos(hora_salida)

        # Validacion de la hora de salida: debe ser mayor que la de ingreso
        if salida <= ingreso:
            raise ValueError("Exit time must be later than entry time.")

        minutos = salida - ingreso
        return round(minutos / 60 * self._tarifa_hora, 2)

    def obtener_placa(self):
        """Metodo de acceso (getter) para consultar la placa privada."""
        return self._placa

    # Metodos de acceso adicionales que usa la interfaz para mostrar los datos
    def obtener_hora_ingreso(self):
        return self._hora_ingreso

    def obtener_hora_salida(self):
        return self._hora_salida

    def obtener_pago(self):
        return self._pago

    def esta_en_lavado(self):
        """Retorna True si el auto aun no ha registrado su salida."""
        return self._hora_salida is None


# =============================================================================
# MODULO DE INICIO DE SESIoN (LOGIN)
# =============================================================================
USUARIO_VALIDO = "programacion"
CLAVE_VALIDA = "programacion"


def normalizar(texto):
    """Quita tildes y pasa a minusculas para que 'programacion' y
    'programacion' se consideren iguales (por facilidad al escribir)."""
    texto = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


class LoginWindow:
    """Ventana de inicio de sesion. Solo si los datos son correctos
    se abre el sistema principal del autolavado."""

    MAX_INTENTOS = 3   # Numero maximo de intentos permitidos

    def __init__(self, root):
        self.root = root
        self.intentos = 0
        self.root.title("Car Wash - Login")
        self.root.geometry("320x210")
        self.root.resizable(False, False)

        marco = ttk.Frame(root, padding=20)
        marco.pack(fill="both", expand=True)

        ttk.Label(marco, text="Sign in", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 12))

        ttk.Label(marco, text="Username:").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_usuario = ttk.Entry(marco, width=22)
        self.entry_usuario.grid(row=1, column=1, pady=4)

        ttk.Label(marco, text="Password:").grid(row=2, column=0, sticky="w", pady=4)
        # show="*" oculta los caracteres de la contraseña
        self.entry_clave = ttk.Entry(marco, width=22, show="*")
        self.entry_clave.grid(row=2, column=1, pady=4)

        ttk.Button(marco, text="Log in", command=self.validar).grid(
            row=3, column=0, columnspan=2, pady=12)

        # Permite iniciar sesion presionando Enter
        self.root.bind("<Return>", lambda e: self.validar())
        self.entry_usuario.focus()

    def validar(self):
        """Compara el usuario y la contrasena con los valores validos."""
        usuario = normalizar(self.entry_usuario.get())
        clave = normalizar(self.entry_clave.get())

        if usuario == normalizar(USUARIO_VALIDO) and clave == normalizar(CLAVE_VALIDA):
            # Acceso correcto: se limpia la ventana y se carga el sistema
            self.root.unbind("<Return>")
            for widget in self.root.winfo_children():
                widget.destroy()
            CarWashApp(self.root)
        else:
            self.intentos += 1
            restantes = self.MAX_INTENTOS - self.intentos
            if restantes <= 0:
                messagebox.showerror("Access denied", "Too many failed attempts. The program will close.")
                self.root.destroy()
            else:
                messagebox.showerror("Access denied",
                                     f"Invalid username or password.\nAttempts left: {restantes}")
                self.entry_clave.delete(0, tk.END)


# =============================================================================
# VENTANA PRINCIPAL DEL SISTEMA
# =============================================================================
TARIFA = 12000   # Tarifa por hora en pesos colombianos (puede modificarse)


class CarWashApp:
    """Interfaz principal: registrar ingresos, seleccionar autos,
    registrar salidas y mostrar el valor a pagar."""

    def __init__(self, root):
        self.root = root
        self.autos = []   # Lista interna donde se almacenan los objetos AutoLavado

        self.root.title("Car Wash Control System")
        self.root.geometry("640x590")
        self.root.resizable(False, False)

        principal = ttk.Frame(root, padding=15)
        principal.pack(fill="both", expand=True)

        ttk.Label(principal, text="Car Wash Control System",
                  font=("Segoe UI", 15, "bold")).pack(pady=(0, 10))
        ttk.Label(principal, text=f"Rate per hour: ${TARIFA:,.0f} COP").pack()

        # Reloj con fecha y hora actuales: sirve como evidencia de ejecucion
        # en la captura de pantalla que exige la guia (dia y hora en la imagen)
        self.label_reloj = ttk.Label(principal, font=("Segoe UI", 10, "italic"))
        self.label_reloj.pack()
        self.actualizar_reloj()

        # ----------------- Seccion: registrar ingreso -----------------
        marco_ingreso = ttk.LabelFrame(principal, text="Car entry", padding=10)
        marco_ingreso.pack(fill="x", pady=8)

        ttk.Label(marco_ingreso, text="License plate:").grid(row=0, column=0, sticky="w")
        self.entry_placa = ttk.Entry(marco_ingreso, width=15)
        self.entry_placa.grid(row=0, column=1, padx=5)

        ttk.Label(marco_ingreso, text="Entry time (HH:MM):").grid(row=0, column=2, sticky="w")
        self.entry_hora_ingreso = ttk.Entry(marco_ingreso, width=8)
        self.entry_hora_ingreso.grid(row=0, column=3, padx=5)
        # Se sugiere la hora actual del sistema para agilizar el registro
        self.entry_hora_ingreso.insert(0, datetime.now().strftime("%H:%M"))

        ttk.Button(marco_ingreso, text="Register entry",
                   command=self.registrar_ingreso).grid(row=0, column=4, padx=5)

        # ----------------- Tabla de autos registrados -----------------
        marco_tabla = ttk.LabelFrame(principal, text="Registered cars (select one to check out)", padding=10)
        marco_tabla.pack(fill="both", expand=True, pady=8)

        columnas = ("plate", "entry", "exit", "amount", "status")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=8)
        encabezados = {"plate": "Plate", "entry": "Entry time", "exit": "Exit time",
                       "amount": "Amount (COP)", "status": "Status"}
        for col in columnas:
            self.tabla.heading(col, text=encabezados[col])
            self.tabla.column(col, width=110, anchor="center")
        self.tabla.pack(fill="both", expand=True)

        # ----------------- Seccion: registrar salida -----------------
        marco_salida = ttk.LabelFrame(principal, text="Car exit", padding=10)
        marco_salida.pack(fill="x", pady=8)

        ttk.Label(marco_salida, text="Exit time (HH:MM):").grid(row=0, column=0, sticky="w")
        self.entry_hora_salida = ttk.Entry(marco_salida, width=8)
        self.entry_hora_salida.grid(row=0, column=1, padx=5)
        self.entry_hora_salida.insert(0, datetime.now().strftime("%H:%M"))

        ttk.Button(marco_salida, text="Register exit and charge",
                   command=self.registrar_salida).grid(row=0, column=2, padx=5)

        # Etiqueta donde se muestra el resultado del último cobro
        self.label_total = ttk.Label(principal, text="Total to pay: -",
                                     font=("Segoe UI", 12, "bold"))
        self.label_total.pack(pady=5)

    # -------------------------------------------------------------------------
    # Acciones de los botones
    # -------------------------------------------------------------------------
    def registrar_ingreso(self):
        """Crea un objeto AutoLavado y lo agrega a la lista interna."""
        placa = self.entry_placa.get().strip()
        hora = self.entry_hora_ingreso.get().strip()

        if not placa:
            messagebox.showwarning("Missing data", "Please enter the license plate.")
            return

        # Evita registrar dos veces un auto que todavia esta en lavado
        for a in self.autos:
            if a.obtener_placa() == placa.upper() and a.esta_en_lavado():
                messagebox.showwarning("Duplicate", "This car is already in the wash.")
                return

        auto = AutoLavado(placa, TARIFA)    # Se crea el objeto (instancia)
        try:
            auto.registrar_ingreso(hora)
        except ValueError as e:
            messagebox.showerror("Invalid time", str(e))
            return

        self.autos.append(auto)             # Se guarda en la lista interna
        self.entry_placa.delete(0, tk.END)
        self.actualizar_tabla()
        messagebox.showinfo("Entry registered", f"Car {auto.obtener_placa()} registered at {hora}.")

    def registrar_salida(self):
        """Toma el auto seleccionado en la tabla, registra su salida y cobra."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("No selection", "Please select a car from the list.")
            return

        # El identificador de cada fila es la posicion del auto en la lista
        indice = int(seleccion[0])
        auto = self.autos[indice]
        hora = self.entry_hora_salida.get().strip()

        try:
            pago = auto.registrar_salida(hora)   # Calcula el costo automaticamente
        except ValueError as e:
            messagebox.showerror("Invalid exit", str(e))
            return

        self.actualizar_tabla()
        self.label_total.config(text=f"Total to pay ({auto.obtener_placa()}): ${pago:,.0f} COP")
        messagebox.showinfo("Payment", f"Car {auto.obtener_placa()}\nTotal to pay: ${pago:,.0f} COP")

    def actualizar_reloj(self):
        """Muestra la fecha y hora del sistema y se actualiza cada segundo."""
        ahora = datetime.now().strftime("Date: %A, %B %d, %Y   |   Time: %H:%M:%S")
        self.label_reloj.config(text=ahora)
        # after() vuelve a llamar este método dentro de 1000 ms (1 segundo)
        self.root.after(1000, self.actualizar_reloj)

    def actualizar_tabla(self):
        """Vuelve a dibujar la tabla con los datos de la lista de autos."""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for i, a in enumerate(self.autos):
            salida = a.obtener_hora_salida() or "-"
            monto = f"${a.obtener_pago():,.0f}" if a.obtener_pago() is not None else "-"
            estado = "In wash" if a.esta_en_lavado() else "Finished"
            # iid=str(i) guarda la posición del auto para recuperarlo al seleccionar
            self.tabla.insert("", tk.END, iid=str(i),
                              values=(a.obtener_placa(), a.obtener_hora_ingreso(), salida, monto, estado))


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================
if __name__ == "__main__":
    ventana = tk.Tk()          # Ventana raiz de Tkinter
    LoginWindow(ventana)       # Primero se muestra el login
    ventana.mainloop()         # Mantiene la aplicacion abierta esperando eventos
