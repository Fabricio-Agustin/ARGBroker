# Desde app.py se ejecuta absolutamente todo el programa completo
from views.auth_view import mostrar_menu_auth

def main():
    # Arrancamos el flujo desde la pantalla de login/registro
    mostrar_menu_auth()

# Punto de entrada del programa
if __name__ == "__main__":
    main()