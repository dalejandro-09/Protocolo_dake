import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controlador.view.cli.menu_principal import MenuPrincipal
from controlador.config.database import Database


def main():
    """Función principal"""
    print("=" * 60)
    print(" " * 15 + "CONTROLADOR SDN ")
    print(" " * 10 + "Inicializando sistema...")
    print("=" * 60)

    # Probar conexión a la base de datos
    db = Database()
    connection = db.connect()

    if connection is None:
        print("\n Error: No se pudo conectar a la base de datos")
        print("  Verifique la configuración en controlador_sdn/config/settings.py")
        input("\nPresione Enter para salir...")
        return

    print("\n Conexión a base de datos establecida")
    print(" Sistema listo")
    input("\nPresione Enter para continuar...")

    # Iniciar menú principal
    menu = MenuPrincipal()
    menu.ejecutar()

    # Cerrar conexión al salir
    db.disconnect()
    print("\n Sistema cerrado correctamente\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Programa interrumpido por el usuario")
        print(" Cerrando sistema...\n")
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        import traceback

        traceback.print_exc()
        input("\nPresione Enter para salir...")

