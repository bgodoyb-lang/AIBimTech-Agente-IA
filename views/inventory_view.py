import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable

from models.archivo import Archivo


class InventoryView:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("AIBim Tech - Inventory Scanner MVC + MySQL")
        self.root.geometry("1160x690")
        self.root.minsize(920, 540)

        self.ruta_var = tk.StringVar()
        self.limite_archivos_var = tk.StringVar()
        self.limite_mb_var = tk.StringVar()
        self.estado_var = tk.StringVar(
            value="Pruebe la conexión y seleccione una carpeta."
        )
        self.resumen_var = tk.StringVar(
            value="Archivos: 0 | Tamaño: 0 MB | Errores: 0"
        )
        self.mysql_var = tk.StringVar(
            value="MySQL: conexión no comprobada"
        )

        self._crear_componentes()

    def _crear_componentes(self) -> None:
        contenedor = ttk.Frame(self.root, padding=12)
        contenedor.pack(fill="both", expand=True)

        conexion = ttk.LabelFrame(
            contenedor,
            text="Base de datos",
            padding=10,
        )
        conexion.pack(fill="x", pady=(0, 8))

        ttk.Label(
            conexion,
            textvariable=self.mysql_var,
        ).pack(side="left")

        self.boton_probar_mysql = ttk.Button(
            conexion,
            text="Probar conexión MySQL",
        )
        self.boton_probar_mysql.pack(side="right")

        seleccion = ttk.LabelFrame(
            contenedor,
            text="Origen del análisis",
            padding=10,
        )
        seleccion.pack(fill="x")

        ttk.Entry(
            seleccion,
            textvariable=self.ruta_var,
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=(0, 8),
        )

        self.boton_seleccionar = ttk.Button(
            seleccion,
            text="Seleccionar carpeta",
        )
        self.boton_seleccionar.grid(row=0, column=4)

        ttk.Label(
            seleccion,
            text="Límite de archivos (opcional):",
        ).grid(row=1, column=0, sticky="w", pady=(10, 0))

        ttk.Entry(
            seleccion,
            textvariable=self.limite_archivos_var,
            width=12,
        ).grid(
            row=1,
            column=1,
            sticky="w",
            pady=(10, 0),
            padx=(5, 20),
        )

        ttk.Label(
            seleccion,
            text="Límite en MB (opcional):",
        ).grid(row=1, column=2, sticky="w", pady=(10, 0))

        ttk.Entry(
            seleccion,
            textvariable=self.limite_mb_var,
            width=12,
        ).grid(
            row=1,
            column=3,
            sticky="w",
            pady=(10, 0),
            padx=(5, 20),
        )

        self.boton_iniciar = ttk.Button(
            seleccion,
            text="Iniciar inventario",
        )
        self.boton_iniciar.grid(
            row=1,
            column=4,
            pady=(10, 0),
            sticky="e",
        )

        seleccion.columnconfigure(0, weight=1)

        progreso_frame = ttk.Frame(contenedor)
        progreso_frame.pack(fill="x", pady=(10, 8))

        self.progreso = ttk.Progressbar(
            progreso_frame,
            mode="indeterminate",
        )
        self.progreso.pack(fill="x")

        ttk.Label(
            progreso_frame,
            textvariable=self.estado_var,
        ).pack(anchor="w", pady=(4, 0))

        ttk.Label(
            progreso_frame,
            textvariable=self.resumen_var,
        ).pack(anchor="w")

        columnas = (
            "nombre",
            "extension",
            "tipo",
            "tamano",
            "modificacion",
            "ruta",
        )

        self.tabla = ttk.Treeview(
            contenedor,
            columns=columnas,
            show="headings",
        )

        titulos = {
            "nombre": "Nombre",
            "extension": "Extensión",
            "tipo": "Tipo",
            "tamano": "Tamaño (bytes)",
            "modificacion": "Modificación",
            "ruta": "Ruta",
        }

        anchos = {
            "nombre": 190,
            "extension": 75,
            "tipo": 150,
            "tamano": 100,
            "modificacion": 135,
            "ruta": 390,
        }

        for columna in columnas:
            self.tabla.heading(
                columna,
                text=titulos[columna],
            )
            self.tabla.column(
                columna,
                width=anchos[columna],
                anchor="w",
            )

        barra_y = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=self.tabla.yview,
        )
        barra_x = ttk.Scrollbar(
            contenedor,
            orient="horizontal",
            command=self.tabla.xview,
        )

        self.tabla.configure(
            yscrollcommand=barra_y.set,
            xscrollcommand=barra_x.set,
        )

        self.tabla.pack(fill="both", expand=True, side="left")
        barra_y.pack(fill="y", side="right")
        barra_x.pack(fill="x", side="bottom")

    def configurar_eventos(
        self,
        seleccionar_carpeta: Callable[[], None],
        iniciar_inventario: Callable[[], None],
        probar_mysql: Callable[[], None],
    ) -> None:
        self.boton_seleccionar.configure(
            command=seleccionar_carpeta
        )
        self.boton_iniciar.configure(
            command=iniciar_inventario
        )
        self.boton_probar_mysql.configure(
            command=probar_mysql
        )

    def pedir_carpeta(self) -> str:
        return filedialog.askdirectory(
            title="Seleccione una carpeta"
        )

    def obtener_ruta(self) -> str:
        return self.ruta_var.get().strip()

    def establecer_ruta(self, ruta: str) -> None:
        self.ruta_var.set(ruta)

    def obtener_limite_archivos(self) -> str:
        return self.limite_archivos_var.get()

    def obtener_limite_mb(self) -> str:
        return self.limite_mb_var.get()

    def limpiar_tabla(self) -> None:
        for item in self.tabla.get_children():
            self.tabla.delete(item)

    def agregar_archivo(self, archivo: Archivo) -> None:
        self.tabla.insert(
            "",
            "end",
            values=(
                archivo.nombre,
                archivo.extension or "(sin extensión)",
                archivo.categoria_tipo,
                archivo.tamano_bytes,
                archivo.fecha_modificacion,
                archivo.ruta,
            ),
        )

    def iniciar_progreso(self) -> None:
        self.boton_iniciar.configure(state="disabled")
        self.progreso.start(10)
        self.estado_var.set("Escaneando archivos...")

    def detener_progreso(self) -> None:
        self.progreso.stop()
        self.boton_iniciar.configure(state="normal")

    def actualizar_resumen(
        self,
        cantidad: int,
        total_bytes: int,
        errores: int,
    ) -> None:
        self.resumen_var.set(
            f"Archivos: {cantidad} | "
            f"Tamaño: {total_bytes / (1024 * 1024):.2f} MB | "
            f"Errores: {errores}"
        )

    def actualizar_mysql(
        self,
        correcto: bool,
        mensaje: str,
    ) -> None:
        estado = "conectado" if correcto else "sin conexión"
        self.mysql_var.set(f"MySQL: {estado} — {mensaje}")

    def mostrar_estado(self, texto: str) -> None:
        self.estado_var.set(texto)

    def mostrar_error(self, mensaje: str) -> None:
        messagebox.showerror("Error", mensaje)

    def mostrar_advertencia(self, mensaje: str) -> None:
        messagebox.showwarning("Advertencia", mensaje)

    def mostrar_informacion(
        self,
        titulo: str,
        mensaje: str,
    ) -> None:
        messagebox.showinfo(titulo, mensaje)

    def mostrar_finalizado(
        self,
        cantidad: int,
        errores: int,
        id_inventario: int,
    ) -> None:
        messagebox.showinfo(
            "Proceso terminado",
            "El inventario fue generado y guardado en MySQL.\n\n"
            f"ID de inventario: {id_inventario}\n"
            f"Archivos: {cantidad}\n"
            f"Errores: {errores}",
        )
