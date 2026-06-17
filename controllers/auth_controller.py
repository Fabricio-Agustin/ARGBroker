from rich.console import Console
from rich.prompt import Prompt
from views.menu_view import mostrar_menu_principal
from views.auth_view import iniciar_sesion, registrar_cuenta

class AuthManager:
    def __init__(self, repo_auth, repo_trans):
        self.repo_auth = repo_auth
        self.repo_trans = repo_trans
        self.console = Console()
        self._running = True

    def run(self):
        while self._running:
            self.console.print("\n[bold blue]─── ARGBroker ENTREGA FINAL ISPC ───[/bold blue]")
            self.console.print("1. Iniciar Sesión\n2. Registrarse\n3. Salir")
            op = Prompt.ask("Selecciona opción", choices=["1", "2", "3"])
            if op == "1": self._handle_login()
            elif op == "2": self._handle_register()
            elif op == "3": self._running = False

    def _handle_login(self):
        user_id = Prompt.ask("Usuario")
        password = Prompt.ask("Contraseña", password=True)
        resultado = iniciar_sesion(self.repo_auth, user_id, password)
        if resultado["exito"]:
            self.console.print(f"[green]{resultado['mensaje']}[/green]")
            mostrar_menu_principal(resultado["usuario"], self.repo_trans)
        else:
            self.console.print(f"[red]{resultado['mensaje']}[/red]")

    def _handle_register(self):
        self.console.print("\n[bold cyan]─── Registro de Nuevo Inversor ───[/bold cyan]")
        user_id = Prompt.ask("ID")
        nombre = Prompt.ask("Nombre")
        email = Prompt.ask("Email")
        password = Prompt.ask("Contraseña", password=True)
        mensaje = registrar_cuenta(self.repo_auth, user_id, nombre, email, password)
        self.console.print(f"[yellow]{mensaje}[/yellow]")