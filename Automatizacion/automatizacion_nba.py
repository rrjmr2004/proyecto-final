from kaggle.api.kaggle_api_extended import KaggleApi
import kaggle
from dotenv import load_dotenv
import os
import pandas as pd
import sqlite3
from sqlalchemy import create_engine, types, text
import pyodbc 
import logging
import time
import sys

# --- Configuración ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Acceder a las variables cargadas
KAGGLE_DATASET_SLUG = os.getenv('KAGGLE_DATASET_SLUG')
KAGGLE_FILE_NAME = os.getenv('KAGGLE_FILE_NAME')
LOCAL_FILE_PATH = os.getenv('LOCAL_FILE_PATH')
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH')
SQL_SERVER_DRIVER = os.getenv('SQL_SERVER_DRIVER')
SQL_SERVER_NAME = os.getenv('SQL_SERVER_NAME')
SQL_DATABASE_NAME = os.getenv('SQL_DATABASE_NAME')
SQL_SCHEMA = os.getenv('SQL_SCHEMA')


# Es importante verificar que las variables no sean None antes de usarlas en el f-string
# si existe la posibilidad de que no estén definidas en el .env
if SQL_SERVER_NAME and SQL_DATABASE_NAME and SQL_SERVER_DRIVER:
    SQL_SERVER_CONN_STR = (
        f"mssql+pyodbc://{SQL_SERVER_NAME}/{SQL_DATABASE_NAME}?"
        f"driver={SQL_SERVER_DRIVER.replace(' ', '+')}&trusted_connection=yes" # Reemplazar espacios en el driver para URL
    )
else:
    SQL_SERVER_CONN_STR = None
    print("Advertencia: Alguna de las variables para la cadena de conexión SQL Server no está definida.")
# Definición de colores ANSI
class AnsiColors:
    """Clase para almacenar códigos de color ANSI."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    # Colores de texto
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    # Colores de fondo
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

def imprimir_letra_por_letra(texto, color_texto=AnsiColors.WHITE, delay=0.05):
    """Imprime un texto carácter por carácter con un color y delay específicos."""
    for char in texto:
        sys.stdout.write(color_texto + char + AnsiColors.RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print() # Para el salto de línea final

# Crear conexión a SQLite
conn_sqlite = sqlite3.connect(SQLITE_DB_PATH)
# Crear conexión a SQL Server
engine_sql_server = create_engine(SQL_SERVER_CONN_STR)

def verificar_actualizacion():

    api = KaggleApi()

    imprimir_letra_por_letra( "🔑Iniciando la autenticación con Kaggle...", AnsiColors.CYAN, delay=0.025)
    api.authenticate() # Se autentica usando el archivo kaggle.json
    time.sleep(1.75)
    imprimir_letra_por_letra( "✅Autenticación exitosa.", AnsiColors.CYAN, delay=0.025)
    print()
    time.sleep(.25)
    files = api.dataset_list_files(KAGGLE_DATASET_SLUG).files
    time.sleep(.25)
    print("Obteniendo metadata de los archivos en el dataset de Kaggle:")
    for i in range(len(files)):
        print( "🏀" + f"{files[i].name}, Tamaño: {files[i].total_bytes}" + AnsiColors.RESET)
        time.sleep(i/20)
    
    # si la tabla team de la basae de datos sql server está vacia return true
    query = f"SELECT COUNT(*) as row_count FROM team"
    df_count = pd.read_sql(query, engine_sql_server)

    if not df_count.empty:
        count = df_count['row_count'].iloc[0]  # Obtiene el valor del conteo

        if count == 0:
            print(f"⚙️La base de datos SQL Server requiere actualización.")
            print()
            return True 

    local_file = LOCAL_FILE_PATH
    if os.path.exists(local_file):
        #obtener el tamaño del archivo local a partir de la lectura del archivo file_size.txt que contiene el tamaño del archivo local
        local_size = os.path.getsize(local_file)
        print()
        imprimir_letra_por_letra( "📂Verificando tamaños ...", AnsiColors.CYAN, delay=0.025)
        print()
        # Buscar el archivo correspondiente en Kaggle
        kaggle_file = next((f for f in files if f.name == KAGGLE_FILE_NAME), None)
        if kaggle_file:
            if local_size == kaggle_file.total_bytes:
                print("✅La base de datos está ACTUALIZADA.")
                return False
            else:
                print("✨la base de datos está DESACTUALIZADA.")
                # Aquí podrías llamar a la función para descargar la actualización
                return True
    else:
        print(f"\nEl archivo local {local_file} no existe.")
        return True



def descargar_dataset():
    
    api = KaggleApi()
    api.authenticate()
    print()
    print(f"📥 Descargando dataset {KAGGLE_DATASET_SLUG} desde Kaggle...")
    api.dataset_download_files(KAGGLE_DATASET_SLUG, path='.', unzip=True, quiet=False)
    print("✅Descarga completada.")
    time.sleep(.25)
    print()
    print("🤖ANALIZANDO Y CARGANDO DATOS:")
    
def cargar_team():
    print("-----------------------------------------------------------------------")
    # Leer datos de la tabla team desde SQLite
    df_team = pd.read_sql_query("SELECT * FROM team", conn_sqlite)

    # Eliminar filas duplicadas y completamente vacías
    df_team = df_team.drop_duplicates().dropna(how='all')

    # Leer los ids existentes en SQL Server (si la tabla existe)
    try:
        df_team_sql = pd.read_sql_query(f"SELECT id FROM {SQL_SCHEMA}.team", engine_sql_server)
        ids_team_existentes = set(df_team_sql['id'].astype(str))
    except Exception as e:
        print("No se pudo leer la tabla team en SQL Server (puede que no exista aún). Se insertarán todos los registros.")
        ids_team_existentes = set()

    # Filtrar solo los registros cuyo id no existe ya en SQL Server
    df_team_nuevos = df_team[~df_team['id'].astype(str).isin(ids_team_existentes)]

    # Insertar los nuevos registros en SQL Server
    if not df_team_nuevos.empty:
        df_team_nuevos.to_sql(
            name='team',
            con=engine_sql_server,
            schema=SQL_SCHEMA,
            if_exists='append',
            index=False,
        )
        print(f"📄Se insertaron {len(df_team_nuevos)} registros nuevos en la tabla team.")
        
    else:
        print("No hay nuevos registros para insertar en team.")

def cargar_player():
    print("-----------------------------------------------------------------------")
    # Traer los datos de la tabla player desde SQLite
    df_player = pd.read_sql_query("SELECT * FROM player", conn_sqlite)

    # Leer la tabla player desde SQL Server
    df_player_sql = pd.read_sql_query(f"SELECT * FROM {SQL_SCHEMA}.player", engine_sql_server)

    df_player['is_active'] = df_player['is_active'].astype(bool)

    # Eliminar filas duplicadas y filas completamente vacías en df_player
    df_player = df_player.drop_duplicates().dropna(how='all')
    

    # Insertar solo los registros cuyo id no existe ya en SQL Server
    ids_existentes = set(df_player_sql['id'].astype(str))
    df_nuevos = df_player[~df_player['id'].astype(str).isin(ids_existentes)]

    if not df_nuevos.empty:
        df_nuevos.to_sql(
            name='player',
            con=engine_sql_server,
            schema=SQL_SCHEMA,
            if_exists='append',  # Cambia a 'replace' si quieres reemplazar la tabla
            index=False,
        )
        print(f"📄Se insertaron {len(df_nuevos)} registros nuevos en la tabla player.")
        
    else:
        print("No hay nuevos registros para insertar.")

def cargar_team_details():    
    print("-----------------------------------------------------------------------")
    # Leer datos de la tabla team_details desde SQLite
    df_team_details = pd.read_sql_query("SELECT * FROM team_details", conn_sqlite)

    # Leer los ids existentes en SQL Server
    df_team_details_sql = pd.read_sql_query(f"SELECT team_id FROM {SQL_SCHEMA}.team_details", engine_sql_server)
    


    ids_team_existentes = set(df_team_details_sql['team_id'].astype(str))

    # Eliminar filas duplicadas y completamente vacías
    df_team_details = df_team_details.drop_duplicates().dropna(how='all')

    # Filtrar solo los registros cuyo id no existe ya en SQL Server
    df_team_nuevos = df_team_details[~df_team_details['team_id'].astype(str).isin(ids_team_existentes)]

    # Insertar los nuevos registros en SQL Server
    if not df_team_nuevos.empty:
        df_team_nuevos.to_sql(
            name='team_details',
            con=engine_sql_server,
            schema=SQL_SCHEMA,
            if_exists='append',
            index=False,
        )
        print(f"📄Se insertaron {len(df_team_nuevos)} registros nuevos en la tabla team.")
    else:
        print("No hay nuevos registros para insertar en team_details.")

def cargar_common_player_info():    
    print("-----------------------------------------------------------------------")
    # Leer la tabla common_player_info desde SQLite
    df_common_player_info = pd.read_sql_query("SELECT * FROM common_player_info", conn_sqlite)
    # Ver tipos de datos de la tabla common_player_info en SQL Server
    df_common_player_info_sql = pd.read_sql_query(
        f"SELECT * FROM {SQL_SCHEMA}.common_player_info", engine_sql_server
    )
        
    # Leer los ids existentes en SQL Server
    df_team_details_sql = pd.read_sql_query(f"SELECT team_id FROM {SQL_SCHEMA}.team_details", engine_sql_server)
    
    ids_team_existentes = set(df_team_details_sql['team_id'].astype(str))
    # Eliminar filas duplicadas y completamente vacías
    df_common_player_info = df_common_player_info.drop_duplicates().dropna(how='all')

    # Convertir la columna 'height' de formato '6-10' a entero (pulgadas)
    def height_to_inches(h):
        if isinstance(h, str) and '-' in h:
            try:
                feet, inches = h.split('-')
                return int(feet) * 12 + int(inches)
            except Exception:
                return None
        try:
            return int(h)
        except Exception:
            return None

    df_common_player_info['height'] = df_common_player_info['height'].apply(height_to_inches)

    # Convertir columnas de flags 'N'/'Y' a booleanos ANTES de filtrar
    flag_columns = ['dleague_flag', 'nba_flag', 'games_played_flag', 'greatest_75_flag']
    for col in flag_columns:
        if col in df_common_player_info.columns:
            df_common_player_info[col] = df_common_player_info[col].map({'Y': True, 'N': False})

    # Convertir 'games_played_current_season_flag' a booleano
    if 'games_played_current_season_flag' in df_common_player_info.columns:
        df_common_player_info['games_played_current_season_flag'] = df_common_player_info['games_played_current_season_flag'].map({'Y': True, 'N': False})

    # Filtrar solo los registros cuyo person_id no existe ya en SQL Server
    ids_common_existentes = set(df_common_player_info_sql['person_id'].astype(str))
    df_common_nuevos = df_common_player_info[~df_common_player_info['person_id'].astype(str).isin(ids_common_existentes)]

    # Filtrar solo los registros cuyo team_id existe en la tabla team (para respetar la FK)
    df_common_nuevos = df_common_nuevos[df_common_nuevos['team_id'].astype(str).isin(ids_team_existentes)]

    # Limpiar columnas de draft para evitar errores de conversión
    for col in ['draft_year', 'draft_round', 'draft_number']:
        if col in df_common_nuevos.columns:
            df_common_nuevos[col] = pd.to_numeric(df_common_nuevos[col], errors='coerce')

    # Insertar los nuevos registros en SQL Server
    if not df_common_nuevos.empty:
        df_common_nuevos.to_sql(
            name='common_player_info',
            con=engine_sql_server,
            schema=SQL_SCHEMA,
            if_exists='append',
            index=False,
        )
        print(f"📄Se insertaron {len(df_common_nuevos)} registros nuevos en la tabla common_player_info.")
    else:
        print("No hay nuevos registros para insertar en common_player_info.")

def cargar_game():
    print("-----------------------------------------------------------------------")
    # Leer datos de la tabla game desde SQLite
    df_game = pd.read_sql_query("SELECT * FROM game", conn_sqlite)

    # Eliminar filas duplicadas y completamente vacías
    df_game = df_game.drop_duplicates().dropna(how='all')

    # Convertir wl_home y wl_away a booleano (True para 'W', False para 'L', None para otros)
    for col in ['wl_home', 'wl_away']:
        if col in df_game.columns:
            df_game[col] = df_game[col].map({'W': True, 'L': False})

    # Leer los ids existentes en SQL Server (si la tabla existe)
    try:
        df_game_sql = pd.read_sql_query(f"SELECT game_id FROM {SQL_SCHEMA}.game", engine_sql_server)
        ids_game_existentes = set(df_game_sql['game_id'].astype(str))
    except Exception as e:
        print("No se pudo leer la tabla game en SQL Server (puede que no exista aún). Se insertarán todos los registros.")
        ids_game_existentes = set()

    # Filtrar solo los registros cuyo game_id no existe ya en SQL Server
    df_game_nuevos = df_game[~df_game['game_id'].astype(str).isin(ids_game_existentes)]

    # Extraer el año de la columna game_date (asumiendo formato 'YYYY-MM-DD')
    df_game_nuevos['season_year'] = df_game_nuevos['game_date'].astype(str).str[:4].astype(int)

    # Obtener los 5 años más recientes
    ultimos_5_anios = sorted(df_game_nuevos['season_year'].unique())[-5:]

    # Filtrar solo los registros cuyo año pertenece a las últimas 5 temporadas
    df_game_nuevos = df_game_nuevos[df_game_nuevos['season_year'].isin(ultimos_5_anios)]

    # Eliminar la columna auxiliar si no la necesitas más
    df_game_nuevos = df_game_nuevos.drop(columns=['season_year'])

    # Leer los ids existentes en SQL Server
    df_team_details_sql = pd.read_sql_query(f"SELECT team_id FROM {SQL_SCHEMA}.team_details", engine_sql_server)
    
    ids_team_existentes = set(df_team_details_sql['team_id'].astype(str))
    # Filtrar solo los registros donde ambos team_id existen en la tabla team
    df_game_nuevos = df_game_nuevos[
        df_game_nuevos['team_id_home'].astype(str).isin(ids_team_existentes) &
        df_game_nuevos['team_id_away'].astype(str).isin(ids_team_existentes)
    ]

    # Insertar los nuevos registros en SQL Server
    if not df_game_nuevos.empty:
        df_game_nuevos.to_sql(
            name='game',
            con=engine_sql_server,
            schema=SQL_SCHEMA,
            if_exists='append',
            index=False,
        )
        print(f"📄Se insertaron {len(df_game_nuevos)} registros nuevos en la tabla game.")
    else:
        print("No hay nuevos registros para insertar en game.")

def cargar_draft_history():
    print("-----------------------------------------------------------------------")
    # Leer datos de la tabla draft_history desde SQLite
    from pandas import read_sql_query


    df_draft_history = pd.read_sql_query("SELECT * FROM draft_history", conn_sqlite)


    # Leer los ids existentes en SQL Server (si la tabla existe)
    try:
        df_draft_history_sql = pd.read_sql_query(f"SELECT person_id, season FROM {SQL_SCHEMA}.draft_history", engine_sql_server)
        # Crear un set de tuplas (person_id, season) existentes
        ids_draft_existentes = set(
            zip(
                df_draft_history_sql['person_id'].astype(str),
                df_draft_history_sql['season'].astype(str)
            )
        )
    except Exception as e:
        print("No se pudo leer la tabla draft_history en SQL Server (puede que no exista aún). Se insertarán todos los registros.")
        ids_draft_existentes = set()

    # Eliminar filas duplicadas y completamente vacías
    df_draft_history = df_draft_history.drop_duplicates().dropna(how='all')

    #definir los id existentes de los equipos
    ids_team_existentes2 = read_sql_query(
        f"SELECT id FROM {SQL_SCHEMA}.team", engine_sql_server)
    ids_team_existentes2 = set(ids_team_existentes2['id'].astype(str))

    df_draft_nuevos = df_draft_history.copy()
    # Filtrar solo los registros cuyo team_id existe en la tabla team (para respetar la FK)
    df_draft_nuevos = df_draft_nuevos[df_draft_nuevos['team_id'].astype(str).isin(ids_team_existentes2)]

    ids_jugadores2 = read_sql_query(
        f"SELECT id FROM {SQL_SCHEMA}.player", engine_sql_server)
    # definir los id existentes de los jugadores
    ids_existentesjj = set(ids_jugadores2['id'].astype(str))

    # Filtrar solo los registros cuyo person_id existe en la tabla player (para respetar la FK)
    df_draft_nuevos = df_draft_nuevos[df_draft_nuevos['person_id'].astype(str).isin(ids_existentesjj)]

    # Filtrar solo los registros cuyo (person_id, season) NO existen ya en SQL Server
    df_draft_nuevos = df_draft_nuevos[
        ~df_draft_nuevos.apply(
            lambda row: (str(row['person_id']), str(row['season'])) in ids_draft_existentes,
            axis=1
        )
    ]

    # Insertar los nuevos registros en SQL Server
    if not df_draft_nuevos.empty:
        df_draft_nuevos.to_sql(
            name='draft_history',
            con=engine_sql_server,
            schema=SQL_SCHEMA,
            if_exists='append',
            index=False,
        )
        print(f"📄Se insertaron {len(df_draft_nuevos)} registros nuevos en la tabla draft_history.")
    else:
        print("No hay nuevos registros para insertar en draft_history.")

def cargar_draft_combine_stats():
    print("-----------------------------------------------------------------------")
    # Leer datos de la tabla draft_combine_stats desde SQLite
    df_draft_combine_stats = pd.read_sql_query("SELECT * FROM draft_combine_stats", conn_sqlite)

    # Eliminar filas duplicadas y completamente vacías
    df_draft_combine_stats = df_draft_combine_stats.drop_duplicates().dropna(how='all')
    # Leer la tabla player desde SQL Server
    df_player_sql = pd.read_sql_query(f"SELECT * FROM {SQL_SCHEMA}.player", engine_sql_server)
    # Insertar solo los registros cuyo id no existe ya en SQL Server
    ids_existentesjj = set(df_player_sql['id'].astype(str))

    # Filtrar solo los registros cuyo player_id existe en la tabla player (para respetar la FK)
    player_id_col = 'player_id'
    if player_id_col is not None:
        df_draft_combine_stats = df_draft_combine_stats[df_draft_combine_stats[player_id_col].astype(str).isin(ids_existentesjj)]

    # --- Conversión de columnas numéricas ---
    # Ajusta esta lista según las columnas numéricas de tu tabla en SQL Server
    numeric_columns = [
        'height_wo_shoes', 'height_w_shoes', 'weight', 'wingspan', 'standing_reach',
        'body_fat_pct', 'hand_length', 'hand_width', 'lane_agility', 'shuttle_run',
        'three_quarter_sprint', 'bench_press', 'vertical_leap_no_step', 'vertical_leap_max'
    ]
    for col in numeric_columns:
        if col in df_draft_combine_stats.columns:
            df_draft_combine_stats[col] = pd.to_numeric(df_draft_combine_stats[col], errors='coerce')

    # Leer los ids existentes en SQL Server (si la tabla existe)
    try:
        df_draft_combine_stats_sql = pd.read_sql_query(
            f"SELECT player_id, season FROM {SQL_SCHEMA}.draft_combine_stats", engine_sql_server
        )
        ids_combine_existentes = set(
            zip(
                df_draft_combine_stats_sql['player_id'].astype(str),
                df_draft_combine_stats_sql['season'].astype(str)
            )
        )
    except Exception as e:
        print("No se pudo leer la tabla draft_combine_stats en SQL Server (puede que no exista aún). Se insertarán todos los registros.")
        ids_combine_existentes = set()

    # Filtrar solo los registros cuyo (player_id, season) NO existen ya en SQL Server
    if 'player_id' in df_draft_combine_stats.columns and 'season' in df_draft_combine_stats.columns:
        df_draft_combine_nuevos = df_draft_combine_stats[
            ~df_draft_combine_stats.apply(
                lambda row: (str(row['player_id']), str(row['season'])) in ids_combine_existentes,
                axis=1
            )       
        ]
    else:
        df_draft_combine_nuevos = df_draft_combine_stats

    # Insertar los nuevos registros en SQL Server
    if not df_draft_combine_nuevos.empty:
        df_draft_combine_nuevos.to_sql(
            name='draft_combine_stats',
            con=engine_sql_server,
            schema=SQL_SCHEMA,
            if_exists='append',
            index=False,
        )
        print(f"📄Se insertaron {len(df_draft_combine_nuevos)} registros nuevos en la tabla draft_combine_stats.")
    else:
        print("No hay nuevos registros para insertar en draft_combine_stats.")

def cargar_other_stats():
    print("-----------------------------------------------------------------------")
    # Leer datos de la tabla other_stats desde SQLite
    df_other_stats = pd.read_sql_query("SELECT * FROM other_stats", conn_sqlite)


    # Eliminar filas duplicadas y completamente vacías
    df_other_stats = df_other_stats.drop_duplicates().dropna(how='all')

    # Leer los ids existentes en SQL Server (usando columnas correctas)
    df_other_stats_sql_ids = pd.read_sql_query(
        f"SELECT game_id, team_id_home, team_id_away FROM {SQL_SCHEMA}.other_stats", engine_sql_server
    )
    ids_other_stats_existentes = set(
        zip(
            df_other_stats_sql_ids['game_id'].astype(str),
            df_other_stats_sql_ids['team_id_home'].astype(str),
            df_other_stats_sql_ids['team_id_away'].astype(str)
        )
    )

    # Filtrar solo los registros cuyo (game_id, team_id_home, team_id_away) NO existen ya en SQL Server
    if all(col in df_other_stats.columns for col in ['game_id', 'team_id_home', 'team_id_away']):
        df_other_stats_nuevos = df_other_stats[
            ~df_other_stats.apply(
                lambda row: (str(row['game_id']), str(row['team_id_home']), str(row['team_id_away'])) in ids_other_stats_existentes,
                axis=1
            )
        ]
    else:
        df_other_stats_nuevos = df_other_stats

    # Filtrar solo los registros cuyo game_id existe en la tabla game (para respetar la FK)
    # Leer los game_id válidos directamente desde SQL Server
    df_game_ids_sql = pd.read_sql_query(f"SELECT game_id FROM {SQL_SCHEMA}.game", engine_sql_server)
    valid_game_ids = set(df_game_ids_sql['game_id'].astype(str))
    df_other_stats_nuevos = df_other_stats_nuevos[df_other_stats_nuevos['game_id'].astype(str).isin(valid_game_ids)]

    # Insertar los nuevos registros en SQL Server
    if not df_other_stats_nuevos.empty:
        df_other_stats_nuevos.to_sql(
            name='other_stats',
            con=engine_sql_server,
            schema=SQL_SCHEMA,
            if_exists='append',
            index=False,
        )
        print(f"📄Se insertaron {len(df_other_stats_nuevos)} registros nuevos en la tabla other_stats.")
    else:
        print("No hay nuevos registros para insertar en other_stats.")

def database_is_empty():
    # si la tabla team de la basae de datos sql server está vacia return true
    query = f"SELECT COUNT(*) as row_count FROM team"
    df_count = pd.read_sql(query, engine_sql_server)

    if not df_count.empty:
        count = df_count['row_count'].iloc[0]  # Obtiene el valor del conteo

        if count == 0:
            print(f"La base de datos SQL Server está vacía. Se requiere actualización.")
            return True 
    else:
        return False

if __name__ == "__main__":
    print(AnsiColors.MAGENTA + "********************************************************************" + AnsiColors.RESET)
    imprimir_letra_por_letra( "👋🤖🏀Bienvenido al programa de actualización automática HoopVision", AnsiColors.MAGENTA, delay=0.005)
    print(AnsiColors.MAGENTA + "********************************************************************" + AnsiColors.RESET)
    print()
    time.sleep(.4)
    imprimir_letra_por_letra( "Conexion a SQLite y SQL Server creada exitosamente.", AnsiColors.GREEN, delay=0.025)
   
    actualizar = verificar_actualizacion()
    if actualizar:
        #if not database_is_empty():
            #descargar_dataset()           
        descargar_dataset()
        cargar_team()
        cargar_player()
        cargar_team_details()
        cargar_common_player_info() 
        cargar_game()
        cargar_draft_history()
        cargar_draft_combine_stats()
        cargar_other_stats()
        print()
        imprimir_letra_por_letra( "✅💾⚙️Carga de datos nuevos a SQL Server FINALIZADA.", AnsiColors.GREEN, delay=0.02)     
    else:
        print("No es necesario descargar el dataset, ya está actualizado.")