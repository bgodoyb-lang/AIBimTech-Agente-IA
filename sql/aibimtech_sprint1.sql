CREATE DATABASE IF NOT EXISTS aibimtech
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE aibimtech;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(120) NOT NULL UNIQUE,
    rol VARCHAR(30) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS unidades_almacenamiento (
    id_unidad INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    ruta VARCHAR(500) NOT NULL,
    capacidad_total BIGINT UNSIGNED NOT NULL,
    espacio_disponible BIGINT UNSIGNED NOT NULL,
    tipo_unidad VARCHAR(50) NOT NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS configuraciones_analisis (
    id_configuracion INT PRIMARY KEY AUTO_INCREMENT,
    volumen_maximo BIGINT UNSIGNED NULL,
    cantidad_maxima_archivos INT UNSIGNED NULL,
    ruta_seleccionada VARCHAR(500) NOT NULL,
    fecha_configuracion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS inventarios (
    id_inventario INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_unidad INT NOT NULL,
    id_configuracion INT NOT NULL UNIQUE,
    fecha_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_termino DATETIME NULL,
    cantidad_archivos INT UNSIGNED NOT NULL DEFAULT 0,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT fk_inventarios_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_inventarios_unidad
        FOREIGN KEY (id_unidad)
        REFERENCES unidades_almacenamiento(id_unidad)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_inventarios_configuracion
        FOREIGN KEY (id_configuracion)
        REFERENCES configuraciones_analisis(id_configuracion)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tipos_archivo (
    id_tipo_archivo INT PRIMARY KEY AUTO_INCREMENT,
    nombre_tipo VARCHAR(50) NOT NULL,
    extension VARCHAR(20) NOT NULL UNIQUE,
    tipo_mime VARCHAR(150) NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NULL,
    ruta_destino VARCHAR(500) NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS archivos (
    id_archivo INT PRIMARY KEY AUTO_INCREMENT,
    id_inventario INT NOT NULL,
    id_tipo_archivo INT NOT NULL,
    id_categoria INT NULL,
    nombre_original VARCHAR(255) NOT NULL,
    nombre_actual VARCHAR(255) NOT NULL,
    extension VARCHAR(20) NULL,
    ruta_original VARCHAR(1000) NOT NULL,
    ruta_actual VARCHAR(1000) NOT NULL,
    tamano BIGINT UNSIGNED NOT NULL,
    fecha_creacion DATETIME NULL,
    fecha_modificacion DATETIME NULL,
    hash_sha256 CHAR(64) NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT fk_archivos_inventario
        FOREIGN KEY (id_inventario)
        REFERENCES inventarios(id_inventario)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_archivos_tipo
        FOREIGN KEY (id_tipo_archivo)
        REFERENCES tipos_archivo(id_tipo_archivo)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_archivos_categoria
        FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS metadatos (
    id_metadato INT PRIMARY KEY AUTO_INCREMENT,
    id_archivo INT NOT NULL,
    clave VARCHAR(100) NOT NULL,
    valor TEXT NULL,
    fecha_extraccion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_metadatos_archivo
        FOREIGN KEY (id_archivo)
        REFERENCES archivos(id_archivo)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS registros_operacion (
    id_registro INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_archivo INT NOT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_operacion VARCHAR(50) NOT NULL,
    ruta_original VARCHAR(1000) NULL,
    ruta_nueva VARCHAR(1000) NULL,
    resultado VARCHAR(30) NOT NULL,
    mensaje_error TEXT NULL,
    CONSTRAINT fk_registros_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_registros_archivo
        FOREIGN KEY (id_archivo)
        REFERENCES archivos(id_archivo)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS puntos_control (
    id_punto_control INT PRIMARY KEY AUTO_INCREMENT,
    id_inventario INT NOT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_archivo_procesado VARCHAR(1000) NULL,
    archivos_procesados INT UNSIGNED NOT NULL DEFAULT 0,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT fk_puntos_inventario
        FOREIGN KEY (id_inventario)
        REFERENCES inventarios(id_inventario)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;

INSERT IGNORE INTO usuarios (
    id_usuario,
    nombre_usuario,
    contrasena_hash,
    nombre,
    correo,
    rol,
    activo
) VALUES (
    1,
    'admin',
    SHA2('Cambiar123!', 256),
    'Administrador de prueba',
    'admin@aibimtech.local',
    'ADMINISTRADOR',
    1
);

INSERT IGNORE INTO tipos_archivo (
    nombre_tipo,
    extension,
    tipo_mime
) VALUES
    ('PDF', 'pdf', 'application/pdf'),
    ('Texto', 'txt', 'text/plain'),
    ('Documento Word', 'docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
    ('Hoja de cálculo Excel', 'xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    ('CSV', 'csv', 'text/csv'),
    ('Imagen JPEG', 'jpg', 'image/jpeg'),
    ('Imagen JPEG', 'jpeg', 'image/jpeg'),
    ('Imagen PNG', 'png', 'image/png'),
    ('Audio MP3', 'mp3', 'audio/mpeg'),
    ('Audio WAV', 'wav', 'audio/wav'),
    ('Audio M4A', 'm4a', 'audio/mp4'),
    ('Archivo ZIP', 'zip', 'application/zip'),
    ('Archivo RAR', 'rar', 'application/vnd.rar');
