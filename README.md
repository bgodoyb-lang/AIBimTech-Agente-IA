# AIBim Tech — MVC conectado a MySQL

Esta versión mantiene la interfaz y el patrón MVC, pero reemplaza el
almacenamiento SQLite por la base de datos MySQL diseñada para el proyecto.

## Estructura principal

```text
AIBimTech_MVC_MySQL/
├── app.py
├── config/
│   └── database_config.py
├── controllers/
│   └── inventory_controller.py
├── models/
│   └── archivo.py
├── repositories/
│   └── mysql_repository.py
├── services/
│   └── inventory_scanner.py
├── views/
│   └── inventory_view.py
├── sql/
│   └── aibimtech_sprint1.sql
└── requirements.txt
```

## 1. Instalar el conector

En la terminal de VS Code:

```powershell
python -m pip install -r requirements.txt
```

## 2. Crear la base de datos

1. Abre MySQL Workbench.
2. Abre `sql/aibimtech_sprint1.sql`.
3. Ejecuta el script
4. Actualiza el panel **Schemas**.
5. Debe aparecer la base `aibimtech` con las diez tablas.

## 3. Configura la contraseña

Abre:

```text
config/database_config.py
```

Cambia:

```python
"password": "CAMBIAR_AQUI",
```

por la contraseña que utilizas para conectarte como `root` en Workbench.

También revisa el host, puerto y usuario si tu conexión usa otros valores.

## 4. Ejecutar

```powershell
python app.py
```

Primero pulsa **Probar conexión MySQL**.

Después selecciona una carpeta y pulsa **Iniciar inventario**.

## 5. Verificar los datos en Workbench

Ejecuta:

```sql
USE aibimtech;

SELECT * FROM inventarios ORDER BY id_inventario DESC;
SELECT * FROM archivos ORDER BY id_archivo DESC;
SELECT * FROM registros_operacion ORDER BY id_registro DESC;
SELECT * FROM puntos_control ORDER BY id_punto_control DESC;
```

La aplicación debe mostrar el ID del inventario creado.
