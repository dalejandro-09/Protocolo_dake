import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from router.view.cli.menu_principal import MenuPrincipal
from router.config.database import Database


def main():
    """Función principal"""
    print("=" * 60)
    print(" " * 20 + " ROUTER")
    print(" " * 15 + "Inicializando sistema...")
    print("=" * 60)

    # Solicitar información del router
    print("\n Configuración del Router:")

    try:
        router_id = int(input("ID del router (número): ").strip())
    except ValueError:
        print(" Error: ID debe ser un número")
        input("\nPresione Enter para salir...")
        return

    router_nombre = input("Nombre del router (ej: R1): ").strip()
    if not router_nombre:
        print(" Error: El nombre no puede estar vacío")
        input("\nPresione Enter para salir...")
        return

    router_ip = input("IP del router (ej: 192.168.1.1): ").strip()
    if not router_ip:
        print(" Error: La IP no puede estar vacía")
        input("\nPresione Enter para salir...")
        return

    # Probar conexión a la base de datos
    print("\n Conectando a la base de datos...")
    db = Database()
    connection = db.connect()

    if connection is None:
        print("\n Error: No se pudo conectar a la base de datos")
        print("  Verifique la configuración en router/config/settings.py")
        input("\nPresione Enter para salir...")
        return

    print(" Conexión a base de datos establecida")
    print(f" Router {router_nombre} ({router_ip}) configurado")
    print(" Sistema listo")
    input("\nPresione Enter para continuar...")

    # Iniciar menú principal - ¡CON LOS TRES ARGUMENTOS!
    menu = MenuPrincipal(router_id, router_nombre, router_ip)
    menu.ejecutar()

    # Cerrar conexión al salir
    db.disconnect()
    print(f"\n Router {router_nombre} cerrado correctamente\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Programa interrumpido por el usuario")
        print(" Cerrando sistema...\n")
    except Exception as e:
        print(f"\n Error fatal: {e}")
        import traceback

        traceback.print_exc()
        input("\nPresione Enter para salir...")
