from __future__ import annotations

import queue
import threading
from typing import Optional

from repositories.mysql_repository import MySQLInventoryRepository
from services.inventory_scanner import InventoryScanner
from views.inventory_view import InventoryView


class InventoryController:
    def __init__(
        self,
        view: InventoryView,
        repository: MySQLInventoryRepository,
    ) -> None:
        self.view = view
        self.repository = repository
        self.cola: queue.Queue = queue.Queue()
        self.errores_actuales: list[str] = []

        self.view.configurar_eventos(
            self.seleccionar_carpeta,
            self.iniciar_inventario,
            self.probar_conexion_mysql,
        )

        self.view.root.after(100, self.procesar_cola)

    def seleccionar_carpeta(self) -> None:
        ruta = self.view.pedir_carpeta()

        if ruta:
            self.view.establecer_ruta(ruta)

    def probar_conexion_mysql(self) -> None:
        self.view.actualizar_mysql(
            False,
            "comprobando...",
        )

        threading.Thread(
            target=self._ejecutar_prueba_mysql,
            daemon=True,
        ).start()

    def _ejecutar_prueba_mysql(self) -> None:
        correcto, mensaje = self.repository.probar_conexion()
        self.cola.put(
            ("conexion_mysql", correcto, mensaje)
        )

    @staticmethod
    def _convertir_entero(
        valor: str,
        nombre: str,
    ) -> Optional[int]:
        valor = valor.strip()

        if not valor:
            return None

        numero = int(valor)

        if numero <= 0:
            raise ValueError(
                f"{nombre} debe ser mayor que cero."
            )

        return numero

    def iniciar_inventario(self) -> None:
        ruta = self.view.obtener_ruta()

        if not ruta:
            self.view.mostrar_advertencia(
                "Seleccione una carpeta antes de iniciar."
            )
            return

        try:
            limite_archivos = self._convertir_entero(
                self.view.obtener_limite_archivos(),
                "El límite de archivos",
            )
            limite_mb = self._convertir_entero(
                self.view.obtener_limite_mb(),
                "El límite en MB",
            )
        except ValueError as error:
            self.view.mostrar_error(str(error))
            return

        limite_bytes = (
            limite_mb * 1024 * 1024
            if limite_mb
            else None
        )

        self.view.limpiar_tabla()
        self.view.iniciar_progreso()
        self.view.actualizar_resumen(0, 0, 0)
        self.errores_actuales = []

        threading.Thread(
            target=self._ejecutar_escaneo,
            args=(
                ruta,
                limite_archivos,
                limite_bytes,
            ),
            daemon=True,
        ).start()

    def _ejecutar_escaneo(
        self,
        ruta: str,
        limite_archivos: Optional[int],
        limite_bytes: Optional[int],
    ) -> None:
        scanner = InventoryScanner(
            limite_archivos,
            limite_bytes,
        )

        def progreso(
            archivo,
            cantidad,
            total_bytes,
        ) -> None:
            self.cola.put(
                (
                    "archivo",
                    archivo,
                    cantidad,
                    total_bytes,
                )
            )

        try:
            archivos = scanner.escanear(
                ruta,
                callback=progreso,
            )

            id_inventario = self.repository.guardar(
                archivos=archivos,
                errores=scanner.errores,
                ruta_origen=ruta,
                limite_archivos=limite_archivos,
                limite_bytes=limite_bytes,
            )

            self.cola.put(
                (
                    "terminado",
                    archivos,
                    scanner.errores,
                    id_inventario,
                )
            )

        except Exception as error:
            self.cola.put(
                ("error", str(error))
            )

    def procesar_cola(self) -> None:
        try:
            while True:
                mensaje = self.cola.get_nowait()
                tipo = mensaje[0]

                if tipo == "archivo":
                    _, archivo, cantidad, total_bytes = mensaje

                    self.view.agregar_archivo(archivo)
                    self.view.actualizar_resumen(
                        cantidad,
                        total_bytes,
                        len(self.errores_actuales),
                    )

                elif tipo == "conexion_mysql":
                    _, correcto, texto = mensaje

                    self.view.actualizar_mysql(
                        correcto,
                        texto,
                    )

                    if correcto:
                        self.view.mostrar_informacion(
                            "Conexión correcta",
                            texto,
                        )
                    else:
                        self.view.mostrar_error(texto)

                elif tipo == "terminado":
                    _, archivos, errores, id_inventario = mensaje
                    self.errores_actuales = errores
                    total_bytes = sum(
                        archivo.tamano_bytes
                        for archivo in archivos
                    )

                    self.view.detener_progreso()
                    self.view.actualizar_resumen(
                        len(archivos),
                        total_bytes,
                        len(errores),
                    )
                    self.view.mostrar_estado(
                        "Inventario completado y guardado "
                        f"en MySQL con ID {id_inventario}."
                    )
                    self.view.mostrar_finalizado(
                        len(archivos),
                        len(errores),
                        id_inventario,
                    )

                elif tipo == "error":
                    _, error = mensaje

                    self.view.detener_progreso()
                    self.view.mostrar_estado(
                        "El proceso terminó con un error."
                    )
                    self.view.mostrar_error(error)

        except queue.Empty:
            pass

        self.view.root.after(
            100,
            self.procesar_cola,
        )
