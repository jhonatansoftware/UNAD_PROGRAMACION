# =============================================================================
# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (213023)
# Fase 3: Modelos de herencia, polimorfismo y gestion de metodos
# Ejercicio 3: Sistema de Nomina Empresarial (Payroll System)
#
# Descripcion:
#   Motor de nomina que centraliza el calculo de salarios de varios tipos de
#   empleados. Gracias a la herencia y al polimorfismo, se pueden agregar
#   nuevos tipos de empleado sin modificar el codigo base del sistema.
#
# Conceptos aplicados:
#   - Herencia: Empleado es la clase base; EmpleadoTiempoCompleto,
#     EmpleadoPorHoras y EmpleadoComision son clases hijas.
#   - Metodo virtual (abstracto): calcular_salario() se declara en la clase
#     base y cada clase hija lo implementa con su propia regla de pago.
#   - Herencia multiple (mixin): EmpleadoTiempoCompletoBonificado hereda de
#     EmpleadoTiempoCompleto y de Bonificable al mismo tiempo.
#   - Sobrecarga: Python no permite varios metodos con el mismo nombre, por
#     eso mostrar_informacion() se "sobrecarga" con parametros opcionales.
#   - Polimorfismo: SistemaNomina llama calcular_salario() en cada empleado
#     sin importar su tipo, y cada objeto responde con su propia logica.
#
# Interfaz grafica: Tkinter (en ingles), con modulo de inicio de sesion.
# Entorno de desarrollo: Visual Studio Code - Lenguaje: Python 3
# =============================================================================

import tkinter as tk                    # Biblioteca estandar para interfaces graficas
from tkinter import ttk, messagebox     # Widgets modernos y ventanas emergentes
from abc import ABC, abstractmethod     # Para declarar clases y metodos abstractos
from datetime import datetime           # Fecha y hora para la evidencia de ejecucion
import unicodedata                      # Para comparar textos con o sin tilde


def formato_pesos(valor):
    """Da formato de moneda a un numero. Ejemplo: 3500000 -> $3,500,000 COP"""
    return f"${valor:,.0f} COP"


# =============================================================================
# CLASE BASE: Empleado
# =============================================================================
class Empleado(ABC):
    """Clase base abstracta con los atributos generales de todo empleado.

    Hereda de ABC (Abstract Base Class), por lo que no se pueden crear objetos
    directamente de Empleado: solo de sus clases hijas.
    """

    def __init__(self, nombre, identificacion, salario_base):
        # Validaciones de los datos generales
        if not nombre.strip():
            raise ValueError("Name is required.")
        if not identificacion.strip():
            raise ValueError("ID is required.")
        if salario_base < 0:
            raise ValueError("Base salary cannot be negative.")

        # Atributos protegidos (encapsulamiento): se consultan con propiedades
        self._nombre = nombre.strip()
        self._identificacion = identificacion.strip()
        self._salario_base = salario_base

    # Propiedades de solo lectura (getters)
    @property
    def nombre(self):
        return self._nombre

    @property
    def identificacion(self):
        return self._identificacion

    @property
    def salario_base(self):
        return self._salario_base

    @abstractmethod
    def calcular_salario(self):
        """Metodo virtual: cada clase hija DEBE implementar su propia regla."""
        pass

    def tipo(self):
        """Nombre del tipo de empleado. Las clases hijas lo sobrescriben."""
        return "Employee"

    def detalles(self):
        """Datos especificos del tipo de empleado (se sobrescribe en las hijas).
        Retorna un diccionario {etiqueta: valor}."""
        return {}

    def mostrar_informacion(self, mostrar_salario=False, mostrar_detalles=False):
        """Metodo 'sobrecargado' mediante parametros opcionales:

        - mostrar_informacion()                       -> solo datos basicos
        - mostrar_informacion(mostrar_salario=True)   -> datos basicos + salario total
        - mostrar_informacion(mostrar_detalles=True)  -> salario + bonificaciones + detalles
        """
        lineas = [
            f"Name: {self.nombre}",
            f"ID: {self.identificacion}",
            f"Employee type: {self.tipo()}",
        ]

        # Nivel 3: detalles especificos (incluye bonificaciones si las hay)
        if mostrar_detalles:
            lineas.append("--- Details ---")
            for etiqueta, valor in self.detalles().items():
                lineas.append(f"{etiqueta}: {valor}")

        # Nivel 2 y 3: salario total del mes
        if mostrar_salario or mostrar_detalles:
            lineas.append(f"Total monthly salary: {formato_pesos(self.calcular_salario())}")

        return "\n".join(lineas)


# =============================================================================
# CLASES HIJAS (herencia simple)
# =============================================================================
class EmpleadoTiempoCompleto(Empleado):
    """Recibe un salario fijo mas una bonificacion por desempeno."""

    def __init__(self, nombre, identificacion, salario_base, bonificacion_desempeno=0):
        # super() llama al constructor de la clase padre (Empleado)
        super().__init__(nombre, identificacion, salario_base)
        if bonificacion_desempeno < 0:
            raise ValueError("Performance bonus cannot be negative.")
        self._bonificacion_desempeno = bonificacion_desempeno

    def calcular_salario(self):
        # Regla de pago: salario fijo + bonificacion por desempeno
        return self.salario_base + self._bonificacion_desempeno

    def tipo(self):
        return "Full-time"

    def detalles(self):
        return {
            "Fixed salary": formato_pesos(self.salario_base),
            "Performance bonus": formato_pesos(self._bonificacion_desempeno),
        }


class EmpleadoPorHoras(Empleado):
    """Su salario se calcula segun el numero de horas trabajadas.
    Aqui el salario_base representa el valor de cada hora."""

    HORAS_MAXIMAS = 744   # 31 dias x 24 horas: limite logico de un mes

    def __init__(self, nombre, identificacion, valor_hora, horas_trabajadas):
        super().__init__(nombre, identificacion, valor_hora)
        if not (0 <= horas_trabajadas <= self.HORAS_MAXIMAS):
            raise ValueError(f"Hours worked must be between 0 and {self.HORAS_MAXIMAS}.")
        self._horas_trabajadas = horas_trabajadas

    def calcular_salario(self):
        # Regla de pago: valor por hora x horas trabajadas
        return self.salario_base * self._horas_trabajadas

    def tipo(self):
        return "Hourly"

    def detalles(self):
        return {
            "Hourly rate": formato_pesos(self.salario_base),
            "Hours worked": f"{self._horas_trabajadas:g}",
        }


class EmpleadoComision(Empleado):
    """Recibe un salario base mas un porcentaje de sus ventas."""

    def __init__(self, nombre, identificacion, salario_base, ventas, porcentaje):
        super().__init__(nombre, identificacion, salario_base)
        if ventas < 0:
            raise ValueError("Sales cannot be negative.")
        if not (0 <= porcentaje <= 100):
            raise ValueError("Commission must be between 0 and 100 %.")
        self._ventas = ventas
        self._porcentaje = porcentaje

    def comision(self):
        """Valor de la comision: ventas x porcentaje / 100"""
        return self._ventas * self._porcentaje / 100

    def calcular_salario(self):
        # Regla de pago: salario base + comision por ventas
        return self.salario_base + self.comision()

    def tipo(self):
        return "Commission"

    def detalles(self):
        return {
            "Base salary": formato_pesos(self.salario_base),
            "Monthly sales": formato_pesos(self._ventas),
            "Commission rate": f"{self._porcentaje:g} %",
            "Commission earned": formato_pesos(self.comision()),
        }


# =============================================================================
# MIXIN: Bonificable (clase extra para la herencia multiple)
# =============================================================================
class Bonificable:
    """Agrega a cualquier clase la capacidad de recibir bonificaciones extra.
    Un 'mixin' es una clase pequena que aporta un comportamiento adicional."""

    def __init__(self):
        self._bonificaciones = []   # Lista de montos de bonificacion

    def agregar_bonificacion(self, monto):
        if monto <= 0:
            raise ValueError("Bonus amount must be greater than zero.")
        self._bonificaciones.append(monto)

    def obtener_bonificaciones(self):
        # Se retorna una copia para proteger la lista original (encapsulamiento)
        return list(self._bonificaciones)

    def total_bonificaciones(self):
        return sum(self._bonificaciones)


# =============================================================================
# HERENCIA MULTIPLE: EmpleadoTiempoCompletoBonificado
# =============================================================================
class EmpleadoTiempoCompletoBonificado(EmpleadoTiempoCompleto, Bonificable):
    """Hereda de DOS clases: de EmpleadoTiempoCompleto (salario fijo +
    desempeno) y de Bonificable (bonificaciones extra).

    Orden de resolucion de metodos (MRO):
    EmpleadoTiempoCompletoBonificado -> EmpleadoTiempoCompleto -> Empleado
    -> ABC -> Bonificable -> object
    """

    def __init__(self, nombre, identificacion, salario_base, bonificacion_desempeno=0):
        # Se inicializa explicitamente cada clase padre
        EmpleadoTiempoCompleto.__init__(self, nombre, identificacion,
                                        salario_base, bonificacion_desempeno)
        Bonificable.__init__(self)

    def calcular_salario(self):
        # Reutiliza el calculo del padre y le suma las bonificaciones extra
        return super().calcular_salario() + self.total_bonificaciones()

    def tipo(self):
        return "Full-time + Bonuses"

    def detalles(self):
        # Se extienden los detalles del padre con la informacion del mixin
        datos = super().detalles()
        bonos = self.obtener_bonificaciones()
        datos["Extra bonuses"] = ", ".join(formato_pesos(b) for b in bonos) if bonos else "None"
        datos["Total extra bonuses"] = formato_pesos(self.total_bonificaciones())
        return datos


# =============================================================================
# SISTEMA DE NOMINA (polimorfismo)
# =============================================================================
class SistemaNomina:
    """Gestiona la lista de empleados y calcula la nomina mensual."""

    def __init__(self):
        self._empleados = []

    def agregar_empleado(self, empleado):
        # Solo se aceptan objetos que sean Empleado (o de sus clases hijas)
        if not isinstance(empleado, Empleado):
            raise TypeError("Only Employee objects can be added.")
        if self.buscar(empleado.identificacion):
            raise ValueError("An employee with this ID already exists.")
        self._empleados.append(empleado)

    def buscar(self, identificacion):
        for e in self._empleados:
            if e.identificacion == identificacion:
                return e
        return None

    def obtener_empleados(self):
        return list(self._empleados)

    def calcular_nomina_mensual(self):
        # POLIMORFISMO: la misma llamada calcular_salario() ejecuta una regla
        # diferente segun el tipo real de cada objeto de la lista.
        return sum(e.calcular_salario() for e in self._empleados)

    def generar_reporte(self):
        lineas = ["MONTHLY PAYROLL REPORT", "=" * 50]
        for e in self._empleados:
            lineas.append(f"{e.nombre:<20} {e.tipo():<20} {formato_pesos(e.calcular_salario())}")
        lineas.append("=" * 50)
        lineas.append(f"Employees: {len(self._empleados)}")
        lineas.append(f"TOTAL MONTHLY PAYROLL: {formato_pesos(self.calcular_nomina_mensual())}")
        return "\n".join(lineas)


# =============================================================================
# MODULO DE INICIO DE SESION (LOGIN)
# =============================================================================
USUARIO_VALIDO = "programacion"
CLAVE_VALIDA = "programacion"


def normalizar(texto):
    """Quita tildes y pasa a minusculas ('programacion' == 'programacion')."""
    texto = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


class LoginWindow:
    """Ventana de inicio de sesion. Si los datos son correctos, abre el sistema."""

    MAX_INTENTOS = 3

    def __init__(self, root):
        self.root = root
        self.intentos = 0
        self.root.title("Payroll System - Login")
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
        self.entry_clave = ttk.Entry(marco, width=22, show="*")   # Oculta la clave
        self.entry_clave.grid(row=2, column=1, pady=4)
        ttk.Button(marco, text="Log in", command=self.validar).grid(
            row=3, column=0, columnspan=2, pady=12)

        self.root.bind("<Return>", lambda e: self.validar())   # Enter = Log in
        self.entry_usuario.focus()

    def validar(self):
        usuario = normalizar(self.entry_usuario.get())
        clave = normalizar(self.entry_clave.get())
        if usuario == normalizar(USUARIO_VALIDO) and clave == normalizar(CLAVE_VALIDA):
            self.root.unbind("<Return>")
            for widget in self.root.winfo_children():
                widget.destroy()
            PayrollApp(self.root)            # Acceso correcto: se abre el sistema
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
# VENTANA PRINCIPAL DEL SISTEMA DE NOMINA
# =============================================================================
# Etiquetas de los campos segun el tipo de empleado:
# (campo salario base, campo extra 1, campo extra 2 o None si no se usa)
TIPOS = {
    "Full-time": ("Monthly fixed salary:", "Performance bonus:", None),
    "Hourly": ("Hourly rate:", "Hours worked:", None),
    "Commission": ("Base salary:", "Monthly sales:", "Commission (%):"),
    "Full-time + Bonuses": ("Monthly fixed salary:", "Performance bonus:",
                            "Extra bonuses (comma separated):"),
}


class PayrollApp:
    """Interfaz grafica para registrar empleados y calcular la nomina."""

    def __init__(self, root):
        self.root = root
        self.sistema = SistemaNomina()   # Objeto que gestiona la lista de empleados

        self.root.title("Payroll System")
        self.root.geometry("780x760")
        self.root.resizable(False, False)

        principal = ttk.Frame(root, padding=12)
        principal.pack(fill="both", expand=True)

        ttk.Label(principal, text="Corporate Payroll System",
                  font=("Segoe UI", 15, "bold")).pack()
        # Reloj: evidencia de fecha y hora para la captura de pantalla
        self.label_reloj = ttk.Label(principal, font=("Segoe UI", 10, "italic"))
        self.label_reloj.pack(pady=(0, 6))
        self.actualizar_reloj()

        # ----------------- Formulario: nuevo empleado -----------------
        form = ttk.LabelFrame(principal, text="New employee", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Employee type:").grid(row=0, column=0, sticky="w", pady=3)
        self.combo_tipo = ttk.Combobox(form, values=list(TIPOS), state="readonly", width=24)
        self.combo_tipo.current(0)
        self.combo_tipo.grid(row=0, column=1, sticky="w", pady=3)
        # Al cambiar el tipo, se actualizan las etiquetas del formulario
        self.combo_tipo.bind("<<ComboboxSelected>>", lambda e: self.cambiar_tipo())

        ttk.Label(form, text="Name:").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_nombre = ttk.Entry(form, width=27)
        self.entry_nombre.grid(row=1, column=1, sticky="w", pady=3)

        ttk.Label(form, text="ID number:").grid(row=1, column=2, sticky="w", padx=(15, 0))
        self.entry_id = ttk.Entry(form, width=20)
        self.entry_id.grid(row=1, column=3, sticky="w")

        self.label_base = ttk.Label(form)
        self.label_base.grid(row=2, column=0, sticky="w", pady=3)
        self.entry_base = ttk.Entry(form, width=27)
        self.entry_base.grid(row=2, column=1, sticky="w", pady=3)

        self.label_extra1 = ttk.Label(form)
        self.label_extra1.grid(row=2, column=2, sticky="w", padx=(15, 0))
        self.entry_extra1 = ttk.Entry(form, width=20)
        self.entry_extra1.grid(row=2, column=3, sticky="w")

        self.label_extra2 = ttk.Label(form)
        self.label_extra2.grid(row=3, column=0, sticky="w", pady=3)
        self.entry_extra2 = ttk.Entry(form, width=27)
        self.entry_extra2.grid(row=3, column=1, sticky="w", pady=3)

        ttk.Button(form, text="Add employee", command=self.agregar_empleado).grid(
            row=3, column=3, sticky="e", pady=3)
        self.cambiar_tipo()

        # ----------------- Tabla de empleados -----------------
        marco_tabla = ttk.LabelFrame(principal, text="Employees", padding=8)
        marco_tabla.pack(fill="x", pady=8)
        columnas = ("name", "id", "type", "salary")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", height=6)
        for col, texto, ancho in [("name", "Name", 200), ("id", "ID", 120),
                                  ("type", "Type", 180), ("salary", "Monthly salary", 200)]:
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor="center")
        self.tabla.pack(fill="x")

        # ----------------- Acciones -----------------
        acciones = ttk.LabelFrame(principal, text="Actions", padding=8)
        acciones.pack(fill="x")

        # Opciones de la "sobrecarga" de mostrar_informacion()
        self.opcion = tk.StringVar(value="basic")
        ttk.Label(acciones, text="Show:").grid(row=0, column=0, sticky="w")
        for i, (valor, texto) in enumerate([("basic", "Basic data"),
                                            ("salary", "Basic + total salary"),
                                            ("full", "Salary + bonuses + details")]):
            ttk.Radiobutton(acciones, text=texto, value=valor,
                            variable=self.opcion).grid(row=0, column=i + 1, sticky="w", padx=4)
        ttk.Button(acciones, text="Show information",
                   command=self.mostrar_informacion).grid(row=0, column=4, padx=6)

        ttk.Label(acciones, text="Extra bonus:").grid(row=1, column=0, sticky="w", pady=6)
        self.entry_bono = ttk.Entry(acciones, width=15)
        self.entry_bono.grid(row=1, column=1, sticky="w")
        ttk.Button(acciones, text="Add bonus to selected",
                   command=self.agregar_bono).grid(row=1, column=2, sticky="w")
        ttk.Button(acciones, text="Calculate monthly payroll",
                   command=self.calcular_nomina).grid(row=1, column=3, columnspan=2, sticky="e")

        # ----------------- Area de resultados -----------------
        self.texto = tk.Text(principal, height=12, font=("Consolas", 10), state="disabled")
        self.texto.pack(fill="both", expand=True, pady=(8, 0))

        self.cargar_ejemplos()

    # -------------------------------------------------------------------------
    # Metodos de apoyo
    # -------------------------------------------------------------------------
    def actualizar_reloj(self):
        """Muestra la fecha y hora del sistema; se actualiza cada segundo."""
        self.label_reloj.config(
            text=datetime.now().strftime("Date: %A, %B %d, %Y   |   Time: %H:%M:%S"))
        self.root.after(1000, self.actualizar_reloj)

    def cambiar_tipo(self):
        """Cambia las etiquetas del formulario segun el tipo elegido."""
        base, extra1, extra2 = TIPOS[self.combo_tipo.get()]
        self.label_base.config(text=base)
        self.label_extra1.config(text=extra1)
        if extra2:
            self.label_extra2.config(text=extra2)
            self.label_extra2.grid()
            self.entry_extra2.grid()
        else:
            # grid_remove() oculta el campo sin perder su posicion
            self.label_extra2.grid_remove()
            self.entry_extra2.grid_remove()

    @staticmethod
    def leer_numero(texto, campo):
        """Convierte un texto en numero; muestra un error claro si no es valido."""
        try:
            return float(texto.strip())
        except ValueError:
            raise ValueError(f"'{campo}' must be a valid number.")

    def escribir(self, contenido):
        """Muestra un texto en el area de resultados (solo lectura)."""
        self.texto.config(state="normal")
        self.texto.delete("1.0", tk.END)
        self.texto.insert(tk.END, contenido)
        self.texto.config(state="disabled")

    def actualizar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for e in self.sistema.obtener_empleados():
            # iid = identificacion, para recuperar el empleado al seleccionarlo
            self.tabla.insert("", tk.END, iid=e.identificacion,
                              values=(e.nombre, e.identificacion, e.tipo(),
                                      formato_pesos(e.calcular_salario())))

    def empleado_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("No selection", "Please select an employee from the list.")
            return None
        return self.sistema.buscar(seleccion[0])

    # -------------------------------------------------------------------------
    # Acciones de los botones
    # -------------------------------------------------------------------------
    def agregar_empleado(self):
        """Crea el objeto del tipo elegido y lo agrega al sistema."""
        tipo = self.combo_tipo.get()
        base_txt, extra1_txt, extra2_txt = TIPOS[tipo]
        try:
            nombre = self.entry_nombre.get()
            ident = self.entry_id.get()
            base = self.leer_numero(self.entry_base.get(), base_txt.rstrip(":"))
            extra1 = self.leer_numero(self.entry_extra1.get() or "0", extra1_txt.rstrip(":"))

            # Segun el tipo elegido se crea un objeto de una clase hija diferente
            if tipo == "Full-time":
                empleado = EmpleadoTiempoCompleto(nombre, ident, base, extra1)
            elif tipo == "Hourly":
                empleado = EmpleadoPorHoras(nombre, ident, base, extra1)
            elif tipo == "Commission":
                porcentaje = self.leer_numero(self.entry_extra2.get(), "Commission (%)")
                empleado = EmpleadoComision(nombre, ident, base, extra1, porcentaje)
            else:
                empleado = EmpleadoTiempoCompletoBonificado(nombre, ident, base, extra1)
                # Las bonificaciones extra se separan por comas: 200000, 150000
                for parte in self.entry_extra2.get().split(","):
                    if parte.strip():
                        empleado.agregar_bonificacion(self.leer_numero(parte, "Extra bonuses"))

            self.sistema.agregar_empleado(empleado)
        except (ValueError, TypeError) as error:
            messagebox.showerror("Invalid data", str(error))
            return

        self.actualizar_tabla()
        for campo in (self.entry_nombre, self.entry_id, self.entry_base,
                      self.entry_extra1, self.entry_extra2):
            campo.delete(0, tk.END)
        self.escribir(empleado.mostrar_informacion(mostrar_salario=True))

    def mostrar_informacion(self):
        """Usa la 'sobrecarga' de mostrar_informacion() segun la opcion elegida."""
        empleado = self.empleado_seleccionado()
        if not empleado:
            return
        opcion = self.opcion.get()
        if opcion == "basic":
            texto = empleado.mostrar_informacion()
        elif opcion == "salary":
            texto = empleado.mostrar_informacion(mostrar_salario=True)
        else:
            texto = empleado.mostrar_informacion(mostrar_detalles=True)
        self.escribir(texto)

    def agregar_bono(self):
        """Agrega una bonificacion extra; solo funciona con empleados Bonificable."""
        empleado = self.empleado_seleccionado()
        if not empleado:
            return
        # isinstance() verifica si el objeto heredo del mixin Bonificable
        if not isinstance(empleado, Bonificable):
            messagebox.showwarning("Not allowed",
                                   "Only 'Full-time + Bonuses' employees can receive extra bonuses.")
            return
        try:
            empleado.agregar_bonificacion(self.leer_numero(self.entry_bono.get(), "Extra bonus"))
        except ValueError as error:
            messagebox.showerror("Invalid data", str(error))
            return
        self.entry_bono.delete(0, tk.END)
        self.actualizar_tabla()
        self.escribir(empleado.mostrar_informacion(mostrar_detalles=True))

    def calcular_nomina(self):
        """Calcula la nomina mensual de todos los empleados (polimorfismo)."""
        self.escribir(self.sistema.generar_reporte())

    def cargar_ejemplos(self):
        """Carga empleados de ejemplo para probar el sistema rapidamente."""
        bonificado = EmpleadoTiempoCompletoBonificado("Pedro Gomez", "1004", 4000000, 300000)
        bonificado.agregar_bonificacion(200000)
        bonificado.agregar_bonificacion(150000)
        for e in (EmpleadoTiempoCompleto("Ana Torres", "1001", 3500000, 400000),
                  EmpleadoPorHoras("Carlos Ruiz", "1002", 25000, 160),
                  EmpleadoComision("Maria Lopez", "1003", 2000000, 15000000, 5),
                  bonificado):
            self.sistema.agregar_empleado(e)
        self.actualizar_tabla()


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================
if __name__ == "__main__":
    ventana = tk.Tk()
    LoginWindow(ventana)     # Primero se muestra el inicio de sesion
    ventana.mainloop()
