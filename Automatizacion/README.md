# Automatización ETL: Kaggle Data to SQL Server (HoopVision)

## 1. Visión General

Este proyecto implementa un pipeline ETL (Extract, Transform, Load) automatizado para ingestar datos de baloncesto desde un dataset público en Kaggle, procesarlos y cargarlos en una base de datos SQL Server. El objetivo es mantener un data warehouse actualizado con estadísticas de baloncesto, listo para análisis y visualización. El script está diseñado con un enfoque en la robustez, la carga incremental y la mantenibilidad, utilizando Python y diversas bibliotecas para la manipulación de datos y la interacción con bases de datos.

El pipeline se encarga de verificar si existen actualizaciones en el dataset de origen, descargar los datos si es necesario, realizar transformaciones para asegurar la calidad y consistencia de los datos, y finalmente, cargar la información de manera incremental en las tablas correspondientes del SQL Server.

## 2. Características Principales

* **Extracción Automatizada desde Kaggle:** Utiliza la API de Kaggle para verificar y descargar la última versión del dataset.
* **Carga Incremental:** Identifica y carga únicamente registros nuevos o actualizados en la base de datos SQL Server, optimizando el proceso y evitando duplicados.
* **Transformación de Datos:** Incluye limpieza de datos (duplicados, nulos), conversión de tipos (e.g., altura de formato 'pies-pulgadas' a pulgadas, flags 'Y'/'N' a booleanos) y validaciones de integridad referencial.
* **Manejo de Múltiples Entidades:** Procesa y carga datos para diversas tablas relacionadas (equipos, jugadores, partidos, estadísticas de draft, etc.).
* **Configuración Centralizada:** Utiliza variables de entorno (`.env`) para gestionar configuraciones sensibles y específicas del entorno (credenciales, rutas).
* **Logging Informativo:** Proporciona retroalimentación detallada sobre el progreso y los resultados de cada etapa del proceso ETL.
* **Interfaz de Consola Mejorada:** Utiliza colores para una mejor legibilidad de los mensajes en la consola.

## 3. Stack Tecnológico

* **Lenguaje de Programación:** Python 3.13.3
* **Gestión de Datos:**
    * Pandas: Para manipulación y transformación de DataFrames.
    * SQLAlchemy: Para interactuar con SQL Server.
    * SQLite3: Como base de datos de origen o staging (leída directamente del dataset descargado).
* **Interacción con APIs:**
    * Kaggle API: Para la descarga y verificación de datasets.
* **Gestión de Entorno:**
    * `python-dotenv`: Para cargar variables de entorno.
* **Logging:**
    * `logging`: Módulo estándar de Python.

## 4. Configuración del Entorno

Antes de ejecutar el script, es necesario configurar las siguientes variables de entorno en un archivo `.env` ubicado en la raíz del proyecto:

```plaintext
# Credenciales y Metadatos de Kaggle
KAGGLE_DATASET_SLUG="USUARIO_KAGGLE/NOMBRE_DATASET"  # Ej: "wyattowalsh/basketball"
KAGGLE_FILE_NAME="nombre_del_archivo_principal.sqlite" # Ej: "basketball.sqlite" - Archivo clave para la verificación de tamaño
LOCAL_FILE_PATH="./nombre_del_archivo_principal.sqlite" # Ruta local donde se espera el archivo descargado (usado para la verificación de tamaño)

# Configuración de la Base de Datos Staging/Origen (SQLite)
SQLITE_DB_PATH="./nombre_del_archivo_principal.sqlite" # Ruta al archivo SQLite descargado de Kaggle

# Configuración de SQL Server (Destino)
SQL_SERVER_DRIVER="ODBC Driver 17 for SQL Server" # Ajustar según el driver instalado
SQL_SERVER_NAME="NOMBRE_SERVIDOR\\INSTANCIA_SQL"   # Ej: "localhost\SQLEXPRESS"
SQL_DATABASE_NAME="NombreDeTuBaseDeDatos"
SQL_SCHEMA="dbo" # Esquema a utilizar en SQL Server