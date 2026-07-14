from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Optional

from models.archivo import Archivo

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError as error:
    raise ImportError(
        "Falta MySQL Connector/Python. Instálalo con: "
        "python -m pip install mysql-connector-python"
    ) from error


class MySQLInventoryRepository:
    """Guarda el inventario y sus operaciones en MySQL."""

    def __init__(
        self,
        db_config: dict[str, Any],
        id_usuario: int = 1,
    ) -> None:
        self.db_config = db_config
        self.id_usuario = id_usuario

    def _conectar(self):
        return mysql.connector.connect(**self.db_config)

    def probar_conexion(self) -> tuple[bool, str]:
        conexion = None

        try:
            conexion = self._conectar()

            if conexion.is_connected():
                return True, (
                    "Conexión correcta con la base de datos "
                    f"`{self.db_config['database']}`."
                )

            return False, "MySQL no confirmó la conexión."

        except Error as error:
            return False, self._traducir_error(error)

        finally:
            if conexion is not None and conexion.is_connected():
                conexion.close()

    @staticmethod
    def _traducir_error(error: Error) -> str:
        numero = getattr(error, "errno", None)

        if numero == 1045:
            return (
                "MySQL rechazó el usuario o la contraseña. "
                "Revisa config/database_config.py."
            )

        if numero == 1049:
            return (
                "La base de datos no existe. Ejecuta primero "
                "sql/aibimtech_sprint1.sql en MySQL Workbench."
            )

        if numero in (2003, 2005):
            return (
                "No fue posible encontrar el servidor MySQL. "
                "Verifica que MySQL esté iniciado y que el host y puerto sean correctos."
            )

        return f"Error de MySQL: {error}"

    @staticmethod
    def _datos_unidad(ruta_origen: str) -> tuple[str, int, int]:
        ruta = Path(ruta_origen)
        nombre = ruta.anchor or ruta.name or "Unidad local"

        try:
            uso = shutil.disk_usage(ruta_origen)
            return nombre, uso.total, uso.free
        except OSError:
            return nombre, 0, 0

    @staticmethod
    def _buscar_o_crear_tipo(cursor, archivo: Archivo) -> int:
        extension = archivo.extension.lower()

        cursor.execute(
            """
            SELECT id_tipo_archivo
            FROM tipos_archivo
            WHERE extension = %s
            LIMIT 1
            """,
            (extension,),
        )
        fila = cursor.fetchone()

        if fila:
            return int(fila[0])

        cursor.execute(
            """
            INSERT INTO tipos_archivo (
                nombre_tipo,
                extension,
                tipo_mime
            ) VALUES (%s, %s, %s)
            """,
            (
                archivo.categoria_tipo,
                extension,
                archivo.tipo_mime,
            ),
        )

        return int(cursor.lastrowid)

    def guardar(
        self,
        archivos: list[Archivo],
        errores: list[str],
        ruta_origen: str,
        limite_archivos: Optional[int] = None,
        limite_bytes: Optional[int] = None,
    ) -> int:
        conexion = None
        cursor = None

        try:
            conexion = self._conectar()
            cursor = conexion.cursor()

            nombre_unidad, capacidad_total, espacio_disponible = (
                self._datos_unidad(ruta_origen)
            )

            cursor.execute(
                """
                INSERT INTO unidades_almacenamiento (
                    nombre,
                    ruta,
                    capacidad_total,
                    espacio_disponible,
                    tipo_unidad,
                    fecha_registro
                ) VALUES (%s, %s, %s, %s, %s, NOW())
                """,
                (
                    nombre_unidad,
                    ruta_origen,
                    capacidad_total,
                    espacio_disponible,
                    "CARPETA_LOCAL",
                ),
            )
            id_unidad = int(cursor.lastrowid)

            cursor.execute(
                """
                INSERT INTO configuraciones_analisis (
                    volumen_maximo,
                    cantidad_maxima_archivos,
                    ruta_seleccionada,
                    fecha_configuracion
                ) VALUES (%s, %s, %s, NOW())
                """,
                (
                    limite_bytes,
                    limite_archivos,
                    ruta_origen,
                ),
            )
            id_configuracion = int(cursor.lastrowid)

            cursor.execute(
                """
                INSERT INTO inventarios (
                    id_usuario,
                    id_unidad,
                    id_configuracion,
                    fecha_inicio,
                    cantidad_archivos,
                    estado
                ) VALUES (%s, %s, %s, NOW(), 0, 'EN_PROCESO')
                """,
                (
                    self.id_usuario,
                    id_unidad,
                    id_configuracion,
                ),
            )
            id_inventario = int(cursor.lastrowid)

            for archivo in archivos:
                id_tipo_archivo = self._buscar_o_crear_tipo(
                    cursor,
                    archivo,
                )

                cursor.execute(
                    """
                    INSERT INTO archivos (
                        id_inventario,
                        id_tipo_archivo,
                        id_categoria,
                        nombre_original,
                        nombre_actual,
                        extension,
                        ruta_original,
                        ruta_actual,
                        tamano,
                        fecha_creacion,
                        fecha_modificacion,
                        hash_sha256,
                        estado
                    ) VALUES (
                        %s, %s, NULL, %s, %s, %s, %s, %s,
                        %s, %s, %s, NULL, %s
                    )
                    """,
                    (
                        id_inventario,
                        id_tipo_archivo,
                        archivo.nombre,
                        archivo.nombre,
                        archivo.extension,
                        archivo.ruta,
                        archivo.ruta,
                        archivo.tamano_bytes,
                        archivo.fecha_creacion,
                        archivo.fecha_modificacion,
                        archivo.estado,
                    ),
                )
                id_archivo = int(cursor.lastrowid)

                cursor.execute(
                    """
                    INSERT INTO registros_operacion (
                        id_usuario,
                        id_archivo,
                        fecha_hora,
                        tipo_operacion,
                        ruta_original,
                        ruta_nueva,
                        resultado,
                        mensaje_error
                    ) VALUES (
                        %s, %s, NOW(), 'INVENTARIAR',
                        %s, NULL, 'EXITOSO', NULL
                    )
                    """,
                    (
                        self.id_usuario,
                        id_archivo,
                        archivo.ruta,
                    ),
                )

                cursor.execute(
                    """
                    INSERT INTO registros_operacion (
                        id_usuario,
                        id_archivo,
                        fecha_hora,
                        tipo_operacion,
                        ruta_original,
                        ruta_nueva,
                        resultado,
                        mensaje_error
                    ) VALUES (
                        %s, %s, NOW(), 'IDENTIFICAR_TIPO',
                        %s, NULL, 'EXITOSO', NULL
                    )
                    """,
                    (
                        self.id_usuario,
                        id_archivo,
                        archivo.ruta,
                    ),
                )

            cursor.execute(
                """
                UPDATE inventarios
                SET fecha_termino = NOW(),
                    cantidad_archivos = %s,
                    estado = %s
                WHERE id_inventario = %s
                """,
                (
                    len(archivos),
                    "COMPLETADO_CON_ERRORES" if errores else "COMPLETADO",
                    id_inventario,
                ),
            )

            cursor.execute(
                """
                INSERT INTO puntos_control (
                    id_inventario,
                    fecha_hora,
                    ultimo_archivo_procesado,
                    archivos_procesados,
                    estado
                ) VALUES (%s, NOW(), %s, %s, %s)
                """,
                (
                    id_inventario,
                    archivos[-1].ruta if archivos else None,
                    len(archivos),
                    "COMPLETADO",
                ),
            )

            conexion.commit()
            return id_inventario

        except Error as error:
            if conexion is not None:
                conexion.rollback()

            raise RuntimeError(
                self._traducir_error(error)
            ) from error

        finally:
            if cursor is not None:
                cursor.close()

            if conexion is not None and conexion.is_connected():
                conexion.close()
