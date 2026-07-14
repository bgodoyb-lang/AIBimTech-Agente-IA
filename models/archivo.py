from dataclasses import dataclass


@dataclass
class Archivo:
    nombre: str
    extension: str
    tipo_mime: str
    categoria_tipo: str
    ruta: str
    tamano_bytes: int
    fecha_creacion: str
    fecha_modificacion: str
    estado: str = "INVENTARIADO"
