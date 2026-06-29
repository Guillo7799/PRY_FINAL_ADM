import pymysql
from faker import Faker

fake = Faker("es_ES")

conn = pymysql.connect(
    host="localhost",
    port=33071,
    user="dba_mariadb",
    password="MariaDB123",
    database="rrhh_catalogos"
)

cursor = conn.cursor()

# Limpiar tablas
cursor.execute("DELETE FROM cargos")
cursor.execute("DELETE FROM departamentos")
cursor.execute("DELETE FROM sedes")

# Departamentos
for i in range(1, 21):
    cursor.execute(
        "INSERT INTO departamentos VALUES (%s, %s, %s)",
        (i, f"Departamento {i}", fake.text(max_nb_chars=100))
    )

# Cargos: 200
for i in range(1, 201):
    departamento_id = ((i - 1) % 20) + 1
    cursor.execute(
        "INSERT INTO cargos VALUES (%s, %s, %s, %s)",
        (i, departamento_id, f"Cargo {i}", fake.random_element(["Junior", "Semi Senior", "Senior", "Jefatura"]))
    )

# Sedes
for i in range(1, 6):
    cursor.execute(
        "INSERT INTO sedes VALUES (%s, %s, %s, %s)",
        (i, f"Sede {i}", fake.city(), fake.address())
    )

conn.commit()
cursor.close()
conn.close()

print("MariaDB cargado correctamente: departamentos, cargos y sedes.")