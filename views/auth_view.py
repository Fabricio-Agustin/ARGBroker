from rich.console import Console
from rich.panel import Panel
from controllers.auth_controller import iniciar_sesion, registrar_cuenta
from views.menu_view import mostrar_menu_principal

console = Console()

def mostrar_menu_auth():
    while True:
        bienvenida = "[bold white]Bienvenido a la plataforma de inversiones ARGBroker.[/bold white]\n[dim]Regístrate para obtener tus $10,000 virtuales y empezar a operar.[/dim]"
        console.print(Panel(bienvenida, title="[bold white] ARGBroker — ENTREGA FINAL[/bold white]", border_style="white"))
        
        print(" 1. Iniciar Sesión")
        print(" 2. Registrar nueva cuenta")
        print(" 3. Salir")
        print("-" * 45)
        
        opcion = input(" Selecciona una opción (1-3): ").strip()
        
        if opcion == "1":
            console.print("\n[bold white]─── INICIO DE SESIÓN ───[/bold white]")
            id_user = input(" Usuario: ").strip()
            password = input(" Contraseña: ").strip()
            
            resultado = iniciar_sesion(id_user, password)
            if resultado["exito"]:
                mostrar_menu_principal(resultado["usuario"]) 
            else:
                console.print(f"\n[bold red]{resultado['mensaje']}[/bold red]\n")
                
        elif opcion == "2":
            console.print("\n[bold white]─── REGISTRO DE CUENTA ───[/bold white]")
            id_user = input(" ID de Usuario único: ").strip()
            nombre = input(" Nombre completo: ").strip()
            email = input(" Correo electrónico: ").strip()
            password = input(" Contraseña segura: ").strip()
            
            mensaje = registrar_cuenta(id_user, nombre, email, password)
            console.print(f"\n{mensaje}\n")
            
        elif opcion == "3":
            console.print("\n Desconectando servidores... ¡Chau!", style="white")
            break