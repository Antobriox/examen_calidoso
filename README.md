# Foro en Línea

Este es un proyecto de foro en línea desarrollado con Flask y PostgreSQL. Permite a los usuarios registrarse, iniciar sesión, crear temas y agregar respuestas a los temas existentes.

## Configuración del Proyecto

### Prerrequisitos

1. Python 3.x
2. PostgreSQL

### Instalación

1. Clona este repositorio en tu máquina local:

    ```bash
    git clone https://github.com/tu_usuario/tu_repositorio.git
    cd tu_repositorio
    ```



### Configuración de la Base de Datos

1. Asegúrate de tener PostgreSQL instalado y en funcionamiento en tu máquina.
2. Crea una base de datos llamada `foro_linea`:

    ```sql
    CREATE DATABASE foro_linea;
    ```

3. Ejecuta los siguientes queries para crear las tablas necesarias:

    ```sql

    
    CREATE TABLE Usuarios (
        id SERIAL PRIMARY KEY,
        nombre_usuario VARCHAR(100),
        email VARCHAR(100),
        contraseña VARCHAR(100)
    );

    CREATE TABLE Temas (
        id SERIAL PRIMARY KEY,
        titulo VARCHAR(100),
        descripcion TEXT,
        id_usuario INT,
        fecha_creacion DATE,
        FOREIGN KEY (id_usuario) REFERENCES Usuarios(id)
    );

    CREATE TABLE Respuestas (
        id SERIAL PRIMARY KEY,
        id_tema INT,
        id_usuario INT,
        contenido TEXT,
        fecha_respuesta DATE,
        FOREIGN KEY (id_tema) REFERENCES Temas(id),
        FOREIGN KEY (id_usuario) REFERENCES Usuarios(id)
    );
    ```


### Estructura del Proyecto

Ejecuta el codigo en app.py


