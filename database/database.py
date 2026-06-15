import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            database='name_database',
            user='root',
            password='password'
        )
    
    except Error as e:
        print("\nla base de datos sql no se conecto de manera correcta.")
        print(" Verifica el nombre de la base de datos, la contraseña y que el servicio esté activo.")
        return None

if __name__ == "__main__":
    connection = create_connection()
    
    if connection:
        print("conectado a la base de datos sql de manera correcta")