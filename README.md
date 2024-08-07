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

2. Crea y activa un entorno virtual:

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instala las dependencias necesarias:

    ```bash
    pip install -r requirements.txt
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

### Migraciones de Base de Datos

1. Inicializa las migraciones:

    ```bash
    flask db init
    ```

2. Crea una migración inicial:

    ```bash
    flask db migrate -m "Initial migration."
    ```

3. Aplica las migraciones:

    ```bash
    flask db upgrade
    ```

### Ejecución del Proyecto

1. Configura las variables de entorno (opcional):

    ```bash
    export FLASK_APP=app.py
    export FLASK_ENV=development  # En Windows usa `set` en lugar de `export`
    ```

2. Ejecuta la aplicación:

    ```bash
    flask run
    ```

La aplicación estará disponible en `http://127.0.0.1:5000`.

### Estructura del Proyecto

- `app.py`: Archivo principal de la aplicación donde se configuran las rutas y modelos.
- `requirements.txt`: Archivo que contiene todas las dependencias del proyecto.
- `migrations/`: Carpeta que contiene los archivos relacionados con las migraciones de base de datos.
- `tests/`: Carpeta que contiene los archivos de pruebas unitarias y de integración.
- `static/`: Carpeta para archivos estáticos como CSS, JavaScript, etc.
- `templates/`: Carpeta para plantillas HTML.

### Funcionalidades

- Registro e inicio de sesión de usuarios.
- Creación, visualización y gestión de temas.
- Adición de respuestas y calificaciones a los temas.
- Gestión de usuarios, asignaturas, evaluaciones y calificaciones.
- Registro de asistencia.

### Contribuir

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -am 'Añadir nueva funcionalidad'`).
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.


