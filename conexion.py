
import pyodbc


def conectar_bd():
    conexion = pyodbc.connect(
        "SERVER=HP-Mateo;"
        "DATABASE=MiEquipo;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
        "DRIVER={ODBC Driver 17 for SQL Server};"
    )

    return conexion
