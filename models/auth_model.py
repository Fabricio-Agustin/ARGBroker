"""
Este módulo actúa como el puente exclusivo entre la lógica de autenticación del sistema 
y la base de datos, garantizando que las operaciones de lectura y escritura de usuarios 
se realicen de forma segura y consistente.
"""

class AuthRepository:

    def __init__(self, db_manager):
        self.db = db_manager

    def buscar_usuario(self, id_usuario):
        try:
            with self.db.cursor(dictionary=True) as (cur, _):
                query = "SELECT id, nombre, password FROM usuarios WHERE id = %s"
                cur.execute(query, (id_usuario,))
                return cur.fetchone()
        except Exception as e:
            print(f"[Error en AuthRepository.buscar_usuario]: {e}")
            return None

    def registrar_usuario(self, id_usuario, nombre, email, password):
      
        if self.buscar_usuario(id_usuario):
            print(f"[Aviso]: El usuario con ID {id_usuario} ya existe.")
            return False

        try:
            with self.db.cursor(dictionary=False) as (cur, conn):
                query = """INSERT INTO usuarios (id, nombre, email, password, saldo) 
                           VALUES (%s, %s, %s, %s, 10000.00)"""
                cur.execute(query, (id_usuario, nombre, email, password))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"[Error crítico en AuthRepository.registrar_usuario]: {e}")
            return False