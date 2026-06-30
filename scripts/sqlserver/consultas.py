import pyodbc

# Establece la conexión con SQL Server
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,14330;"
    "DATABASE=rrhh_asistencia;"
    "UID=sa;"
    "PWD=SqlServer123!;"
    "TrustServerCertificate=yes;"
)

# Crea el cursor para ejecutar consultas SQL
cursor = conn.cursor()

print("\n=== VALIDACIÓN SQL SERVER ===")

# ----------------------------------------------------
# Verificación de registros

# Se consulta la cantidad de registros existentes en
# cada una de las tablas del sistema de asistencia.
consultas = {
    "Horarios": "SELECT COUNT(*) FROM horarios",
    "Control horario": "SELECT COUNT(*) FROM control_horario",
    "Asistencias": "SELECT COUNT(*) FROM asistencias"
}

for nombre, query in consultas.items():
    cursor.execute(query)
    total = cursor.fetchone()[0]
    print(f"{nombre}: {total} registros")

# ----------------------------------------------------
# Resumen de asistencias

# Se agrupan los registros por estado para validar que
# la generación de datos produjo distintos escenarios
# de asistencia.
print("\nResumen de asistencias por estado:")

cursor.execute("""
    SELECT estado,
           COUNT(*) AS total
    FROM asistencias
    GROUP BY estado
""")

for fila in cursor.fetchall():
    print(fila)

# Libera los recursos utilizados
cursor.close()
conn.close()

print("\nSQL Server validado correctamente.")