from datetime import datetime
import random
import oracledb
import pyodbc
import pymysql

# ----------------------------------------------------
# Conexión a los tres motores de base de datos

# Se establece una conexión independiente con Oracle,
# SQL Server y MariaDB para poder extraer y consolidar
# la información de cada uno de ellos.

oracle = oracledb.connect(
    user="system",
    password="Oracle123",
    dsn="localhost:15210/XEPDB1"
)

sqlserver = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,14330;"
    "DATABASE=rrhh_asistencia;"
    "UID=sa;"
    "PWD=SqlServer123!;"
    "TrustServerCertificate=yes;"
)

mariadb = pymysql.connect(
    host="localhost",
    port=33071,
    user="dba_mariadb",
    password="MariaDB123",
    database="rrhh_catalogos"
)

# Se crean los cursores para ejecutar consultas en cada SGBD.
cur_oracle = oracle.cursor()
cur_sql = sqlserver.cursor()
cur_maria = mariadb.cursor()

# Antes de generar una nueva consolidación se elimina
# la información anterior para evitar registros duplicados.
cur_oracle.execute("DELETE FROM rrhh_oracle.nomina_consolidada")

# ----------------------------------------------------
# Extracción de información desde MariaDB

# Se obtiene el catálogo de cargos y departamentos
# que posteriormente será asociado a cada empleado.
cur_maria.execute("""
    SELECT c.cargo_id, c.nombre, d.nombre
    FROM cargos c
    JOIN departamentos d
      ON c.departamento_id = d.departamento_id
""")

cargos = cur_maria.fetchall()

# ----------------------------------------------------
# Extracción de información desde Oracle

# Se recuperan los datos principales de cada empleado,
# junto con su contrato laboral y salario base.
cur_oracle.execute("""
    SELECT e.empleado_id, e.nombres, e.apellidos, e.correo,
           c.salario_base, c.estado
    FROM rrhh_oracle.empleados e
    JOIN rrhh_oracle.contratos_laborales c
      ON e.empleado_id = c.empleado_id
""")

empleados = cur_oracle.fetchall()

# Lista donde se almacenará la información consolidada
# antes de insertarla nuevamente en Oracle.
datos_consolidados = []

# ----------------------------------------------------
# Transformación de la información

# Para cada empleado se consulta la asistencia registrada
# en SQL Server y se combina con la información obtenida
# desde Oracle y MariaDB.
for empleado in empleados:

    empleado_id, nombres, apellidos, correo, salario_base, estado_contrato = empleado

    # Se asigna un cargo y departamento del catálogo generado.
    cargo = random.choice(cargos)

    nombre_cargo = cargo[1]
    nombre_departamento = cargo[2]

    # Se calculan indicadores de asistencia del empleado.
    cur_sql.execute("""
        SELECT
            COUNT(*) AS total_asistencias,
            SUM(CASE WHEN estado = 'ATRASO' THEN 1 ELSE 0 END) AS total_atrasos,
            SUM(CASE WHEN estado = 'AUSENTE' THEN 1 ELSE 0 END) AS total_ausencias
        FROM asistencias
        WHERE empleado_id = ?
    """, empleado_id)

    asistencia = cur_sql.fetchone()

    # Se construye el registro consolidado que posteriormente
    # será almacenado en Oracle.
    datos_consolidados.append((
        empleado_id,
        nombres,
        apellidos,
        correo,
        salario_base,
        asistencia[0] or 0,
        asistencia[1] or 0,
        asistencia[2] or 0,
        estado_contrato,
        datetime.now(),
        nombre_departamento,
        nombre_cargo
    ))

# ----------------------------------------------------
# Carga de la información consolidada

# Se realiza una inserción masiva en la tabla
# nomina_consolidada utilizando todos los registros
# generados durante el proceso ETL.
cur_oracle.executemany("""
    INSERT INTO rrhh_oracle.nomina_consolidada (
        empleado_id, nombres, apellidos, correo, salario_base,
        total_asistencias, total_atrasos, total_ausencias,
        estado_contrato, fecha_consolidacion, departamento, cargo
    )
    VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)
""", datos_consolidados)

# Guarda todos los cambios realizados en Oracle.
oracle.commit()

# Cierra los cursores utilizados durante el proceso.
cur_oracle.close()
cur_sql.close()
cur_maria.close()

# Finaliza las conexiones con cada uno de los motores
# de base de datos.
oracle.close()
sqlserver.close()
mariadb.close()

print(f"ETL ejecutado correctamente usando Oracle, SQL Server y MariaDB. Registros consolidados: {len(datos_consolidados)}")