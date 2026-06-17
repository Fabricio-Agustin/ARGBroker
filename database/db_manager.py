"""
Este script utiliza el patrón de diseño Context Manager de Python para automatizar 
el ciclo de vida de las 
conexiones a la base de datos, eliminando la necesidad de abrir y cerrar conexiones manualmente 
en cada método de tus repositorios.

Patrón @contextmanager
Propósito: Actúa como un "guardián" de la conexión. Al usarlo con la sentencia with, 
aseguramos que cada recurso abierto (cursor y conexión) se cierre de forma garantizada, 
incluso si ocurre un error dentro de la consulta.
"""

from database.database import create_connection
from contextlib import contextmanager

class DatabaseManager:
    @contextmanager
    def cursor(self, dictionary=True):
        conn = create_connection()
        if not conn: raise Exception("Error: No se pudo establecer conexión.")
        cur = conn.cursor(dictionary=dictionary)
        try:
            yield cur, conn
        finally:
            cur.close()
            conn.close()