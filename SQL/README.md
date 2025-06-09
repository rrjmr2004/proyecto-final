# Esquema de Base de Datos NBA_HoopVision para SQL Server

## 1. Introducción

Este documento describe el script DDL - Data Definition Language para crear la estructura de la base de datos `NBA_HoopVision` en un servidor Microsoft SQL Server. Esta base de datos está diseñada para almacenar información detallada sobre equipos, jugadores, partidos y estadísticas relacionadas con la NBA, obtenida a través de la automatización ETL HoopVision.

El esquema ha sido diseñado considerando la normalización básica, la integridad referencial mediante claves foráneas y la elección de tipos de datos adecuados para cada atributo. Las claves primarias que provienen del dataset de origen se han definido como `NVARCHAR(50)` para acomodar identificadores alfanuméricos.

## 2. Script de Creación de Base de Datos

El script proporcionado realiza las siguientes acciones:

1.  **Creación de la Base de Datos:**
    * Verifica si la base de datos `NBA_HoopVision` ya existe.
    * Si no existe, la crea.
    * Establece `NBA_HoopVision` como la base de datos activa para las operaciones subsiguientes.

2.  **Definición de Tablas:**
    * Se crean múltiples tablas para almacenar diferentes entidades y sus atributos.
    * Las tablas se dividen conceptualmente en "Tablas Maestras" (entidades principales como `team` y `player`) y "Tablas de Detalle" (información más granular o transaccional).

## 3. Descripción del Esquema

A continuación, se detallan las tablas creadas por el script:

---
### 3.1. Tablas Maestras

Estas tablas almacenan información fundamental sobre las entidades principales del dominio.

* **`dbo.team`**:
    * **Propósito:** Almacena información básica sobre cada equipo de la NBA.
    * **Clave Primaria:** `id` (NVARCHAR(50))
    * **Campos Notables:** `full_name`, `abbreviation` (UNIQUE), `nickname`, `city`, `state`, `year_founded`.

* **`dbo.player`**:
    * **Propósito:** Almacena información básica sobre cada jugador.
    * **Clave Primaria:** `id` (NVARCHAR(50))
    * **Campos Notables:** `full_name`, `first_name`, `last_name`, `is_active` (BIT).

---
### 3.2. Tablas de Detalle

Estas tablas contienen información más específica, estadísticas o eventos relacionados con las tablas maestras.

* **`dbo.team_details`**:
    * **Propósito:** Almacena detalles adicionales de los equipos.
    * **Clave Primaria:** `team_id` (NVARCHAR(50))
    * **Clave Foránea:** `team_id` -> `team(id)`

* **`dbo.common_player_info`**:
    * **Propósito:** Contiene información detallada y común sobre los jugadores, incluyendo datos biográficos, de equipo y de draft.
    * **Clave Primaria:** `person_id` (NVARCHAR(50))
    * **Claves Foráneas:**
        * `person_id` -> `player(id)`
        * `team_id` -> `team(id)`

* **`dbo.game`**:
    * **Propósito:** Registra información detallada de cada partido, incluyendo estadísticas para el equipo local y visitante.
    * **Clave Primaria:** `game_id` (NVARCHAR(50))
    * **Claves Foráneas:**
        * `team_id_home` -> `team(id)`
        * `team_id_away` -> `team(id)`


* **`dbo.draft_history`**:
    * **Propósito:** Almacena el historial del draft para cada jugador.
    * **Clave Primaria Compuesta:** `(person_id, season)` (NVARCHAR(50), INT)
    * **Claves Foráneas:**
        * `person_id` -> `player(id)`
        * `team_id` -> `team(id)`

* **`dbo.draft_combine_stats`**:
    * **Propósito:** Contiene las estadísticas y mediciones de los jugadores obtenidas en el NBA Draft Combine.
    * **Clave Primaria Compuesta:** `(season, player_id)` (INT, NVARCHAR(50))
    * **Clave Foránea:** `player_id` -> `player(id)`

* **`dbo.other_stats`**:
    * **Propósito:** Almacena estadísticas adicionales del partido no cubiertas en la tabla `game`, como puntos en la pintura, puntos de segunda oportunidad, etc.
    * **Clave Primaria:** `game_id` (NVARCHAR(50))
    * **Claves Foráneas:**
        * `game_id` -> `game(game_id)`
        * `team_id_home` -> `team(id)`
        * `team_id_away` -> `team(id)`

* **`dbo.line_score`**:
    * **Propósito:** Registra el marcador por cuarto y tiempo extra para cada partido.
    * **Clave Primaria:** `game_id` (NVARCHAR(50))
    * **Claves Foráneas:**
        * `game_id` -> `game(game_id)`
        * `team_id_home` -> `team(id)`
        * `team_id_away` -> `team(id)`

---
## 4. Consideraciones Importantes

* **Tipos de Datos para IDs:** Todas las claves primarias que representan identificadores provenientes del dataset de origen (como `team.id`, `player.id`, `game.game_id`) se definen como `NVARCHAR(50)`. Esto proporciona flexibilidad para manejar IDs que puedan contener caracteres no numéricos.
* **Integridad Referencial:** Se utilizan `FOREIGN KEY` constraints para asegurar la consistencia entre las tablas. Por ejemplo, un `game` siempre debe tener `team_id_home` y `team_id_away` válidos que existan en la tabla `team`.
* **Nulabilidad:** Los campos se definen como `NULL` o `NOT NULL` según la obligatoriedad de la información.
* **Restricciones `UNIQUE`:** Se aplica una restricción `UNIQUE` en `team.abbreviation` para asegurar que las abreviaturas de los equipos sean únicas.
* **Comandos `GO`:** El comando `GO` se utiliza como un separador de lotes en T-SQL, asegurando que cada `CREATE TABLE` (y otras operaciones DDL) se ejecute en su propio lote.
* **Mensajes de Progreso:** El script incluye sentencias `PRINT` para mostrar el progreso durante la ejecución.

## 5. Instrucciones de Ejecución

1.  **Conexión:** Conéctese a su instancia de Microsoft SQL Server utilizando la herramienta SQL Server Management Studio (SSMS).
2.  **Permisos:** Asegúrese de que el usuario con el que se conecta tiene los permisos necesarios para crear bases de datos y tablas (ej. miembro del rol `dbcreator` o `sysadmin` para crear la base de datos, y `db_ddladmin` sobre la base de datos para crear tablas).
3.  **Ejecución:**
    * Abra una nueva ventana de consulta.
    * Copie y pegue el contenido completo del script SQL proporcionado.
    * Ejecute el script.
4.  **Verificación:** Una vez ejecutado el script, verifique la creación de la base de datos `NBA_HoopVision` y todas sus tablas en el Explorador de Objetos de su herramienta de gestión de SQL Server.

Este esquema proporciona una base sólida para el almacenamiento y posterior análisis de datos de la NBA.