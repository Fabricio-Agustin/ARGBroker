"""
Este módulo gestiona el flujo completo de una orden de compra o venta, 
asegurando que el usuario cumpla con los requisitos financieros antes de confirmar cualquier movimiento 
en la base de datos

Utiliza operaciones a nivel de bits para determinar el tipo de operación, 
lo que permite un control de flujo rápido y eficiente:

OP_COMPRA (0b01): Identifica una orden de compra.
OP_VENTA (0b00): Identifica una orden de venta.
MASCARA_DIRECCION: Máscara para extraer el bit de dirección (compra/venta).
MASCARA_VALIDACION: Máscara para verificar que no se envíen flags inválidos al sistema.

"""

from models.transaccion_model import (
    obtener_saldo_usuario, 
    actualizar_saldo_usuario, 
    registrar_transaccion_db,
    obtener_portafolio_usuario,
    actualizar_posicion_portafolio
)

OP_VENTA = 0b00
OP_COMPRA = 0b01
MASCARA_DIRECCION = 0b01   
MASCARA_VALIDACION = 0b01  

def procesar_orden(id_usuario, activo, cantidad, precio_mercado, flag_operacion: int):

    if (flag_operacion & ~MASCARA_VALIDACION) != 0:
        return "Error: Flag de operación inválido."

    activo = activo.strip().upper()
    es_compra = bool(flag_operacion & MASCARA_DIRECCION)
    total_operacion = cantidad * precio_mercado
    
    saldo_actual = obtener_saldo_usuario(id_usuario)

    if es_compra:
        if saldo_actual < total_operacion:
            return f"Saldo insuficiente. Requerido: ${total_operacion:.2f}, Disponible: ${saldo_actual:.2f}."
        
        nuevo_saldo = saldo_actual - total_operacion
        tipo = "COMPRA"
    
    else:
        portafolio = obtener_portafolio_usuario(id_usuario)
        posicion = next((p for p in portafolio if p['activo'] == activo), None)
        
        if not posicion or float(posicion['cantidad']) < cantidad:
            return f"Error: No posees suficientes activos de {activo} para liquidar."
            
        nuevo_saldo = saldo_actual + total_operacion
        tipo = "VENTA"

    if actualizar_saldo_usuario(id_usuario, nuevo_saldo):
        if actualizar_posicion_portafolio(id_usuario, activo, cantidad, precio_mercado, es_compra):
            registrar_transaccion_db(id_usuario, tipo, activo, cantidad, precio_mercado, total_operacion)
            return f"Operación exitosa: {tipo} de {cantidad} {activo} a ${precio_mercado:.2f}."
        else:
            actualizar_saldo_usuario(id_usuario, saldo_actual)
            return "Error: No se pudo actualizar el portafolio."
    
    return "Error interno del sistema al procesar la transacción."