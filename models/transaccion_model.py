"""
Este módulo gestiona la persistencia de datos financieros. Su responsabilidad es garantizar que el saldo, 
el inventario de activos y el historial de compras/ventas siempre sean exactos y coherentes.
"""

class TransaccionRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def obtener_saldo(self, id_usuario: int) -> float:
        try:
            with self.db.cursor(dictionary=True) as (cur, _):
                cur.execute("SELECT saldo FROM usuarios WHERE id = %s", (id_usuario,))
                res = cur.fetchone()
                return float(res['saldo']) if res else 0.0
        except Exception:
            return 0.0

    def obtener_historial(self, id_usuario: int) -> list:
        query = """SELECT tipo, activo, cantidad, precio, total, fecha 
                   FROM transacciones 
                   WHERE id_usuario = %s 
                   ORDER BY fecha DESC"""
        with self.db.cursor(dictionary=True) as (cur, _):
            cur.execute(query, (id_usuario,))
            return cur.fetchall()

    def obtener_cantidad_poseida(self, id_usuario: int, activo: str) -> float:
        query = """SELECT SUM(CASE WHEN tipo = 'COMPRA' THEN cantidad ELSE -cantidad END) as total 
                   FROM transacciones WHERE id_usuario = %s AND activo = %s"""
        with self.db.cursor(dictionary=True) as (cur, _):
            cur.execute(query, (id_usuario, activo))
            res = cur.fetchone()
            return float(res['total'] or 0)

    def obtener_portafolio_consolidado(self, id_usuario: int) -> list:
        query = """SELECT activo, 
                          SUM(CASE WHEN tipo = 'COMPRA' THEN cantidad ELSE -cantidad END) as total_cantidad,
                          AVG(precio) as precio_promedio_compra
                   FROM transacciones 
                   WHERE id_usuario = %s 
                   GROUP BY activo 
                   HAVING total_cantidad > 0"""
        with self.db.cursor(dictionary=True) as (cur, _):
            cur.execute(query, (id_usuario,))
            return cur.fetchall()

    def buscar_cotizacion(self, ticker: str) -> float:
        ticker = ticker.upper()
        with self.db.cursor(dictionary=True) as (cur, conn):
            cur.execute("SELECT precio_actual FROM activos WHERE ticker = %s", (ticker,))
            res = cur.fetchone()
            if res:
                return float(res['precio_actual'])
            else:
                cur.execute("INSERT INTO activos (ticker, precio_actual) VALUES (%s, 100.00)", (ticker,))
                conn.commit()
                return 100.00

    def registrar_transaccion(self, id_usuario: int, tipo: str, activo: str, cantidad: float, precio: float, total: float) -> bool:
        if cantidad <= 0: return False
        
        with self.db.cursor(dictionary=False) as (cur, conn):
            try:
                cur.execute("START TRANSACTION")
                
                if tipo.upper() == 'COMPRA':
                    if self.obtener_saldo(id_usuario) < total: 
                        raise ValueError("Fondos insuficientes")
                else: 
                    if self.obtener_cantidad_poseida(id_usuario, activo) < cantidad:
                        raise ValueError("No posees suficientes activos para vender")

                cur.execute("""INSERT INTO transacciones (id_usuario, tipo, activo, cantidad, precio, total) 
                                VALUES (%s, %s, %s, %s, %s, %s)""", 
                            (id_usuario, tipo, activo, cantidad, precio, total))
                
                signo = -1 if tipo.upper() == 'COMPRA' else 1
                cur.execute("UPDATE usuarios SET saldo = saldo + (%s * %s) WHERE id = %s", 
                            (signo, total, id_usuario))
                
                conn.commit()
                return True
            except Exception as e:
                print(f"Error en transacción: {e}")
                conn.rollback()
                return False