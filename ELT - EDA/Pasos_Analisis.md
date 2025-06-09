# Proceso de Carga, Limpieza y Exportación de Datos NBA

## 1. Cargar base de datos
1. Cargar la base de datos original (por ejemplo, desde un archivo `.csv` o una URL).
2. Guardar en variables las TABLAS que se van a utilizar para el análisis 

## 2. Limpieza de datos
3. Filtrar los datos por fecha ( 5 temporadas ).
4. Verificar que la fecha esté correctamente filtrada (`df['fecha'].min()` y `df['fecha'].max()` o usando filtros).
5. Sumar los valores nulos para saber cuántos tiene la tabla en total (`df.isnull().sum()`).
6. Revisar qué datos tiene una columna específica (`df['columna'].unique()` o `.value_counts()`).
7. Según los datos encontrados:
   - Reemplazar valores incorrectos con `.replace()`, `.fillna()`, etc.
   - O eliminar filas con `.dropna()` si es necesario (esto elimina el registro completo).
8. Verificar si se eliminaron o reemplazaron correctamente los valores nulos.

## 3. Guardar archivo CSV de la variable
9. Guardar el archivo CSV de cada variable limpio dentro de una carpeta `CSV`
