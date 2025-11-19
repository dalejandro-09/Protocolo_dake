import os
from router.config.settings import ORIGEN_INFO

class MenuEnrutamiento:
    def __init__(self, router_controller):
        self.router_controller = router_controller

    def limpiar_pantalla(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def mostrar_menu(self):
        """Muestra el menú de enrutamiento"""
        print("\n GESTIÓN DE TABLA DE ENRUTAMIENTO")
        print("─" * 60)
        print("  1. Agregar nueva ruta")
        print("  2. Listar todas las rutas")
        print("  3. Ver detalles de una ruta")
        print("  4. Actualizar ruta")
        print("  5. Eliminar ruta")
        print("  6. Buscar ruta a destino")
        print("  7. Listar rutas por origen")
        print("  8. Validar tabla de enrutamiento")
        print("  0. Volver al menú principal")
        print("─" * 60)

    def agregar_ruta(self):
        """Agrega una nueva ruta"""
        print("\n" + "=" * 60)
        print("AGREGAR NUEVA RUTA")
        print("=" * 60)

        destino = input("Destino (IP o red): ").strip()
        if not destino:
            print(" El destino no puede estar vacío")
            return

        next_hop = input("Next hop (IP): ").strip()
        if not next_hop:
            print(" El next hop no puede estar vacío")
            return

        interfaz_salida = input("Interfaz de salida: ").strip()
        if not interfaz_salida:
            print(" La interfaz no puede estar vacía")
            return

        try:
            costo = float(input("Costo total (presione Enter para 0.0): ").strip() or "0.0")
        except ValueError:
            print(" Costo inválido")
            return

        print(f"\nOrígenes disponibles: {', '.join(ORIGEN_INFO)}")
        origen = input("Origen de información (presione Enter para 'Interna'): ").strip() or 'Interna'

        ruta_id = self.router_controller.agregar_ruta(
            destino, next_hop, interfaz_salida, costo, origen
        )

        if ruta_id:
            print(f"\n Ruta agregada exitosamente con ID: {ruta_id}")
        else:
            print("\n No se pudo agregar la ruta")

    def listar_rutas(self):
        """Lista todas las rutas"""
        print("\n" + "=" * 60)
        print("TABLA DE ENRUTAMIENTO")
        print("=" * 60)

        print("\n¿Filtrar por origen? (Deje en blanco para mostrar todas)")
        print(f"Opciones: {', '.join(ORIGEN_INFO)}")
        filtro = input("Origen: ").strip() or None

        rutas = self.router_controller.listar_rutas(filtro_origen=filtro)

        if not rutas:
            print("\nNo hay rutas en la tabla de enrutamiento")
            return

        print(f"\n{'ID':<5} {'Destino':<18} {'Next Hop':<18} {'Interfaz':<12} {'Costo':<8} {'Origen':<12}")
        print("─" * 90)

        for ruta in rutas:
            print(f"{ruta.id_ruta:<5} {ruta.destino:<18} {ruta.next_hop:<18} "
                  f"{ruta.interfaz_salida:<12} {ruta.costo_total:<8.2f} {ruta.origen_info:<12}")

    def ver_detalles_ruta(self):
        """Muestra detalles de una ruta"""
        print("\n" + "=" * 60)
        print("DETALLES DE RUTA")
        print("=" * 60)

        try:
            id_ruta = int(input("ID de la ruta: ").strip())
        except ValueError:
            print("ID inválido")
            return

        ruta = self.router_controller.obtener_ruta(id_ruta)

        if not ruta:
            print(f" Ruta con ID {id_ruta} no encontrada")
            return

        print(f"\n{'Campo':<25} {'Valor'}")
        print("─" * 60)
        print(f"{'ID:':<25} {ruta.id_ruta}")
        print(f"{'Destino:':<25} {ruta.destino}")
        print(f"{'Next Hop:':<25} {ruta.next_hop}")
        print(f"{'Interfaz de Salida:':<25} {ruta.interfaz_salida}")
        print(f"{'Costo Total:':<25} {ruta.costo_total}")
        print(f"{'Origen de Info:':<25} {ruta.origen_info}")

    def actualizar_ruta(self):
        """Actualiza una ruta"""
        print("\n" + "=" * 60)
        print("ACTUALIZAR RUTA")
        print("=" * 60)

        try:
            id_ruta = int(input("ID de la ruta a actualizar: ").strip())
        except ValueError:
            print(" ID inválido")
            return

        ruta = self.router_controller.obtener_ruta(id_ruta)
        if not ruta:
            print(f" Ruta con ID {id_ruta} no encontrada")
            return

        print(f"\nRuta actual: {ruta.destino} via {ruta.next_hop}")
        print("Deje en blanco los campos que no desea modificar")

        destino = input(f"Nuevo destino [{ruta.destino}]: ").strip()
        next_hop = input(f"Nuevo next hop [{ruta.next_hop}]: ").strip()
        interfaz = input(f"Nueva interfaz [{ruta.interfaz_salida}]: ").strip()

        costo_str = input(f"Nuevo costo [{ruta.costo_total}]: ").strip()
        try:
            costo = float(costo_str) if costo_str else None
        except ValueError:
            print(" Costo inválido")
            return

        print(f"\nOrígenes disponibles: {', '.join(ORIGEN_INFO)}")
        origen = input(f"Nuevo origen [{ruta.origen_info}]: ").strip()

        if self.router_controller.actualizar_ruta(
            id_ruta,
            destino=destino if destino else None,
            next_hop=next_hop if next_hop else None,
            interfaz_salida=interfaz if interfaz else None,
            costo_total=costo,
            origen_info=origen if origen else None
        ):
            print("\n Ruta actualizada exitosamente")
        else:
            print("\n No se pudo actualizar la ruta")

    def eliminar_ruta(self):
        """Elimina una ruta"""
        print("\n" + "=" * 60)
        print("ELIMINAR RUTA")
        print("=" * 60)

        try:
            id_ruta = int(input("ID de la ruta a eliminar: ").strip())
        except ValueError:
            print("ID inválido")
            return

        ruta = self.router_controller.obtener_ruta(id_ruta)
        if not ruta:
            print(f" Ruta con ID {id_ruta} no encontrada")
            return

        print(f"\n ¿Está seguro de eliminar la ruta a '{ruta.destino}'?")

        confirmar = input("Escriba 'SI' para continuar: ").strip()

        if confirmar == 'SI':
            if self.router_controller.eliminar_ruta(id_ruta):
                print("\n Ruta eliminada exitosamente")
            else:
                print("\n No se pudo eliminar la ruta")
        else:
            print("\n Operación cancelada")

    def buscar_ruta_destino(self):
        """Busca una ruta a un destino específico"""
        print("\n" + "=" * 60)
        print("BUSCAR RUTA A DESTINO")
        print("=" * 60)

        destino = input("Destino a buscar: ").strip()
        if not destino:
            print("El destino no puede estar vacío")
            return

        ruta = self.router_controller.obtener_ruta_a_destino(destino)

        if ruta:
            print("\n Ruta encontrada:")
            print("─" * 60)
            print(f"Destino:       {ruta.destino}")
            print(f"Next Hop:      {ruta.next_hop}")
            print(f"Interfaz:      {ruta.interfaz_salida}")
            print(f"Costo:         {ruta.costo_total}")
            print(f"Origen:        {ruta.origen_info}")
        else:
            print(f"\n No se encontró ruta a {destino}")

    def listar_rutas_por_origen(self):
        """Lista rutas filtradas por origen"""
        print("\n" + "=" * 60)
        print("LISTAR RUTAS POR ORIGEN")
        print("=" * 60)

        print(f"\nOrígenes disponibles: {', '.join(ORIGEN_INFO)}")
        origen = input("Origen a filtrar: ").strip()

        if origen not in ORIGEN_INFO:
            print(f" Origen inválido. Debe ser uno de: {ORIGEN_INFO}")
            return

        rutas = self.router_controller.listar_rutas(filtro_origen=origen)

        if not rutas:
            print(f"\nNo hay rutas de origen '{origen}'")
            return

        print(f"\nRutas de origen '{origen}': {len(rutas)}")
        print(f"\n{'ID':<5} {'Destino':<18} {'Next Hop':<18} {'Interfaz':<12} {'Costo':<8}")
        print("─" * 80)

        for ruta in rutas:
            print(f"{ruta.id_ruta:<5} {ruta.destino:<18} {ruta.next_hop:<18} "
                  f"{ruta.interfaz_salida:<12} {ruta.costo_total:<8.2f}")

    def validar_tabla_enrutamiento(self):
        """Valida la tabla de enrutamiento"""
        print("\n" + "=" * 60)
        print("VALIDACIÓN DE TABLA DE ENRUTAMIENTO")
        print("=" * 60)

        from router.controller.enrutamiento_controller import EnrutamientoController
        enrut_ctrl = EnrutamientoController()

        validacion = enrut_ctrl.validar_tabla_enrutamiento()

        if validacion['valida']:
            print("\n La tabla de enrutamiento es válida")
        else:
            print("\n Se encontraron problemas en la tabla")

        if validacion['errores']:
            print("\n Errores:")
            for error in validacion['errores']:
                print(f"  • {error}")

        if validacion['advertencias']:
            print("\n Advertencias:")
            for adv in validacion['advertencias']:
                print(f"  • {adv}")

    def ejecutar(self):
        """Ejecuta el menú de enrutamiento"""
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(" " * 25 + "ROUTER")
            print("=" * 60)
            self.mostrar_menu()

            opcion = input("\n Seleccione una opción: ").strip()

            if opcion == '1':
                self.agregar_ruta()
                input("\nPresione Enter para continuar...")

            elif opcion == '2':
                self.listar_rutas()
                input("\nPresione Enter para continuar...")

            elif opcion == '3':
                self.ver_detalles_ruta()
                input("\nPresione Enter para continuar...")

            elif opcion == '4':
                self.actualizar_ruta()
                input("\nPresione Enter para continuar...")

            elif opcion == '5':
                self.eliminar_ruta()
                input("\nPresione Enter para continuar...")

            elif opcion == '6':
                self.buscar_ruta_destino()
                input("\nPresione Enter para continuar...")

            elif opcion == '7':
                self.listar_rutas_por_origen()
                input("\nPresione Enter para continuar...")

            elif opcion == '8':
                self.validar_tabla_enrutamiento()
                input("\nPresione Enter para continuar...")

            elif opcion == '0':
                break

            else:
                input("\n Opción inválida. Presione Enter para continuar...")