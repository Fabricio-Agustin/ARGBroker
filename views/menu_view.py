from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from controllers.rendimiento_service import BrokerMarketService
from models.transaccion_model import obtener_saldo_usuario, obtener_portafolio_usuario

console = Console()
market_service = BrokerMarketService()

def mostrar_encabezado_institucional():
    """Genera el banner principal del sistema en consola."""
    banner_text = (
        "[bold white]ARGBROKER — COMPRA Y VENTA DE ACCIONES[/bold white]\n"
        "[italic white]PROYECTO INTEGRADOR FINAL[/italic white]"
    )
    console.print(
        Panel(
            Align.center(banner_text),
            border_style="white",
            padding=(1, 2)
        )
    )

def mostrar_mi_portafolio(id_usuario):
    """Muestra las posiciones y los rendimientos calculados en tiempo real."""
    portafolio = obtener_portafolio_usuario(id_usuario)
    
    console.print("\n[bold white]─── PORTAFOLIO DE ACTIVOS GUARDADOS ───[/bold white]")
    if not portafolio:
        console.print(" No posees posiciones abiertas en tu portafolio.", style="white")
        console.print("-" * 55, style="white")
        return

    table = Table(show_header=True, header_style="white", box=None)
    table.add_column("ACTIVO", justify="center", style="bold white")
    table.add_column("CANTIDAD", justify="right", style="white")
    table.add_column("PPC (Tu Compra)", justify="right", style="white")
    table.add_column("VALOR HOY", justify="right", style="white")
    table.add_column("REND. ACUM.", justify="right", style="white")
    table.add_column("ESTADO", justify="center", style="white")

    for p in portafolio:
        activo = p['activo']
        cant = float(p['cantidad'])
        
        metricas, exito = market_service.calcular_rendimiento_por_accion(id_usuario, activo)
        precio_hoy = market_service.obtener_o_crear_precio(activo)
        
        rend_acum = metricas['rendimiento_acumulado']
        estado = "GANANDO" if rend_acum >= 0 else "PERDIENDO"
        
        table.add_row(
            activo, 
            f"{cant:.2f}", 
            f"${float(p['precio_compra_promedio']):.2f}", 
            f"${precio_hoy:.2f}", 
            f"{rend_acum:+.2f}%", 
            estado
        )
        
    console.print(table)
    console.print("-" * 55, style="white")

def mostrar_menu_principal(usuario):
    id_usuario = usuario['id']
    nombre_usuario = usuario['nombre']
    
    while True:
        mostrar_encabezado_institucional()
        
        saldo = obtener_saldo_usuario(id_usuario)
        info_perfil = f"Inversor: {nombre_usuario}  |  Billetera disponible: ${saldo:.2f}"
        
        console.print(
            Panel(
                info_perfil, 
                title="[bold white]PANEL DE TRADING[/bold white]", 
                border_style="white", 
                expand=False
            )
        )
        
        console.print(" 1. Buscar Accion y Ejecutar COMPRA", style="white")
        console.print(" 2. Buscar Accion y Ejecutar VENTA", style="white")
        console.print(" 3. Ver Mi Portafolio y Rendimientos Reales", style="white")
        console.print(" 4. Cerrar Sesion", style="white")
        console.print("-" * 55, style="white")
        
        opcion = input(" Selecciona una opcion (1-4): ").strip()
        
        if opcion == "1":
            console.print("\n[bold white]─── MOTOR DE BUSQUEDA Y COMPRA ───[/bold white]")
            activo = input(" Ingresa el Ticker del activo que buscas (Ej: NVDA, GGAL, AAPL, MSFT): ").strip().upper()
            
            precio_mercado = market_service.obtener_o_crear_precio(activo)
            console.print(f" * Activo: {activo} | Estado: DISPONIBLE | Cotizacion actual: ${precio_mercado:.2f}")
            
            confirmar = input(f" ¿Deseas colocar una orden de compra sobre {activo}? (s/n): ").strip().lower()
            if confirmar == 's':
                try:
                    cantidad = float(input(" Cantidad de acciones a comprar: "))
                    if cantidad <= 0: 
                        raise ValueError
                    
                    resultado = market_service.ejecutar_orden_bursatil(
                        id_usuario, activo, cantidad, market_service.OP_COMPRA
                    )
                    console.print(f"\n {resultado}")
                except ValueError:
                    console.print("\n[bold white] Error: Cantidad invalida.[/bold white]")
            else:
                console.print("\n Orden de compra cancelada por el operador.", style="white")
            console.print("-" * 55, style="white")
            
        elif opcion == "2":
            console.print("\n[bold white]─── MOTOR DE BUSQUEDA Y VENTA ───[/bold white]")
            mostrar_mi_portafolio(id_usuario)
            activo = input(" Ingresa el Ticker del activo a liquidar: ").strip().upper()
            
            precio_mercado = market_service.obtener_o_crear_precio(activo)
            console.print(f" * Activo: {activo} | Valor de mercado actual: ${precio_mercado:.2f}")
            
            confirmar = input(f" ¿Deseas confirmar la venta en el mercado de {activo}? (s/n): ").strip().lower()
            if confirmar == 's':
                try:
                    cantidad = float(input(" Cantidad de acciones a vender: "))
                    if cantidad <= 0: 
                        raise ValueError
                    
                    resultado = market_service.ejecutar_orden_bursatil(
                        id_usuario, activo, cantidad, market_service.OP_VENTA
                    )
                    console.print(f"\n {resultado}")
                except ValueError:
                    console.print("\n[bold white] Error: Cantidad invalida.[/bold white]")
            else:
                console.print("\n Orden de venta cancelada.", style="white")
            console.print("-" * 55, style="white")
            
        elif opcion == "3":
            mostrar_mi_portafolio(id_usuario)
            
        elif opcion == "4":
            console.print("\n Sesion cerrada correctamente. Volviendo al menu de autenticacion...", style="white")
            break