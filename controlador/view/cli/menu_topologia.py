import os
from controlador.config.settings import ESTADOS_ENLACE
from controlador.controller.topologia_controller import TopologiaController

class MenuTopologia:
    """Menú de gestión de topología"""

    def __init__(self, controlador):
        self.controlador = controlador
        self.topo_controller = TopologiaController()

    def limpiar_pantalla(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def mostrar_menu(self):
        """Muestra el menú de topología"""
        print("\n GESTIÓN DE TOPOLOGÍA Y ENLACES")
        print("─" * 60)
        print("  1. Crear nuevo enlace")
        print("  2. Listar todos los enlaces")
        print("  3. Ver detalles de un enlace")
        print("  4. Actualizar enlace")
        print("  5. Cambiar estado de enlace")
        print("  6. Eliminar enlace")
        print("  7. Ver topología completa")
        print("  8. Ver vecinos de un router")
        print("  9. Ver matriz de adyacencia")
        print(" 10. Identificar routers críticos")
        print(" 11. Identificar enlaces críticos")
        print(" 12. Visualizar topología de red")
        print(" 13. Ver estadísticas de topología")
        print(" 14. Ver centralidad de routers")
        print("  0. Volver al menú principal")
        print("─" * 60)

    def crear_enlace(self):
        print("\n" + "=" * 60)
        print("CREAR NUEVO ENLACE")
        print("=" * 60)

        # Mostrar routers disponibles
        routers = self.controlador.listar_routers(solo_activos=True)
        if len(routers) < 2:
            print(" No hay suficientes routers activos para crear un enlace")
            return

        print("\nRouters disponibles:")
        for router in routers:
            print(f"  ID {router.id_router}: {router.nombre} ({router.ip})")

        try:
            router_origen = int(input("\nID del router origen: ").strip())
            router_destino = int(input("ID del router destino: ").strip())
            costo = float(input("Costo del enlace: ").strip())
            ancho_banda = input("Ancho de banda (Mbps, opcional): ").strip()
            ancho_banda = float(ancho_banda) if ancho_banda else None

            retardo = input("Retardo (ms, opcional): ").strip()
            retardo = float(retardo) if retardo else None

            print(f"\nEstados disponibles: {', '.join(ESTADOS_ENLACE)}")
            estado = input("Estado (presione Enter para 'Activo'): ").strip() or 'Activo'

        except ValueError:
            print(" Valores inválidos")
            return

        enlace_id = self.controlador.crear_enlace(
            router_origen, router_destino, costo,
            ancho_banda, estado, retardo
        )

        if enlace_id:
            print(f"\n Enlace creado exitosamente con ID: {enlace_id}")
        else:
            print("\n No se pudo crear el enlace")

    def listar_enlaces(self):
        """Lista todos los enlaces"""
        print("\n" + "=" * 60)
        print("LISTA DE ENLACES")
        print("=" * 60)

        solo_activos = input("¿Mostrar solo activos? (s/n): ").strip().lower() == 's'
        enlaces = self.controlador.listar_enlaces(solo_activos)

        if not enlaces:
            print("\nNo hay enlaces registrados")
            return

        print(f"\n{'ID':<5} {'Origen':<8} {'Destino':<8} {'Costo':<8} {'Ancho B.':<10} {'Estado':<10} {'Retardo':<10}")
        print("─" * 80)

        for enlace in enlaces:
            ancho = f"{enlace.ancho_banda:.1f}" if enlace.ancho_banda else "N/A"
            retardo = f"{enlace.retardo_ms:.1f}" if enlace.retardo_ms else "N/A"

            print(f"{enlace.id_enlace:<5} R{enlace.router_origen:<7} R{enlace.router_destino:<7} "
                  f"{enlace.costo:<8.2f} {ancho:<10} {enlace.estado:<10} {retardo:<10}")

    def ver_detalles_enlace(self):
        """Muestra detalles de un enlace"""
        print("\n" + "=" * 60)
        print("DETALLES DE ENLACE")
        print("=" * 60)

        try:
            id_enlace = int(input("ID del enlace: ").strip())
        except ValueError:
            print(" ID inválido")
            return

        enlace = self.controlador.obtener_enlace(id_enlace)

        if not enlace:
            print(f" Enlace con ID {id_enlace} no encontrado")
            return

        router_origen = self.controlador.obtener_router(enlace.router_origen)
        router_destino = self.controlador.obtener_router(enlace.router_destino)

        print(f"\n{'Campo':<20} {'Valor'}")
        print("─" * 60)
        print(f"{'ID:':<20} {enlace.id_enlace}")
        print(f"{'Router Origen:':<20} R{enlace.router_origen} ({router_origen.nombre if router_origen else 'N/A'})")
        print(
            f"{'Router Destino:':<20} R{enlace.router_destino} ({router_destino.nombre if router_destino else 'N/A'})")
        print(f"{'Costo:':<20} {enlace.costo}")
        print(f"{'Ancho de Banda:':<20} {enlace.ancho_banda if enlace.ancho_banda else 'N/A'} Mbps")
        print(f"{'Estado:':<20} {enlace.estado}")
        print(f"{'Retardo:':<20} {enlace.retardo_ms if enlace.retardo_ms else 'N/A'} ms")

    def actualizar_enlace(self):
        """Actualiza un enlace"""
        print("\n" + "=" * 60)
        print("ACTUALIZAR ENLACE")
        print("=" * 60)

        try:
            id_enlace = int(input("ID del enlace a actualizar: ").strip())
        except ValueError:
            print(" ID inválido")
            return

        enlace = self.controlador.obtener_enlace(id_enlace)
        if not enlace:
            print(f" Enlace con ID {id_enlace} no encontrado")
            return

        print(f"\nEnlace actual: R{enlace.router_origen} <-> R{enlace.router_destino}")
        print("Deje en blanco los campos que no desea modificar")

        try:
            costo_str = input(f"Nuevo costo [{enlace.costo}]: ").strip()
            costo = float(costo_str) if costo_str else None

            ancho_str = input(f"Nuevo ancho de banda [{enlace.ancho_banda or 'N/A'}]: ").strip()
            ancho_banda = float(ancho_str) if ancho_str else None

            retardo_str = input(f"Nuevo retardo [{enlace.retardo_ms or 'N/A'}]: ").strip()
            retardo = float(retardo_str) if retardo_str else None

            print(f"\nEstados disponibles: {', '.join(ESTADOS_ENLACE)}")
            estado = input(f"Nuevo estado [{enlace.estado}]: ").strip()

        except ValueError:
            print(" Valores inválidos")
            return

        if self.controlador.actualizar_enlace(
                id_enlace,
                costo=costo,
                ancho_banda=ancho_banda,
                estado=estado if estado else None,
                retardo_ms=retardo
        ):
            print("\n Enlace actualizado exitosamente")
        else:
            print("\n No se pudo actualizar el enlace")

    def cambiar_estado_enlace(self):
        """Cambia el estado de un enlace"""
        print("\n" + "=" * 60)
        print("CAMBIAR ESTADO DE ENLACE")
        print("=" * 60)

        try:
            id_enlace = int(input("ID del enlace: ").strip())
        except ValueError:
            print(" ID inválido")
            return

        enlace = self.controlador.obtener_enlace(id_enlace)
        if not enlace:
            print(f" Enlace con ID {id_enlace} no encontrado")
            return

        print(f"\nEnlace: R{enlace.router_origen} <-> R{enlace.router_destino}")
        print(f"Estado actual: {enlace.estado}")
        print(f"Estados disponibles: {', '.join(ESTADOS_ENLACE)}")

        nuevo_estado = input("Nuevo estado: ").strip()

        if self.controlador.cambiar_estado_enlace(id_enlace, nuevo_estado):
            print("\n Estado cambiado exitosamente")
        else:
            print("\n No se pudo cambiar el estado")

    def eliminar_enlace(self):
        """Elimina un enlace"""
        print("\n" + "=" * 60)
        print("ELIMINAR ENLACE")
        print("=" * 60)

        try:
            id_enlace = int(input("ID del enlace a eliminar: ").strip())
        except ValueError:
            print(" ID inválido")
            return

        enlace = self.controlador.obtener_enlace(id_enlace)
        if not enlace:
            print(f" Enlace con ID {id_enlace} no encontrado")
            return

        print(f"\n ¿Está seguro de eliminar el enlace R{enlace.router_origen} <-> R{enlace.router_destino}?")

        confirmar = input("Escriba 'SI' para continuar: ").strip()

        if confirmar == 'SI':
            if self.controlador.eliminar_enlace(id_enlace):
                print("\n Enlace eliminado exitosamente")
            else:
                print("\n No se pudo eliminar el enlace")
        else:
            print("\n Operación cancelada")

    def ver_topologia_completa(self):
        """Muestra la topología completa"""
        print("\n" + "=" * 60)
        print("TOPOLOGÍA COMPLETA DE LA RED")
        print("=" * 60)

        topologia = self.topo_controller.obtener_topologia_completa()

        print("\n  ROUTERS:")
        print("─" * 60)
        for router in topologia['routers']:
            print(f"  R{router['id']}: {router['nombre']} ({router['ip']}) - {router['estado']}")

        print("\n ENLACES:")
        print("─" * 60)
        for enlace in topologia['enlaces']:
            print(f"  E{enlace['id_enlace']}: R{enlace['router_origen']} <-> R{enlace['router_destino']} "
                  f"(Costo: {enlace['costo']}, Estado: {enlace['estado']})")

    def ver_vecinos_router(self):
        """Muestra los vecinos de un router"""
        print("\n" + "=" * 60)
        print("VECINOS DE UN ROUTER")
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

        vecinos = self.topo_controller.obtener_vecinos_router(id_router)

        print(f"\nRouter: {router.nombre} ({router.ip})")
        print(f"Número de vecinos: {len(vecinos)}")
        print("\n" + "─" * 60)

        if vecinos:
            for vecino in vecinos:
                print(f"  • R{vecino['id']}: {vecino['nombre']} ({vecino['ip']})")
                print(f"    Costo: {vecino['costo']}, Enlace ID: {vecino['enlace_id']}")
        else:
            print("  Este router no tiene vecinos")

    def ver_matriz_adyacencia(self):
        """Muestra la matriz de adyacencia"""
        print("\n" + "=" * 60)
        print("MATRIZ DE ADYACENCIA")
        print("=" * 60)

        matriz_data = self.topo_controller.obtener_matriz_adyacencia()
        router_ids = matriz_data['router_ids']
        matriz = matriz_data['matriz']

        # Imprimir encabezado
        print("\n    ", end="")
        for rid in router_ids:
            print(f"R{rid:<6}", end="")
        print()
        print("    " + "─" * (len(router_ids) * 7))

        # Imprimir filas
        for rid_i in router_ids:
            print(f"R{rid_i:<3} ", end="")
            for rid_j in router_ids:
                valor = matriz[rid_i][rid_j]
                if valor == 0:
                    print(f"{'0':<6}", end="")
                elif valor == float('inf'):
                    print(f"{'∞':<6}", end="")
                else:
                    print(f"{valor:<6.1f}", end="")
            print()

    def identificar_routers_criticos(self):
        """Identifica routers críticos en la red"""
        print("\n" + "=" * 60)
        print("IDENTIFICACIÓN DE ROUTERS CRÍTICOS")
        print("=" * 60)
        print("\n Analizando red (esto puede tomar un momento)...")

        criticos = self.topo_controller.encontrar_routers_criticos()

        if criticos:
            print(f"\n Se encontraron {len(criticos)} routers críticos:")
            print("(Routers cuya falla desconectaría la red)")
            print("\n" + "─" * 60)

            for router in criticos:
                print(f"  • R{router['id']}: {router['nombre']}")
                print(f"    Grado (conexiones): {router['grado']}")
        else:
            print("\n No se encontraron routers críticos")
            print("  La red tiene redundancia suficiente")

    def identificar_enlaces_criticos(self):
        """Identifica enlaces críticos (puentes)"""
        print("\n" + "=" * 60)
        print("IDENTIFICACIÓN DE ENLACES CRÍTICOS")
        print("=" * 60)
        print("\n⏳ Analizando red...")

        enlaces_criticos = self.topo_controller.encontrar_enlaces_criticos()

        if enlaces_criticos:
            print(f"\n Se encontraron {len(enlaces_criticos)} enlaces críticos:")
            print("(Enlaces cuya falla desconectaría la red)")
            print("\n" + "─" * 60)

            for enlace in enlaces_criticos:
                print(f"  • {enlace['router1_nombre']} <-> {enlace['router2_nombre']}")
                print(f"    IDs: R{enlace['router1_id']} <-> R{enlace['router2_id']}")
        else:
            print("\n✓ No se encontraron enlaces críticos")
            print("  La red tiene suficiente redundancia")

    def visualizar_topologia(self):
        """Visualiza la topología de la red"""
        print("\n" + "=" * 60)
        print("VISUALIZAR TOPOLOGÍA DE RED")
        print("=" * 60)

        print("\n Generando visualización...")

        guardar = input("\n¿Guardar imagen? (s/n): ").strip().lower() == 's'

        if guardar:
            archivo = input("Nombre del archivo (default: topologia.png): ").strip() or "topologia.png"
            if not archivo.endswith('.png'):
                archivo += '.png'
        else:
            archivo = None

        try:
            self.controlador.visualizar_topologia(guardar=guardar, archivo=archivo)
        except Exception as e:
            print(f"\n Error al visualizar: {e}")

    def ver_estadisticas_topologia(self):
        """Muestra estadísticas avanzadas de la topología"""
        print("\n" + "=" * 60)
        print("ESTADÍSTICAS DE TOPOLOGÍA")
        print("=" * 60)

        stats = self.topo_controller.obtener_estadisticas_topologia()

        print(f"\n{'Métrica':<25} {'Valor'}")
        print("─" * 60)
        print(f"{'Número de Routers:':<25} {stats['num_routers']}")
        print(f"{'Número de Enlaces:':<25} {stats['num_enlaces']}")
        print(f"{'Densidad del Grafo:':<25} {stats['densidad']:.4f}")

        if stats['diametro'] is not None:
            print(f"{'Diámetro:':<25} {stats['diametro']}")
            print(f"{'Radio:':<25} {stats['radio']}")
        else:
            print(f"{'Diámetro:':<25} N/A (red no conectada)")
            print(f"{'Radio:':<25} N/A (red no conectada)")

    def ver_centralidad_routers(self):
        """Muestra métricas de centralidad de los routers"""
        print("\n" + "=" * 60)
        print("CENTRALIDAD DE ROUTERS")
        print("=" * 60)

        metricas = self.topo_controller.obtener_centralidad_routers()

        if not metricas:
            print("\nNo hay suficientes routers para calcular centralidad")
            return

        # Degree Centrality
        print("\nCentralidad de Grado (Degree Centrality):")
        print("─" * 60)
        degree_sorted = sorted(metricas['degree'].items(), key=lambda x: x[1], reverse=True)
        for router_id, valor in degree_sorted[:10]:
            router = self.controlador.obtener_router(router_id)
            nombre = router.nombre if router else f"R{router_id}"
            print(f"  {nombre:<10} {valor:.4f}")

        # Betweenness Centrality
        print("\n Centralidad de Intermediación (Betweenness):")
        print("─" * 60)
        between_sorted = sorted(metricas['betweenness'].items(), key=lambda x: x[1], reverse=True)
        for router_id, valor in between_sorted[:10]:
            router = self.controlador.obtener_router(router_id)
            nombre = router.nombre if router else f"R{router_id}"
            print(f"  {nombre:<10} {valor:.4f}")

        # Closeness Centrality
        print("\n Centralidad de Cercanía (Closeness):")
        print("─" * 60)
        close_sorted = sorted(metricas['closeness'].items(), key=lambda x: x[1], reverse=True)
        for router_id, valor in close_sorted[:10]:
            router = self.controlador.obtener_router(router_id)
            nombre = router.nombre if router else f"R{router_id}"
            print(f"  {nombre:<10} {valor:.4f}")

    def ejecutar(self):
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(" " * 20 + "CONTROLADOR SDN")
            print("=" * 60)
            self.mostrar_menu()

            opcion = input("\n Seleccione una opción: ").strip()

            if opcion == '1':
                self.crear_enlace()
                input("\nPresione Enter para continuar...")

            elif opcion == '2':
                self.listar_enlaces()
                input("\nPresione Enter para continuar...")

            elif opcion == '3':
                self.ver_detalles_enlace()
                input("\nPresione Enter para continuar...")

            elif opcion == '4':
                self.actualizar_enlace()
                input("\nPresione Enter para continuar...")

            elif opcion == '5':
                self.cambiar_estado_enlace()
                input("\nPresione Enter para continuar...")

            elif opcion == '6':
                self.eliminar_enlace()
                input("\nPresione Enter para continuar...")

            elif opcion == '7':
                self.ver_topologia_completa()
                input("\nPresione Enter para continuar...")

            elif opcion == '8':
                self.ver_vecinos_router()
                input("\nPresione Enter para continuar...")

            elif opcion == '9':
                self.ver_matriz_adyacencia()
                input("\nPresione Enter para continuar...")

            elif opcion == '10':
                self.identificar_routers_criticos()
                input("\nPresione Enter para continuar...")

            elif opcion == '11':  # ← NUEVO
                self.identificar_enlaces_criticos()
                input("\nPresione Enter para continuar...")

            elif opcion == '12':  # ← NUEVO
                self.visualizar_topologia()
                input("\nPresione Enter para continuar...")

            elif opcion == '13':  # ← NUEVO
                self.ver_estadisticas_topologia()
                input("\nPresione Enter para continuar...")

            elif opcion == '14':  # ← NUEVO
                self.ver_centralidad_routers()
                input("\nPresione Enter para continuar...")

            elif opcion == '0':
                break

            else:
                input("\n Opción inválida. Presione Enter para continuar...")