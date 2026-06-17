"""
Define un estándar (Contrato): Obliga a cualquier "motor de precios" 
a tener un método para obtener valores, permitiendo cambiar la fuente de datos 
(ej. pasar de números aleatorios a una API real) sin romper el resto del sistema.

Orquestación: Es el único lugar donde se coordinan los pasos necesarios para una compra o venta: 
pide el precio, calcula el total, traduce los datos y ordena al repositorio (la base de datos) 
que guarde la transacción.

Protección (Programación Defensiva): Si algo falla durante el proceso 
(por ejemplo, si se cae la conexión a la base de datos), 
el sistema captura el error y evita que el programa completo se cierre, 
devolviendo simplemente un estado de fallo controlado.
"""

import random
from abc import ABC, abstractmethod

class IMotorPrecios(ABC):
    @abstractmethod
    def obtener_precio(self, activo: str) -> float:
        pass

class MotorPreciosSQL(IMotorPrecios):
    def obtener_precio(self, activo: str) -> float:
        return round(random.uniform(10.0, 300.0), 2)

class TransaccionDAO:
    def __init__(self, db_manager):
        self.db = db_manager

    def registrar_transaccion(self, id_usuario, tipo, activo, cantidad, precio, total):
        return self.db.registrar_transaccion_db(
            id_usuario, tipo, activo, cantidad, precio, total
        )

class BrokerMarketService:
    OP_VENTA = 0
    OP_COMPRA = 1
    
    def __init__(self, motor: IMotorPrecios, transaccion_dao: TransaccionDAO):
        self._motor = motor
        self._dao = transaccion_dao
        
    def _mapear_tipo_operacion(self, tipo: int) -> str:
        return 'COMPRA' if tipo == self.OP_COMPRA else 'VENTA'
        
    def ejecutar_orden(self, id_usuario: int, activo: str, cantidad: float, tipo: int) -> bool:
        try:
            precio = self._motor.obtener_precio(activo)
            total = cantidad * precio
            tipo_str = self._mapear_tipo_operacion(tipo)
            
            return self._dao.registrar_transaccion(
                id_usuario, tipo_str, activo, cantidad, precio, total
            )
        except Exception as e:
            print(f"Error crítico en ejecución de orden: {e}")
            return False