import random
from datetime import timedelta
from faker import Faker
import oracledb

fake = Faker("es_ES")

conn = oracledb.connect(
    user="system",
    password="Oracle123",
    dsn="localhost:15210/XEPDB1"
)
cursor = conn.cursor()

cursor.execute("DELETE FROM rrhh_oracle.historial_salarial")
cursor.execute("DELETE FROM rrhh_oracle.contratos_laborales")
cursor.execute("DELETE FROM rrhh_oracle.empleados")

empleados = []
contratos = []
historial = []

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
        random.choice(["Indefinido", "Temporal", "Servicios profesionales"]),
        fecha_ingreso,
        None,
        salario_base,
        "VIGENTE"
    ))

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
        random.choice(["Ajuste anual", "Promoción", "Revisión salarial"])
    ))

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

conn.commit()
cursor.close()
conn.close()

print("Oracle cargado: 4000 empleados, 4000 contratos y 50000 movimientos salariales.")