import json
import os
import random
from abc import ABC, abstractmethod
from decimal import Decimal
from models.transaccion_model import (
    obtener_saldo_usuario, 
    actualizar_saldo_usuario, 
    registrar_transaccion_db,
    obtener_portafolio_usuario,
    actualizar_posicion_portafolio
)

class IPersistenciaMercado(ABC):
    @abstractmethod
    def cargar_precios(self) -> dict:
        pass

    @abstractmethod
    def guardar_precios(self, precios: dict) -> None:
        pass


class IMotorVolatilidad(ABC):
    @abstractmethod
    def calcular_siguiente_precio(self, precio_base: float) -> float:
        pass

    @abstractmethod
    def generar_precio_inicial(self) -> float:
        pass


class PersistenciaJSON(IPersistenciaMercado):
    def __init__(self, ruta_archivo: str = "database/market_seed.json"):
        self.__ruta = ruta_archivo

    def cargar_precios(self) -> dict:
        if os.path.exists(self.__ruta):
            try:
                with open(self.__ruta, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def guardar_precios(self, precios: dict) -> None:
        try:
            os.makedirs(os.path.dirname(self.__ruta), exist_ok=True)
            with open(self.__ruta, "w") as f:
                json.dump(precios, f, indent=4)
        except Exception:
            pass


class MotorVolatilidadAleatoria(IMotorVolatilidad):
    def __init__(self, min_inicial: float = 10.0, max_inicial: float = 300.0, 
                 variacion_min: float = 0.95, variacion_max: float = 1.07):
        self.__min_inicial = min_inicial
        self.__max_inicial = max_inicial
        self.__var_min = variacion_min
        self.__var_max = variacion_max

    def generar_precio_inicial(self) -> float:
        return round(random.uniform(self.__min_inicial, self.__max_inicial), 2)

    def calcular_siguiente_precio(self, precio_base: float) -> float:
        variacion = random.uniform(self.__var_min, self.__var_max)
        return round(precio_base * variacion, 2)

class BrokerMarketService:

    OP_VENTA = 0b00
    OP_COMPRA = 0b01
    
    MASCARA_DIRECCION = 0b01   
    MASCARA_VALIDACION = 0b01  

    def __init__(self, persistencia: IPersistenciaMercado = None, volatilidad: IMotorVolatilidad = None):
        self.__persistencia = persistencia if persistencia else PersistenciaJSON()
        self.__volatilidad = volatilidad if volatilidad else MotorVolatilidadAleatoria()
        
        self.__precios_mercado = {}
        self.__inicializar_mercado()

    def __inicializar_mercado(self) -> None:
        datos_recuperados = self.__persistencia.cargar_precios()
        if datos_recuperados:
            self.__precios_mercado.update(datos_recuperados)

    def obtener_o_crear_precio(self, activo: str) -> float:
        activo = activo.strip().upper()
        
        # Si el usuario busca cualquier acción que no existe en el JSON, se genera de cero acá
        if activo not in self.__precios_mercado:
            self.__precios_mercado[activo] = self.__volatilidad.generar_precio_inicial()
        
        precio_anterior = self.__precios_mercado[activo]
        self.__precios_mercado[activo] = self.__volatilidad.calcular_siguiente_precio(precio_anterior)
        
        self.__persistencia.guardar_precios(self.__precios_mercado)
        return self.__precios_mercado[activo]

    def obtener_precios_actualizados(self) -> dict:
        for activo in list(self.__precios_mercado.keys()):
            self.obtener_o_crear_precio(activo)
        return self.__precios_mercado

    def ejecutar_orden_bursatil(self, id_usuario: int, activo: str, cantidad: float, flag_operacion: int) -> str:
        if (flag_operacion & ~self.MASCARA_VALIDACION) != 0:
            return "Error: Flag de operación bursátil inválido o corrupto."

        activo = activo.strip().upper()
        precio_actual = self.obtener_o_crear_precio(activo)
        total_operacion = cantidad * precio_actual
        saldo_actual = obtener_saldo_usuario(id_usuario)
        
        es_compra = bool(flag_operacion & self.MASCARA_DIRECCION)
        
        if es_compra:
            if saldo_actual < total_operacion:
                return f"Error: Saldo insuficiente. Requieres ${total_operacion:.2f} y posees ${saldo_actual:.2f}."
            nuevo_saldo = saldo_actual - total_operacion
            tipo_str = "COMPRA"
        else:
            portafolio = obtener_portafolio_usuario(id_usuario)
            posicion = next((p for p in portafolio if p['activo'] == activo), None)
            if not posicion or float(posicion['cantidad']) < cantidad:
                return f"Error: No posees suficientes activos de {activo} para liquidar."
            
            nuevo_saldo = saldo_actual + total_operacion
            tipo_str = "VENTA"
            precio_compra = float(posicion['precio_compra_promedio'])
            rendimiento = ((precio_actual - precio_compra) / precio_compra) * 100

        if actualizar_saldo_usuario(id_usuario, nuevo_saldo):
            actualizar_posicion_portafolio(id_usuario, activo, cantidad, precio_actual, es_compra=es_compra)
            registrar_transaccion_db(id_usuario, tipo_str, activo, cantidad, precio_actual, total_operacion)
            
            if es_compra:
                return f"Operacion Exitosa: Compraste {cantidad} {activo} a ${precio_actual:.2f} c/u."
            
            if rendimiento >= 0:
                return f"Tomaste ganancias: Vendiste {cantidad} {activo} a ${precio_actual:.2f} c/u (+{rendimiento:.2f}%)."
            return f"Saliste a perdida: Vendiste {cantidad} {activo} a ${precio_actual:.2f} c/u ({rendimiento:.2f}%)."
                
        return f"Error interno al procesar la orden de {tipo_str.lower()}."

    def calcular_rendimiento_por_accion(self, id_usuario: int, id_accion: str) -> tuple:
        id_accion = id_accion.strip().upper()
        portafolio = obtener_portafolio_usuario(id_usuario)
        posicion = next((p for p in portafolio if p['activo'] == id_accion), None)
        
        if not posicion or float(posicion['cantidad']) == 0:
            return {'rendimiento_simple_diario': 0.0, 'rendimiento_acumulado': 0.0}, False

        precio_cierre = Decimal(str(self.obtener_o_crear_precio(id_accion)))
        precio_apertura = precio_cierre * Decimal('0.98')
        rendimiento_simple_diario = ((precio_cierre - precio_apertura) / precio_apertura) * 100
        
        precio_compra_promedio = Decimal(str(posicion['precio_compra_promedio']))
        rendimiento_acumulado = ((precio_cierre - precio_compra_promedio) / precio_compra_promedio) * 100

        return {
            'rendimiento_simple_diario': float(rendimiento_simple_diario),
            'rendimiento_acumulado': float(rendimiento_acumulado)
        }, True