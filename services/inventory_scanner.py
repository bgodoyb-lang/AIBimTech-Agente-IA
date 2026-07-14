from __future__ import annotations

import mimetypes
import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from models.archivo import Archivo


class InventoryScanner:
    FORMATOS = {
        ".pdf": "PDF",
        ".txt": "Texto",
        ".docx": "Documento Word",
        ".xlsx": "Hoja de cálculo Excel",
        ".csv": "CSV",
        ".jpg": "Imagen JPEG",
        ".jpeg": "Imagen JPEG",
        ".png": "Imagen PNG",
        ".mp3": "Audio MP3",
        ".wav": "Audio WAV",
        ".m4a": "Audio M4A",
        ".zip": "Archivo comprimido ZIP",
        ".rar": "Archivo comprimido RAR",
    }

    def __init__(
        self,
        limite_archivos: Optional[int] = None,
        limite_bytes: Optional[int] = None,
    ) -> None:
        self.limite_archivos = limite_archivos if limite_archivos and limite_archivos > 0 else None
        self.limite_bytes = limite_bytes if limite_bytes and limite_bytes > 0 else None
        self.errores: list[str] = []

    @staticmethod
    def _formatear_fecha(timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    def _crear_archivo(self, ruta_archivo: Path) -> Archivo:
        datos = ruta_archivo.stat()
        extension = ruta_archivo.suffix.lower()
        tipo_mime = mimetypes.guess_type(str(ruta_archivo))[0] or "desconocido"
        categoria = self.FORMATOS.get(
            extension,
            "OTRO" if extension else "SIN_EXTENSION",
        )

        return Archivo(
            nombre=ruta_archivo.name,
            extension=extension.lstrip("."),
            tipo_mime=tipo_mime,
            categoria_tipo=categoria,
            ruta=str(ruta_archivo.resolve()),
            tamano_bytes=datos.st_size,
            fecha_creacion=self._formatear_fecha(datos.st_ctime),
            fecha_modificacion=self._formatear_fecha(datos.st_mtime),
        )

    def escanear(
        self,
        ruta_origen: str,
        callback: Optional[Callable[[Archivo, int, int], None]] = None,
    ) -> list[Archivo]:
        ruta = Path(ruta_origen).expanduser()

        if not ruta.exists():
            raise FileNotFoundError(f"La ruta no existe: {ruta}")
        if not ruta.is_dir():
            raise NotADirectoryError(f"La ruta no es una carpeta: {ruta}")
        if not os.access(ruta, os.R_OK):
            raise PermissionError(f"No hay permisos de lectura para: {ruta}")

        archivos_encontrados: list[Archivo] = []
        total_bytes = 0
        self.errores.clear()

        for carpeta_actual, carpetas, archivos in os.walk(ruta, followlinks=False):
            carpetas[:] = [
                nombre
                for nombre in carpetas
                if not (Path(carpeta_actual) / nombre).is_symlink()
            ]

            for nombre_archivo in archivos:
                if self.limite_archivos is not None and len(archivos_encontrados) >= self.limite_archivos:
                    return archivos_encontrados

                ruta_archivo = Path(carpeta_actual) / nombre_archivo

                try:
                    archivo = self._crear_archivo(ruta_archivo)

                    if (
                        self.limite_bytes is not None
                        and total_bytes + archivo.tamano_bytes > self.limite_bytes
                    ):
                        return archivos_encontrados

                    archivos_encontrados.append(archivo)
                    total_bytes += archivo.tamano_bytes

                    if callback:
                        callback(archivo, len(archivos_encontrados), total_bytes)

                except (OSError, ValueError) as error:
                    self.errores.append(f"{ruta_archivo}: {error}")

        return archivos_encontrados
