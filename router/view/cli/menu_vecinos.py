import os
from router.config.settings import ESTADOS_VECINO

class MenuVecinos:
    def __init__(self, router_controller):
        self.router_controller = router_controller

    def limpiar_pantalla(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def mostrar_menu(self):
        """Muestra el menú de vecinos"""
        print("\n GESTIÓN DE VECINOS")
        print("─" * 60)
        print("  1. Agregar nuevo vecino")
        print("  2. Listar todos los vecinos")
        print("  3. Ver detalles de un vecino")
        print("  4. Actualizar vecino")
        print("  5. Cambiar estado de vecino")
        print("  6. Eliminar vecino")
        print("  7. Ver vecinos con problemas")
        print("  0. Volver al menú principal")
        print("─" * 60)

    def agregar_vecino(self):
        """Agrega un nuevo vecino"""
        print("\n" + "=" * 60)
        print("AGREGAR NUEVO VECINO")
        print("=" * 60)

        router_vecino = input("Nombre del router vecino: ").strip()
        if not router_vecino:
            print(" El nombre no puede estar vacío")
            return

        ip_vecino = input("IP del vecino: ").strip()
        if not ip_vecino:
            print(" La IP no puede estar vacía")
            return

        try:
            costo = float(input("Costo del enlace (presione Enter para 1.0): ").strip() or "1.0")
        except ValueError:
            print(" Costo inválido")
            return

        print(f"\nEstados disponibles: {', '.join(ESTADOS_VECINO)}")
        estado = input("Estado (presione Enter para 'Down'): ").strip() or 'Down'

        vecino_id = self.router_controller.agregar_vecino(
            router_vecino, ip_vecino, costo, estado
        )

        if vecino_id:
            print(f"\n Vecino agregado exitosamente con ID: {vecino_id}")
        else:
            print("\n No se pudo agregar el vecino")

    def listar_vecinos(self):
        """Lista todos los vecinos"""
        print("\n" + "=" * 60)
        print("LISTA DE VECINOS")
        print("=" * 60)

        solo_activos = input("¿Mostrar solo activos? (s/n): ").strip().lower() == 's'
        vecinos = self.router_controller.listar_vecinos(solo_activos)

        if not vecinos:
            print("\nNo hay vecinos registrados")
            return

        print(f"\n{'ID':<5} {'Nombre':<15} {'IP':<18} {'Estado':<10} {'Costo':<8} {'Último HELLO':<20}")
        print("─" * 90)

        for vecino in vecinos:
            print(f"{vecino.id_vecino:<5} {vecino.router_vecino:<15} {vecino.ip_vecino:<18} "
                  f"{vecino.estado_vecino:<10} {vecino.costo_enlace:<8.2f} "
                  f"{str(vecino.tiempo_ultimo_hello):<20}")

    def ver_detalles_vecino(self):
        """Muestra detalles de un vecino"""
        print("\n" + "=" * 60)
        print("DETALLES DE VECINO")
        print("=" * 60)

        try:
            id_vecino = int(input("ID del vecino: ").strip())
        except ValueError:
            print("ID inválido")
            return

        vecino = self.router_controller.obtener_vecino(id_vecino)

        if not vecino:
            print(f" Vecino con ID {id_vecino} no encontrado")
            return

        print(f"\n{'Campo':<25} {'Valor'}")
        print("─" * 60)
        print(f"{'ID:':<25} {vecino.id_vecino}")
        print(f"{'Nombre:':<25} {vecino.router_vecino}")
        print(f"{'IP:':<25} {vecino.ip_vecino}")
        print(f"{'Estado:':<25} {vecino.estado_vecino}")
        print(f"{'Costo del Enlace:':<25} {vecino.costo_enlace}")
        print(f"{'Último HELLO:':<25} {vecino.tiempo_ultimo_hello}")
        print(f"{'Tiempo sin HELLO:':<25} {vecino.tiempo_sin_hello():.0f} segundos")

    def actualizar_vecino(self):
        """Actualiza un vecino"""
        print("\n" + "=" * 60)
        print("ACTUALIZAR VECINO")
        print("=" * 60)

        try:
            id_vecino = int(input("ID del vecino a actualizar: ").strip())
        except ValueError:
            print(" ID inválido")
            return

        vecino = self.router_controller.obtener_vecino(id_vecino)
        if not vecino:
            print(f" Vecino con ID {id_vecino} no encontrado")
            return

        print(f"\nVecino actual: {vecino.router_vecino} ({vecino.ip_vecino})")
        print("Deje en blanco los campos que no desea modificar")

        nombre = input(f"Nuevo nombre [{vecino.router_vecino}]: ").strip()
        ip = input(f"Nueva IP [{vecino.ip_vecino}]: ").strip()

        costo_str = input(f"Nuevo costo [{vecino.costo_enlace}]: ").strip()
        try:
            costo = float(costo_str) if costo_str else None
        except ValueError:
            print(" Costo inválido")
            return

        print(f"\nEstados disponibles: {', '.join(ESTADOS_VECINO)}")
        estado = input(f"Nuevo estado [{vecino.estado_vecino}]: ").strip()

        if self.router_controller.actualizar_vecino(
                id_vecino,
                router_vecino=nombre if nombre else None,
                ip_vecino=ip if ip else None,
                costo_enlace=costo,
                estado=estado if estado else None
        ):
            print("\n Vecino actualizado exitosamente")
        else:
            print("\n No se pudo actualizar el vecino")

    def cambiar_estado_vecino(self):
        """Cambia el estado de un vecino"""
        print("\n" + "=" * 60)
        print("CAMBIAR ESTADO DE VECINO")
        print("=" * 60)

        try:
            id_vecino = int(input("ID del vecino: ").strip())
        except ValueError:
            print(" ID inválido")
            return

        vecino = self.router_controller.obtener_vecino(id_vecino)
        if not vecino:
            print(f" Vecino con ID {id_vecino} no encontrado")
            return

        print(f"\nVecino: {vecino.router_vecino} - Estado actual: {vecino.estado_vecino}")
        print(f"Estados disponibles: {', '.join(ESTADOS_VECINO)}")

        nuevo_estado = input("Nuevo estado: ").strip()

        if self.router_controller.cambiar_estado_vecino(id_vecino, nuevo_estado):
            print("\n Estado cambiado exitosamente")
        else:
            print("\n No se pudo cambiar el estado")

    def eliminar_vecino(self):
        """Elimina un vecino"""
        print("\n" + "=" * 60)
        print("ELIMINAR VECINO")
        print("=" * 60)

        try:
            id_vecino = int(input("ID del vecino a eliminar: ").strip())
        except ValueError:
            print(" ID inválido")
            return

        vecino = self.router_controller.obtener_vecino(id_vecino)
        if not vecino:
            print(f" Vecino con ID {id_vecino} no encontrado")
            return

        print(f"\n ¿Está seguro de eliminar el vecino '{vecino.router_vecino}'?")
        print("   Esto eliminará también las rutas que usan este vecino")

        confirmar = input("Escriba 'SI' para continuar: ").strip()

        if confirmar == 'SI':
            if self.router_controller.eliminar_vecino(id_vecino):
                print("\n Vecino eliminado exitosamente")
            else:
                print("\n No se pudo eliminar el vecino")
        else:
            print("\n Operación cancelada")

    def ver_vecinos_con_problemas(self):
        """Muestra vecinos con problemas de conectividad"""
        print("\n" + "=" * 60)
        print("VECINOS CON PROBLEMAS")
        print("=" * 60)

        from router.controller.vecino_controller import VecinoController
        vecino_ctrl = VecinoController()

        problemas = vecino_ctrl.obtener_vecinos_con_problemas(40)

        if problemas:
            print(f"\n Se encontraron {len(problemas)} vecinos con problemas:")
            print("\n" + "─" * 80)
            for v in problemas:
                print(f"  • {v['nombre']} ({v['ip']})")
                print(f"    Estado: {v['estado']}, Tiempo sin HELLO: {v['tiempo_sin_hello']:.0f} segundos")
                print()
        else:
            print("\n No se detectaron vecinos con problemas")

    def ejecutar(self):
        """Ejecuta el menú de vecinos"""
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(f" " * 25 + "ROUTER")
            print("=" * 60)
            self.mostrar_menu()

            opcion = input("\n Seleccione una opción: ").strip()

            if opcion == '1':
                self.agregar_vecino()
                input("\nPresione Enter para continuar...")

            elif opcion == '2':
                self.listar_vecinos()
                input("\nPresione Enter para continuar...")

            elif opcion == '3':
                self.ver_detalles_vecino()
                input("\nPresione Enter para continuar...")

            elif opcion == '4':
                self.actualizar_vecino()
                input("\nPresione Enter para continuar...")

            elif opcion == '5':
                self.cambiar_estado_vecino()
                input("\nPresione Enter para continuar...")

            elif opcion == '6':
                self.eliminar_vecino()
                input("\nPresione Enter para continuar...")

            elif opcion == '7':
                self.ver_vecinos_con_problemas()
                input("\nPresione Enter para continuar...")

            elif opcion == '0':
                break

            else:
                input("\n Opción inválida. Presione Enter para continuar...")