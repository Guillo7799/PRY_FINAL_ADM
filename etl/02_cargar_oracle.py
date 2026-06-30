import random
from datetime import timedelta
from faker import Faker
import oracledb

# Inicializa Faker para generar información ficticia en español
fake = Faker("es_ES")

# Establece la conexión con Oracle Database
conn = oracledb.connect(
    user="system",
    password="Oracle123",
    dsn="localhost:15210/XEPDB1"
)

# Crea el cursor que permitirá ejecutar las consultas SQL
cursor = conn.cursor()

# Se eliminan los registros existentes para evitar duplicados
# cuando el script se ejecute nuevamente.
cursor.execute("DELETE FROM rrhh_oracle.historial_salarial")
cursor.execute("DELETE FROM rrhh_oracle.contratos_laborales")
cursor.execute("DELETE FROM rrhh_oracle.empleados")

# Se crean listas temporales para almacenar los datos antes de
# insertarlos en la base de datos mediante una carga masiva.
empleados = []
contratos = []
historial = []

# ----------------------------------------------------
# Generación de empleados y contratos laborales

# Se crean 4.000 empleados con información ficticia.
# A cada empleado se le asigna un contrato laboral y un salario base.
for i in range(1, 4001):

    fecha_ingreso = fake.date_between(start_date="-10y", end_date="today")

    empleados.append((
        i,
        fake.unique.numerify("##########"),
        fake.first_name(),
        fake.last_name(),
        fake.email(),
        fecha_ingreso,
        "ACTIVO"
    ))

    salario_base = random.randint(500, 2500)

    contratos.append((
        i,
        i,
        random.choice([
            "Indefinido",
            "Temporal",
            "Servicios profesionales"
        ]),
        fecha_ingreso,
        None,
        salario_base,
        "VIGENTE"
    ))

# ----------------------------------------------------
# Generación del historial salarial

# Se generan 50.000 movimientos salariales distribuidos entre
# los empleados registrados. Cada movimiento almacena el salario
# anterior, el nuevo salario y el motivo del cambio.
for i in range(1, 50001):

    empleado_id = random.randint(1, 4000)

    anterior = random.randint(500, 2000)
    nuevo = anterior + random.randint(25, 300)

    historial.append((
        i,
        empleado_id,
        fake.date_between(start_date="-5y", end_date="today"),
        anterior,
        nuevo,
        random.choice([
            "Ajuste anual",
            "Promoción",
            "Revisión salarial"
        ])
    ))

# ----------------------------------------------------
# Inserción de la información en Oracle

# Se utiliza executemany() para realizar una carga masiva,
# mejorando el rendimiento frente a insertar un registro a la vez.

cursor.executemany("""
    INSERT INTO rrhh_oracle.empleados
    VALUES (:1, :2, :3, :4, :5, :6, :7)
""", empleados)

cursor.executemany("""
    INSERT INTO rrhh_oracle.contratos_laborales
    VALUES (:1, :2, :3, :4, :5, :6, :7)
""", contratos)

cursor.executemany("""
    INSERT INTO rrhh_oracle.historial_salarial
    VALUES (:1, :2, :3, :4, :5, :6)
""", historial)

# Guarda todos los cambios realizados en la base de datos
conn.commit()

# Libera los recursos utilizados durante la conexión
cursor.close()
conn.close()

print("Oracle cargado: 4000 empleados, 4000 contratos y 50000 movimientos salariales.")