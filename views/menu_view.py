"""
ARGBroker | ENTREGA FINAL PROGRAMACIÓN 1
Interfaz principal, consolidación de activos y monitoreo de mercado.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.live import Live
import time

console = Console()

def generar_tabla_portafolio(repo, id_usuario):
    activos = repo.obtener_portafolio_consolidado(id_usuario)
    tabla = Table(title="Tu Portafolio Consolidado", expand=True, header_style="bold cyan")
    for col in ["Activo", "Unidades", "Precio Prom.", "Valor Actual"]:
        tabla.add_column(col)
    
    if not activos:
        tabla.add_row("N/A", "0.00", "$0.00", "$0.00")
        return tabla

    for item in activos:
        ticker = item['activo']
        unidades = item['total_cantidad']
        promedio = item['precio_promedio_compra']
        actual = repo.buscar_cotizacion(ticker)
        tabla.add_row(ticker, f"{unidades:.2f}", f"${promedio:,.2f}", f"${actual:,.2f}")
    return tabla

def generar_tabla_historial(repo, id_usuario):
    historial = repo.obtener_historial(id_usuario)
    tabla = Table(title="Monitoreo de Mercado en Tiempo Real (Ctrl+C para volver)", expand=True, header_style="bold magenta")
    for col in ["Activo", "Precio Compra", "Precio Actual", "Estado"]:
        tabla.add_column(col)
    
    if not historial:
        return Panel("[yellow]Aún no hay transacciones registradas.[/yellow]")

    for tx in historial[:5]:
        activo = tx['activo']
        precio_compra = float(tx['precio'])
        precio_actual = repo.buscar_cotizacion(activo) 
        
        if precio_actual > precio_compra:
            estado = f"[green]▲ +${(precio_actual - precio_compra):.2f}[/green]"
        elif precio_actual < precio_compra:
            estado = f"[red]▼ -${(precio_compra - precio_actual):.2f}[/red]"
        else:
            estado = "[white] = [/white]"
        tabla.add_row(activo, f"${precio_compra:,.2f}", f"${precio_actual:,.2f}", estado)
    return tabla

def mostrar_menu_principal(usuario, repo):
    id_usuario = usuario['id']
    while True:
        console.clear()
        console.print(Panel(
            f"[bold yellow]ARGBroker v2.0[/bold yellow] | Usuario: [bold cyan]{usuario['nombre']}[/bold cyan] | "
            f"Saldo Disponible: [green]${repo.obtener_saldo(id_usuario):,.2f}[/green]",
            style="bold white"
        ))
        
        console.print(generar_tabla_portafolio(repo, id_usuario))
        
        console.print("\n[bold]ACCIONES:[/bold] [1] Comprar | [2] Vender | [3] Historial (Tiempo Real) | [4] Salir")
        op = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4"], default="4")
        
        if op in ["1", "2"]:
            tipo = 'COMPRA' if op == "1" else 'VENTA'
            ticker = Prompt.ask("Ingrese Ticker").upper()
            precio = repo.buscar_cotizacion(ticker)
            console.print(f"[bold blue]Precio actual: ${precio:,.2f}[/bold blue]")
            try:
                cantidad = float(Prompt.ask("Cantidad"))
                total = cantidad * precio
                if Prompt.ask(f"¿Confirmar {tipo}?", choices=["s", "n"], default="s") == "s":
                    if repo.registrar_transaccion(id_usuario, tipo, ticker, cantidad, precio, total):
                        console.print("[green]✔ Operación exitosa.[/green]")
                    else:
                        console.print("[red]✘ Error: Fondos o activos insuficientes.[/red]")
            except ValueError:
                console.print("[red]! Cantidad inválida.[/red]")
            time.sleep(1.5)

        elif op == "3":
            try:
                with Live(generar_tabla_historial(repo, id_usuario), refresh_per_second=1) as live:
                    while True:
                        time.sleep(1)
                        live.update(generar_tabla_historial(repo, id_usuario))
            except KeyboardInterrupt:
                continue
                
        elif op == "4":
            console.print("[bold green]Sesión finalizada.[/bold green]")
            break