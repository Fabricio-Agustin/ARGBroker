"""
Este módulo centraliza la configuración y el acceso a la base de datos ARGBROKER. 
Su objetivo es abstraer los detalles técnicos de la conexión para que el resto de tu aplicación 
no tenga que preocuparse por cómo conectarse, sino solo por ejecutar sentencias SQL.

load_dotenv(): Carga las credenciales (host, usuario, contraseña) desde un archivo .env externo, 
siguiendo las mejores prácticas de seguridad para no exponer datos sensibles 
en el código fuente.

execute_query(query, params):
Utilizada para sentencias de escritura (INSERT, UPDATE, DELETE).
Gestiona el ciclo de vida completo de la conexión: abre, ejecuta, confirma los cambios (commit) 
y cierra tanto el cursor como la conexión para liberar recursos del servidor.

fetch_one(query, params):
Utilizada para sentencias de lectura (SELECT).
Devuelve los resultados como un diccionario (dictionary=True), lo cual es una excelente elección técnica, 
ya que permite acceder a los campos por su nombre (ej. usuario['saldo']) en lugar de por índices numéricos 
(ej. usuario[0]), haciendo tu código mucho más legible.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
    except Error as e:
        print(f"[Error de conexión a BD]: {e}")
        return None

def get_db_connection():
    return create_connection()

def execute_query(query, params=()):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
        finally:
            cursor.close()
            conn.close()

def fetch_one(query, params=()):
    conn = create_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
    return None