import random
from datetime import datetime, timedelta
import pyodbc
from faker import Faker

fake = Faker("es_ES")

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,14330;"
    "DATABASE=rrhh_asistencia;"
    "UID=sa;"
    "PWD=SqlServer123!;"
    "TrustServerCertificate=yes;"
)

cursor = conn.cursor()

cursor.execute("DELETE FROM asistencias")
cursor.execute("DELETE FROM control_horario")
cursor.execute("DELETE FROM horarios")
conn.commit()

horarios = [
    (1, "Administrativo", "08:00:00", "17:00:00"),
    (2, "Operativo Mañana", "07:00:00", "15:00:00"),
    (3, "Operativo Tarde", "14:00:00", "22:00:00"),
    (4, "Medio Tiempo", "08:00:00", "13:00:00"),
]

cursor.executemany(
    "INSERT INTO horarios VALUES (?, ?, ?, ?)",
    horarios
)

control_horario = []
for i in range(1, 4001):
    control_horario.append((
        i,
        i,
        random.randint(1, 4),
        fake.date_between(start_date="-1y", end_date="today"),
        "ACTIVO"
    ))

cursor.executemany(
    "INSERT INTO control_horario VALUES (?, ?, ?, ?, ?)",
    control_horario
)

asistencias = []
fecha_base = datetime.now().date() - timedelta(days=120)

for i in range(1, 40001):
    empleado_id = random.randint(1, 4000)
    fecha = fecha_base + timedelta(days=random.randint(0, 120))
    hora_entrada = random.choice(["07:55:00", "08:00:00", "08:10:00", "08:25:00"])
    hora_salida = random.choice(["16:55:00", "17:00:00", "17:15:00", "17:30:00"])
    estado = random.choice(["PRESENTE", "ATRASO", "AUSENTE", "PERMISO"])

    asistencias.append((i, empleado_id, fecha, hora_entrada, hora_salida, estado))

cursor.executemany(
    "INSERT INTO asistencias VALUES (?, ?, ?, ?, ?, ?)",
    asistencias
)

conn.commit()
cursor.close()
conn.close()

print("SQL Server cargado: 4 horarios, 4000 controles y 40000 asistencias.")