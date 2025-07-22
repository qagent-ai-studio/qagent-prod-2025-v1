from sqlalchemy import create_engine, text

# Configura tus valores aquí directamente (o usa config.get si lo tienes en un archivo)
SERVER = "10.22.28.2"
DATABASE = "qagent"
USERNAME = "tu_usuario"
PASSWORD = "tu_password"
DRIVER = "ODBC Driver 18 for SQL Server"

# Construir la URL de conexión
url = (
    f"mssql+pyodbc://{USERNAME}:{PASSWORD}"
    f"@{SERVER}:1433/{DATABASE}"
    f"?driver={DRIVER.replace(' ', '+')}"
    f"&TrustServerCertificate=yes"
    f"&encrypt=yes"
)

try:
    engine = create_engine(url)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT GETDATE()"))
        print("Conexión exitosa. Fecha actual en el servidor SQL:")
        for row in result:
            print(row[0])
except Exception as e:
    print("Error al conectar:", e)
