from datetime import datetime
import random
import oracledb
import pyodbc
import pymysql

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

cur_oracle = oracle.cursor()
cur_sql = sqlserver.cursor()
cur_maria = mariadb.cursor()

cur_oracle.execute("DELETE FROM rrhh_oracle.nomina_consolidada")

cur_maria.execute("""
    SELECT c.cargo_id, c.nombre, d.nombre
    FROM cargos c
    JOIN departamentos d
      ON c.departamento_id = d.departamento_id
""")

cargos = cur_maria.fetchall()

cur_oracle.execute("""
    SELECT e.empleado_id, e.nombres, e.apellidos, e.correo,
           c.salario_base, c.estado
    FROM rrhh_oracle.empleados e
    JOIN rrhh_oracle.contratos_laborales c
      ON e.empleado_id = c.empleado_id
""")

empleados = cur_oracle.fetchall()
datos_consolidados = []

for empleado in empleados:
    empleado_id, nombres, apellidos, correo, salario_base, estado_contrato = empleado

    cargo = random.choice(cargos)
    nombre_cargo = cargo[1]
    nombre_departamento = cargo[2]

    cur_sql.execute("""
        SELECT
            COUNT(*) AS total_asistencias,
            SUM(CASE WHEN estado = 'ATRASO' THEN 1 ELSE 0 END) AS total_atrasos,
            SUM(CASE WHEN estado = 'AUSENTE' THEN 1 ELSE 0 END) AS total_ausencias
        FROM asistencias
        WHERE empleado_id = ?
    """, empleado_id)

    asistencia = cur_sql.fetchone()

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

cur_oracle.executemany("""
    INSERT INTO rrhh_oracle.nomina_consolidada (
        empleado_id, nombres, apellidos, correo, salario_base,
        total_asistencias, total_atrasos, total_ausencias,
        estado_contrato, fecha_consolidacion, departamento, cargo
    )
    VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)
""", datos_consolidados)

oracle.commit()

cur_oracle.close()
cur_sql.close()
cur_maria.close()

oracle.close()
sqlserver.close()
mariadb.close()

print(f"ETL ejecutado correctamente usando Oracle, SQL Server y MariaDB. Registros consolidados: {len(datos_consolidados)}")