import os
from controlador.config.settings import ESTADOS_ROUTER

class MenuRouter:
    """Menú de gestión de routers"""

    def __init__(self, controlador):
        self.controlador = controlador

    def limpiar_pantalla(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def mostrar_menu(self):
        """Muestra el menú de routers"""
        print("\n  GESTIÓN DE ROUTERS")
        print("─" * 60)
        print("  1. Crear nuevo router")
        print("  2. Listar todos los routers")
        print("  3. Ver detalles de un router")
        print("  4. Actualizar router")
        print("  5. Cambiar estado de router")
        print("  6. Eliminar router")
        print("  0. Volver al menú principal")
        print("─" * 60)

    def crear_router(self):
        """Crea un nuevo router"""
        print("\n" + "=" * 60)
        print("CREAR NUEVO ROUTER")
        print("=" * 60)

        nombre = input("Nombre del router: ").strip()
        if not nombre:
            print("✗ El nombre no puede estar vacío")
            return

        ip = input("Dirección IP: ").strip()
        if not ip:
            print(" La IP no puede estar vacía")
            return

        print(f"\nEstados disponibles: {', '.join(ESTADOS_ROUTER)}")
        estado = input("Estado (presione Enter para 'Activo'): ").strip() or 'Activo'

        if estado not in ESTADOS_ROUTER:
            print(f" Estado inválido. Debe ser uno de: {ESTADOS_ROUTER}")
            return

        router_id = self.controlador.crear_router(nombre, ip, estado)

        if router_id:
            print(f"\n Router creado exitosamente con ID: {router_id}")
        else:
            print("\n No se pudo crear el router")

    def listar_routers(self):
        """Lista todos los routers"""
        print("\n" + "=" * 60)
        print("LISTA DE ROUTERS")
        print("=" * 60)

        solo_activos = input("¿Mostrar solo activos? (s/n): ").strip().lower() == 's'
        routers = self.controlador.listar_routers(solo_activos)

        if not routers:
            print("\nNo hay routers registrados")
            return

        print(f"\n{'ID':<5} {'Nombre':<12} {'IP':<18} {'Estado':<18} {'Última Act.':<20}")
        print("─" * 80)

        for router in routers:
            print(f"{router.id_router:<5} {router.nombre:<12} {router.ip:<18} "
                  f"{router.estado:<18} {str(router.ultima_actualizacion):<20}")

    def ver_detalles_router(self):
        """Muestra detalles de un router"""
        print("\n" + "=" * 60)
        print("DETALLES DE ROUTER")
        print("=" * 60)

        try:
            id_router = int(input("ID del router: ").strip())
        except ValueError:
            print(" ID inválido")
            return

        router = self.controlador.obtener_router(id_router)

        if not router:
            print(f" Router con ID {id_router} no encontrado")
            return

        print(f"\n{'Campo':<20} {'Valor'}")
        print("─" * 60)
        print(f"{'ID:':<20} {router.id_router}")
        print(f"{'Nombre:':<20} {router.nombre}")
        print(f"{'IP:':<20} {router.ip}")
        print(f"{'Estado:':<20} {router.estado}")
        print(f"{'Última Act.:':<20} {router.ultima_actualizacion}")

        # Mostrar enlaces
        enlaces = self.controlador.obtener_enlaces_router(id_router)
        print(f"\n{'Enlaces:':<20} {len(enlaces)}")

        if enlaces:
            print("\nEnlaces del router:")
            for enlace in enlaces:
                if enlace.router_origen == id_router:
                    print(f"  → R{enlace.router_destino} (Costo: {enlace.costo}, Estado: {enlace.estado})")
                else:
                    print(f"  ← R{enlace.router_origen} (Costo: {enlace.costo}, Estado: {enlace.estado})")

    def actualizar_router(self):
        """Actualiza un router"""
        print("\n" + "=" * 60)
        print("ACTUALIZAR ROUTER")
        print("=" * 60)

        try:
            id_router = int(input("ID del router a actualizar: ").strip())
        except ValueError:
            print(" ID inválido")
            return

        router = self.controlador.obtener_router(id_router)
        if not router:
            print(f" Router con ID {id_router} no encontrado")
            return

        print(f"\nRouter actual: {router.nombre} ({router.ip})")
        print("Deje en blanco los campos que no desea modificar")

        nombre = input(f"Nuevo nombre [{router.nombre}]: ").strip()
        ip = input(f"Nueva IP [{router.ip}]: ").strip()

        print(f"\nEstados disponibles: {', '.join(ESTADOS_ROUTER)}")
        estado = input(f"Nuevo estado [{router.estado}]: ").strip()

        if self.controlador.actualizar_router(
                id_router,
                nombre=nombre if nombre else None,
                ip=ip if ip else None,
                estado=estado if estado else None
        ):
            print("\n Router actualizado exitosamente")
        else:
            print("\n No se pudo actualizar el router")

    def cambiar_estado_router(self):
        """Cambia el estado de un router"""
        print("\n" + "=" * 60)
        print("CAMBIAR ESTADO DE ROUTER")
        print("=" * 60)

        try:
            id_router = int(input("ID del router: ").strip())
        except ValueError:
            print(" ID inválido")
            return

        router = self.controlador.obtener_router(id_router)
        if not router:
            print(f" Router con ID {id_router} no encontrado")
            return

        print(f"\nRouter: {router.nombre} - Estado actual: {router.estado}")
        print(f"Estados disponibles: {', '.join(ESTADOS_ROUTER)}")

        nuevo_estado = input("Nuevo estado: ").strip()

        if self.controlador.cambiar_estado_router(id_router, nuevo_estado):
            print("\n Estado cambiado exitosamente")
        else:
            print("\n No se pudo cambiar el estado")

    def eliminar_router(self):
        """Elimina un router"""
        print("\n" + "=" * 60)
        print("ELIMINAR ROUTER")
        print("=" * 60)

        try:
            id_router = int(input("ID del router a eliminar: ").strip())
        except ValueError:
            print(" ID inválido")
            return

        router = self.controlador.obtener_router(id_router)
        if not router:
            print(f" Router con ID {id_router} no encontrado")
            return

        print(f"\n¿Está seguro de eliminar el router '{router.nombre}'?")
        print("   Esto eliminará también todos sus enlaces y rutas")

        confirmar = input("Escriba 'CONFIRMAR' para continuar: ").strip()

        if confirmar == 'CONFIRMAR':
            if self.controlador.eliminar_router(id_router):
                print("\n Router eliminado exitosamente")
            else:
                print("\n No se pudo eliminar el router")
        else:
            print("\n Operación cancelada")

    def ejecutar(self):
        """Ejecuta el menú de routers"""
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(" " * 20 + "CONTROLADOR SDN")
            print("=" * 60)
            self.mostrar_menu()

            opcion = input("\n Seleccione una opción: ").strip()

            if opcion == '1':
                self.crear_router()
                input("\nPresione Enter para continuar...")

            elif opcion == '2':
                self.listar_routers()
                input("\nPresione Enter para continuar...")

            elif opcion == '3':
                self.ver_detalles_router()
                input("\nPresione Enter para continuar...")

            elif opcion == '4':
                self.actualizar_router()
                input("\nPresione Enter para continuar...")

            elif opcion == '5':
                self.cambiar_estado_router()
                input("\nPresione Enter para continuar...")

            elif opcion == '6':
                self.eliminar_router()
                input("\nPresione Enter para continuar...")

            elif opcion == '0':
                break

            else:
                input("\n Opción inválida. Presione Enter para continuar...")