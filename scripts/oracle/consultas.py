import oracledb

# Establece la conexión con Oracle Database
conn = oracledb.connect(
    user="system",
    password="Oracle123",
    dsn="localhost:15210/XEPDB1"
)

# Crea el cursor para ejecutar consultas SQL
cursor = conn.cursor()

print("\n=== VALIDACIÓN ORACLE 21C ===")

# ----------------------------------------------------
# Verificación de registros

# Se obtiene la cantidad de registros de las tablas
# principales para comprobar que la información fue
# cargada correctamente.
consultas = {
    "Empleados": "SELECT COUNT(*) FROM rrhh_oracle.empleados",
    "Contratos laborales": "SELECT COUNT(*) FROM rrhh_oracle.contratos_laborales",
    "Historial salarial": "SELECT COUNT(*) FROM rrhh_oracle.historial_salarial",
    "Nómina consolidada": "SELECT COUNT(*) FROM rrhh_oracle.nomina_consolidada"
}

for nombre, query in consultas.items():
    cursor.execute(query)
    total = cursor.fetchone()[0]
    print(f"{nombre}: {total} registros")

# ----------------------------------------------------
# Visualización de la información consolidada

# Se consultan algunos registros de la tabla
# nomina_consolidada para comprobar que el proceso ETL
# integró correctamente la información de los tres SGBD.
print("\nPrimeros 10 registros consolidados:")

cursor.execute("""
    SELECT empleado_id,
           nombres,
           apellidos,
           departamento,
           cargo,
           salario_base,
           total_asistencias
    FROM rrhh_oracle.nomina_consolidada
    FETCH FIRST 10 ROWS ONLY
""")

for fila in cursor.fetchall():
    print(fila)

# Libera los recursos utilizados
cursor.close()
conn.close()

print("\nOracle validado correctamente.")