import random
from datetime import datetime, timedelta
import pyodbc
from faker import Faker

# Inicializa Faker para generar información ficticia en español
fake = Faker("es_ES")

# Establece la conexión con SQL Server
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,14330;"
    "DATABASE=rrhh_asistencia;"
    "UID=sa;"
    "PWD=SqlServer123!;"
    "TrustServerCertificate=yes;"
)

# Crea el cursor que permitirá ejecutar consultas SQL
cursor = conn.cursor()

# Se eliminan los registros existentes para evitar duplicados
# cuando el script se vuelva a ejecutar.
cursor.execute("DELETE FROM asistencias")
cursor.execute("DELETE FROM control_horario")
cursor.execute("DELETE FROM horarios")
conn.commit()

# ----------------------------------------------------
# Registro de horarios laborales

# Se crean cuatro horarios que posteriormente serán
# asignados a los diferentes colaboradores.
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

# ----------------------------------------------------
# Asignación de horarios a los empleados

# Se generan 4.000 registros donde cada empleado queda
# asociado a un horario de trabajo de forma aleatoria.
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

# ----------------------------------------------------
# Generación de registros de asistencia

# Se generan 40.000 asistencias distribuidas entre los
# empleados. Para cada registro se asigna una fecha,
# una hora de entrada, una hora de salida y un estado
# de asistencia de forma aleatoria.
asistencias = []

# Se toma como referencia una fecha inicial de hace 120 días
fecha_base = datetime.now().date() - timedelta(days=120)

for i in range(1, 40001):

    empleado_id = random.randint(1, 4000)

    fecha = fecha_base + timedelta(days=random.randint(0, 120))

    hora_entrada = random.choice([
        "07:55:00",
        "08:00:00",
        "08:10:00",
        "08:25:00"
    ])

    hora_salida = random.choice([
        "16:55:00",
        "17:00:00",
        "17:15:00",
        "17:30:00"
    ])

    estado = random.choice([
        "PRESENTE",
        "ATRASO",
        "AUSENTE",
        "PERMISO"
    ])

    asistencias.append((
        i,
        empleado_id,
        fecha,
        hora_entrada,
        hora_salida,
        estado
    ))

# Se realiza la inserción masiva de todas las asistencias
# para optimizar el tiempo de carga.
cursor.executemany(
    "INSERT INTO asistencias VALUES (?, ?, ?, ?, ?, ?)",
    asistencias
)

# Guarda todos los cambios realizados en la base de datos
conn.commit()

# Libera los recursos utilizados durante la conexión
cursor.close()
conn.close()

print("SQL Server cargado: 4 horarios, 4000 controles y 40000 asistencias.")