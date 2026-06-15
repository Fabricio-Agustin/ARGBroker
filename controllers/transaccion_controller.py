import random
from models.transaccion_model import obtener_saldo_usuario, actualizar_saldo_usuario, registrar_transaccion_db

PRECIOS_ACCIONES = {
    "AAPL": 175.0,
    "TSLA": 180.0,
    "MSFT": 420.0,
    "GGAL": 35.0
}

def obtener_precios_actualizados():
    precios_simulados = {}
    for activo, precio_base in PRECIOS_ACCIONES.items():
        factor_mercado = random.uniform(-0.05, 0.07)
        nuevo_precio = precio_base * (1 + factor_market)
        precios_simulados[activo] = round(nuevo_precio, 2)
    return precios_simulados

def comprar_activo_logica(id_usuario, activo, cantidad):
    """Procesa la orden de compra validando si le alcanza el dinero."""
    precios = obtener_precios_actualizados()
    
    if activo not in precios:
        return " El activo ingresado no cotiza en ARGBroker."
        
    precio_actual = precios[activo]
    total_operacion = cantidad * precio_actual
    saldo_actual = obtener_saldo_usuario(id_usuario)
    
    if saldo_actual < total_operacion:
        return f" Saldo insuficiente. Necesitás ${total_operacion:.2f} y disponés de ${saldo_actual:.2f}."
        
    # Restamos el dinero de la cuenta
    nuevo_saldo = saldo_actual - total_operacion
    
    if actualizar_saldo_usuario(id_usuario, nuevo_saldo):
        registrar_transaccion_db(id_usuario, "COMPRA", activo, cantidad, precio_actual, total_operacion)
        return f" Compraste {cantidad} acciones de {activo} a ${precio_actual} c/u.\n💰 Tu nuevo saldo es: ${nuevo_saldo:.2f}."
    else:
        return " Error interno del Broker al procesar el pago."

def vender_activo_logica(id_usuario, activo, cantidad):
    """Procesa la orden de venta (aquí es donde el usuario ve si ganó o perdió)."""
    precios = obtener_precios_actualizados()
    
    if activo not in precios:
        return " El activo ingresado no cotiza en ARGBroker."
        
    precio_actual = precios[activo]
    total_operacion = cantidad * precio_actual
    saldo_actual = obtener_saldo_usuario(id_usuario)
    
    # Sumamos las ganancias al saldo actual
    nuevo_saldo = saldo_actual + total_operacion
    
    if actualizar_saldo_usuario(id_usuario, nuevo_saldo):
        registrar_transaccion_db(id_usuario, "VENTA", activo, cantidad, precio_actual, total_operacion)
        return f" Vendiste {cantidad} acciones de {activo} a ${precio_actual} c/u.\n💰 Recibiste: ${total_operacion:.2f}. Saldo total: ${nuevo_saldo:.2f}."
    else:
        return " Error interno del Broker al acreditar la venta."