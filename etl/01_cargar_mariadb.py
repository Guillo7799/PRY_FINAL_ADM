import pymysql
from faker import Faker

# Inicializa Faker utilizando datos en español
fake = Faker("es_ES")

# Establece la conexión con la base de datos MariaDB
conn = pymysql.connect(
    host="localhost",
    port=33071,
    user="dba_mariadb",
    password="MariaDB123",
    database="rrhh_catalogos"
)

# Crea un cursor para poder ejecutar consultas SQL
cursor = conn.cursor()

# Antes de insertar nueva información, se eliminan los registros existentes
# para evitar duplicados cada vez que se ejecute el script.
cursor.execute("DELETE FROM cargos")
cursor.execute("DELETE FROM departamentos")
cursor.execute("DELETE FROM sedes")

# -----------------------------
# Carga de departamentos

# Se generan 20 departamentos con un identificador, un nombre y una
# descripción aleatoria utilizando Faker.
for i in range(1, 21):
    cursor.execute(
        "INSERT INTO departamentos VALUES (%s, %s, %s)",
        (i, f"Departamento {i}", fake.text(max_nb_chars=100))
    )

# -----------------------------
# Carga de cargos

# Se crean 200 cargos. Cada cargo se asigna automáticamente a uno de los
# departamentos existentes y además se genera un nivel organizacional.
for i in range(1, 201):
    departamento_id = ((i - 1) % 20) + 1

    cursor.execute(
        "INSERT INTO cargos VALUES (%s, %s, %s, %s)",
        (
            i,
            departamento_id,
            f"Cargo {i}",
            fake.random_element([
                "Junior",
                "Semi Senior",
                "Senior",
                "Jefatura"
            ])
        )
    )

# -----------------------------
# Carga de sedes

# Se registran cinco sedes con información ficticia de ciudad y dirección.
for i in range(1, 6):
    cursor.execute(
        "INSERT INTO sedes VALUES (%s, %s, %s, %s)",
        (
            i,
            f"Sede {i}",
            fake.city(),
            fake.address()
        )
    )

# Guarda todos los cambios realizados en la base de datos
conn.commit()

# Libera los recursos utilizados
cursor.close()
conn.close()

print("MariaDB cargado correctamente: departamentos, cargos y sedes.")