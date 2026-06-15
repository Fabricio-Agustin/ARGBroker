from decimal import Decimal
from database.database import create_connection

def obtener_saldo_usuario(id_usuario):
    conexion = create_connection()
    if not conexion: return 0.0
    cursor = conexion.cursor()
    query = "SELECT saldo FROM usuarios WHERE id = %s"
    try:
        cursor.execute(query, (id_usuario,))
        resultado = cursor.fetchone()
        return float(resultado[0]) if resultado else 0.0
    finally:
        cursor.close()
        conexion.close()

def actualizar_saldo_usuario(id_usuario, nuevo_saldo):
    conexion = create_connection()
    if not conexion: return False
    cursor = conexion.cursor()
    query = "UPDATE usuarios SET saldo = %s WHERE id = %s"
    try:
        cursor.execute(query, (nuevo_saldo, id_usuario))
        conexion.commit()
        return True
    except Exception:
        return False
    finally:
        cursor.close()
        conexion.close()

def registrar_transaccion_db(id_usuario, tipo, activo, cantidad, precio, total):
    conexion = create_connection()
    if not conexion: return False
    cursor = conexion.cursor()
    query = "INSERT INTO transacciones (id_usuario, tipo, activo, cantidad, precio, total) VALUES (%s, %s, %s, %s, %s, %s)"
    try:
        cursor.execute(query, (id_usuario, tipo, activo, cantidad, precio, total))
        conexion.commit()
        return True
    except Exception:
        return False
    finally:
        cursor.close()
        conexion.close()

def obtener_portafolio_usuario(id_usuario):
    conexion = create_connection()
    if not conexion: return []
    cursor = conexion.cursor(dictionary=True)
    query = "SELECT activo, cantidad, precio_compra_promedio FROM portafolios WHERE id_usuario = %s AND cantidad > 0"
    try:
        cursor.execute(query, (id_usuario,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()

def actualizar_posicion_portafolio(id_usuario, activo, cantidad_operada, precio_operado, es_compra):
    conexion = create_connection()
    if not conexion: return False
    cursor = conexion.cursor(dictionary=True)
    
    try:
        query_buscar = "SELECT cantidad, precio_compra_promedio FROM portafolios WHERE id_usuario = %s AND activo = %s"
        cursor.execute(query_buscar, (id_usuario, activo))
        posicion = cursor.fetchone()
        
        cant_op_dec = Decimal(str(cantidad_operada))
        prec_op_dec = Decimal(str(precio_operado))
        
        if es_compra:
            if posicion:
                cant_act_dec = Decimal(str(posicion['cantidad']))
                prec_act_dec = Decimal(str(posicion['precio_compra_promedio']))
                
                nueva_cant = cant_act_dec + cant_op_dec
                nuevo_ppc = ((cant_act_dec * prec_act_dec) + (cant_op_dec * prec_op_dec)) / nueva_cant
                
                query_update = "UPDATE portafolios SET cantidad = %s, precio_compra_promedio = %s WHERE id_usuario = %s AND activo = %s"
                cursor.execute(query_update, (float(nueva_cant), float(nuevo_ppc), id_usuario, activo))
            else:
                query_insert = "INSERT INTO portafolios (id_usuario, activo, cantidad, precio_compra_promedio) VALUES (%s, %s, %s, %s)"
                cursor.execute(query_insert, (id_usuario, activo, float(cant_op_dec), float(prec_op_dec)))
        else:
            if not posicion or Decimal(str(posicion['cantidad'])) < cant_op_dec:
                return False 
                
            cant_act_dec = Decimal(str(posicion['cantidad']))
            nueva_cant = cant_act_dec - cant_op_dec
            
            if nueva_cant == 0:
                query_delete = "DELETE FROM portafolios WHERE id_usuario = %s AND activo = %s"
                cursor.execute(query_delete, (id_usuario, activo))
            else:
                query_update = "UPDATE portafolios SET cantidad = %s WHERE id_usuario = %s AND activo = %s"
                cursor.execute(query_update, (float(nueva_cant), id_usuario, activo))
                
        conexion.commit()
        return True
    except Exception as e:
        print(f"[Error Portafolio]: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()