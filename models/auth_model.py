from database.database import create_connection

def buscar_usuario_por_id(id_usuario):
    conexion = create_connection()
    if not conexion: return None
    cursor = conexion.cursor(dictionary=True)
    query = "SELECT id, nombre, password FROM usuarios WHERE id = %s"
    try:
        cursor.execute(query, (id_usuario,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()

def registrar_usuario_db(id_usuario, nombre, email, password):
    conexion = create_connection()
    if not conexion: return False
    cursor = conexion.cursor()
    query = "INSERT INTO usuarios (id, nombre, email, password, saldo) VALUES (%s, %s, %s, %s, 10000.00)"
    try:
        cursor.execute(query, (id_usuario, nombre, email, password))
        conexion.commit()
        return True
    except Exception as e:
        print(f"[Error BD Registro]: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()