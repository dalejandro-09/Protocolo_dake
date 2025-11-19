import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def mostrar_banner():
    """Muestra el banner principal"""
    print("\n" + "=" * 70)
    print(" " * 20 + " SISTEMA DE RED SDN ")
    print(" " * 15 + "Simulador de Red de Routers")
    print("=" * 70)


def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "─" * 70)
    print("SELECCIONE EL COMPONENTE A INICIAR:")
    print("─" * 70)
    print("  1. Controlador SDN (Gestor Central)")
    print("  2. Router (Nodo de la Red)")
    print("  3. Ver Guía de Uso")
    print("  0. Salir")
    print("─" * 70)


def iniciar_controlador():
    """Inicia el controlador SDN"""
    print("\n" + "=" * 70)
    print(" " * 25 + "CONTROLADOR SDN")
    print("=" * 70)

    from controlador.config.database import Database
    from controlador.view.cli.menu_principal import MenuPrincipal

    # Probar conexión
    db = Database()
    connection = db.connect()

    if connection is None:
        print("\n✗ Error: No se pudo conectar a controlador_db")
        print("  Verifique la configuración en controlador_sdn/config/settings.py")
        input("\nPresione Enter para continuar...")
        return

    print("\n✓ Conexión a controlador_db establecida")
    print("✓ Sistema listo")
    input("\nPresione Enter para iniciar el controlador...")

    # Iniciar menú
    menu = MenuPrincipal()
    menu.ejecutar()

    # Cerrar conexión
    db.disconnect()


def iniciar_router():
    """Ejecuta un router individual"""
    from router.view.cli.menu_principal import MenuPrincipal
    from router.config.database import Database

    print("\n" + "=" * 60)
    print(" " * 18 + "ROUTER")
    print(" " * 12 + "Inicializando router...")
    print("=" * 60)

    # Solicitar configuración del router
    print("\n Configuración del Router:")

    try:
        router_id = int(input("ID del router (número): ").strip())  # ← CAPTURAR router_id
    except ValueError:
        print(" Error: ID debe ser un número")
        input("\nPresione Enter para continuar...")
        return

    router_nombre = input("Nombre del router (ej: R1): ").strip()
    if not router_nombre:
        print(" Error: El nombre no puede estar vacío")
        input("\nPresione Enter para continuar...")
        return

    router_ip = input("IP del router (ej: 192.168.1.1): ").strip()
    if not router_ip:
        print(" Error: La IP no puede estar vacía")
        input("\nPresione Enter para continuar...")
        return

    # Probar conexión
    print("\n Conectando a router_db...")
    db = Database()
    connection = db.connect()

    if connection is None:
        print("\n Error: No se pudo conectar a router_db")
        print("  Verifique la configuración en router/config/settings.py")
        input("\nPresione Enter para continuar...")
        return

    print(" Conexión a router_db establecida")
    print(f" Router {router_nombre} ({router_ip}) configurado")
    print(" Sistema listo")
    input("\nPresione Enter para continuar...")

    # Iniciar menú del router - ¡AQUÍ ESTÁ LA CORRECCIÓN!
    menu = MenuPrincipal(router_id, router_nombre, router_ip)  # ← TRES ARGUMENTOS
    menu.ejecutar()

    # Cerrar conexión
    db.disconnect()

def mostrar_guia():
    """Muestra la guía de uso del sistema"""
    print("\n" + "=" * 70)
    print(" " * 25 + "📖 GUÍA DE USO")
    print("=" * 70)

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    PASOS PARA PROBAR EL SISTEMA                      ║
╚══════════════════════════════════════════════════════════════════════╝

1️⃣  PREPARAR LAS BASES DE DATOS
   • Ejecutar el script: scripts/crear_bases_datos.sql
   • Esto creará las BD 'controlador' y 'router'

2️⃣  CONFIGURAR CREDENCIALES
   • Editar: controlador_sdn/config/settings.py
   • Editar: router/config/settings.py
   • Cambiar 'password' por tu contraseña de MySQL

3️⃣  INICIAR EL CONTROLADOR SDN (Terminal 1)
   • Ejecutar: python main.py
   • Seleccionar opción 1 (Controlador SDN)
   • Crear routers y enlaces desde el controlador

4️⃣  INICIAR ROUTERS (Terminales 2, 3, 4...)
   • Terminal 2: python main.py → Opción 2 → R1, 192.168.1.1
   • Terminal 3: python main.py → Opción 2 → R2, 192.168.1.2
   • Terminal 4: python main.py → Opción 2 → R3, 192.168.1.3
   • etc...

5️⃣  EJEMPLO DE TOPOLOGÍA (Desde el Controlador)

   Terminal 1 (Controlador):
   • Crear Router: R1, 192.168.1.1
   • Crear Router: R2, 192.168.1.2
   • Crear Router: R3, 192.168.1.3
   • Crear Enlace: R1 <-> R2, costo 1.0
   • Crear Enlace: R2 <-> R3, costo 1.5
   • Calcular rutas: R1 -> R3

6️⃣  AGREGAR VECINOS (Desde cada Router)

   Terminal 2 (R1):
   • Agregar vecino: R2, 192.168.1.2, costo 1.0

   Terminal 3 (R2):
   • Agregar vecino: R1, 192.168.1.1, costo 1.0
   • Agregar vecino: R3, 192.168.1.3, costo 1.5

   Terminal 4 (R3):
   • Agregar vecino: R2, 192.168.1.2, costo 1.5

7️⃣  PROBAR PROTOCOLO OSPF
   • En cualquier router: Protocolo OSPF → Iniciar OSPF
   • Enviar HELLOs manualmente
   • Verificar estado de vecinos

╔══════════════════════════════════════════════════════════════════════╗
║                       TOPOLOGÍA DE EJEMPLO                           ║
╚══════════════════════════════════════════════════════════════════════╝

        R1 (192.168.1.1)
         |
         | costo: 1.0
         |
        R2 (192.168.1.2)
         |
         | costo: 1.5
         |
        R3 (192.168.1.3)

╔══════════════════════════════════════════════════════════════════════╗
║                     COMANDOS ÚTILES                                  ║
╚══════════════════════════════════════════════════════════════════════╝

Controlador:
  • Menú 1: Gestión de Routers
  • Menú 2: Gestión de Enlaces y Topología
  • Menú 3: Gestión de Rutas (Calcular rutas con Dijkstra)
  • Menú 4: Monitoreo (Ver estado de la red)

Router:
  • Menú 1: Gestión de Vecinos
  • Menú 2: Tabla de Enrutamiento
  • Menú 3: Mensajes (Ver comunicaciones)
  • Menú 4: Protocolo OSPF (Iniciar/Detener HELLOs)

╔══════════════════════════════════════════════════════════════════════╗
║                         NOTAS IMPORTANTES                            ║
╚══════════════════════════════════════════════════════════════════════╝

⚠️  El Controlador gestiona la topología GLOBAL
⚠️  Cada Router gestiona su información LOCAL
⚠️  Los routers deben agregarse primero en el Controlador
⚠️  Luego configurar vecinos en cada Router individual
⚠️  El protocolo OSPF simula la comunicación entre routers
    """)

    input("\nPresione Enter para volver al menú...")


def main():
    """Función principal"""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        mostrar_banner()
        mostrar_menu()

        opcion = input("\n➤ Seleccione una opción: ").strip()

        if opcion == '1':
            iniciar_controlador()

        elif opcion == '2':
            iniciar_router()

        elif opcion == '3':
            mostrar_guia()

        elif opcion == '0':
            print("\n" + "=" * 70)
            print(" " * 25 + "¡Hasta luego! ")
            print("=" * 70 + "\n")
            break

        else:
            input("\n✗ Opción inválida. Presione Enter para continuar...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Programa interrumpido por el usuario")
        print("✓ Cerrando sistema...\n")
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        import traceback

        traceback.print_exc()
        input("\nPresione Enter para salir...")