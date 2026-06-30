import pymysql

# Establece la conexión con la base de datos MariaDB
conn = pymysql.connect(
    host="localhost",
    port=33071,
    user="dba_mariadb",
    password="MariaDB123",
    database="rrhh_catalogos"
)

# Crea el cursor para ejecutar consultas SQL
cursor = conn.cursor()

print("\n=== VALIDACIÓN MARIADB ===")

# ----------------------------------------------------
# Verificación de la cantidad de registros

# Se consulta el número de registros existentes en cada
# una de las tablas principales para comprobar que la
# carga de datos se realizó correctamente.
consultas = {
    "Departamentos": "SELECT COUNT(*) FROM departamentos",
    "Cargos": "SELECT COUNT(*) FROM cargos",
    "Sedes": "SELECT COUNT(*) FROM sedes"
}

for nombre, query in consultas.items():
    cursor.execute(query)
    total = cursor.fetchone()[0]
    print(f"{nombre}: {total} registros")

# ----------------------------------------------------
# Visualización de información

# Se muestran los primeros cargos junto con el
# departamento al que pertenecen para validar la
# relación entre ambas tablas.
print("\nPrimeros 10 cargos con departamento:")

cursor.execute("""
    SELECT c.cargo_id,
           c.nombre,
           c.nivel,
           d.nombre
    FROM cargos c
    JOIN departamentos d
      ON c.departamento_id = d.departamento_id
    LIMIT 10
""")

for fila in cursor.fetchall():
    print(fila)

# Libera los recursos utilizados
cursor.close()
conn.close()

print("\nMariaDB validado correctamente.")