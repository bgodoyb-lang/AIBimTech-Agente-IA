"""
Configuración local de MySQL.

Cambia solamente los valores necesarios para que coincidan con la conexión
que utilizas en MySQL Workbench.
"""
import os

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": os.getenv("AIBIMTECH_DB_PASSWORD", ""),
    "database": "aibimtech",
}

APP_USER_ID = 1