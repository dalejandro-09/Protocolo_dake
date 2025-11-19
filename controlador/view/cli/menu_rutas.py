import os
from controlador.controller.ruta_controller import RutaController


class MenuRutas:
    """Menú de gestión de rutas"""

    def __init__(self, controlador):
        self.controlador = controlador
        self.ruta_controller = RutaController()

    def limpiar_pantalla(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def mostrar_menu(self):
        """Muestra el menú de rutas"""
        print("\n GESTIÓN DE RUTAS")
        print("─" * 60)
        print("  1. Calcular ruta entre dos routers")
        print("  2. Ver ruta existente")
        print("  3. Listar todas las rutas")
        print("  4. Ver tabla de enrutamiento de un router")
        print("  5. Recalcular rutas de un router")
        print("  6. Recalcular todas las rutas")
        print("  7. Analizar congestión en la red")
        print("  8. Calcular rutas alternativas")
        print("  9. Visualizar ruta específica")
        print("  0. Volver al menú principal")
        print("─" * 60)

    def calcular_ruta(self):
        """Calcula una ruta entre dos routers"""
        print("\n" + "=" * 60)
        print("CALCULAR RUTA")
        print("=" * 60)

        # Mostrar routers disponibles
        routers = self.controlador.listar_routers(solo_activos=True)
        if len(routers) < 2:
            print(" No hay suficientes routers activos para calcular rutas")
            return

        print("\nRouters disponibles:")
        for router in routers:
            print(f"  ID {router.id_router}: {router.nombre} ({router.ip})")

        try:
            origen = int(input("\nID del router origen: ").strip())
            destino = int(input("ID del router destino: ").strip())
        except ValueError:
            print(" IDs inválidos")
            return

        print("\n Calculando ruta...")
        ruta_info = self.ruta_controller.obtener_ruta_optima(origen, destino)

        if ruta_info:
            print("\n Ruta encontrada:")
            print("─" * 60)
            print(f"Origen:       R{ruta_info['origen']}")
            print(f"Destino:      R{ruta_info['destino']}")
            print(f"Camino:       {ruta_info['camino_str']}")
            print(f"Costo Total:  {ruta_info['costo_total']:.2f}")
            print(f"Nº Saltos:    {ruta_info['numero_saltos']}")

            print("\nRouters en el camino:")
            for i, router_info in enumerate(ruta_info['routers'], 1):
                print(f"  {i}. {router_info['nombre']} ({router_info['ip']})")

            # Preguntar si guardar
            guardar = input("\n¿Guardar esta ruta en la base de datos? (s/n): ").strip().lower()
            if guardar == 's':
                ruta = self.controlador.calcular_ruta(origen, destino, guardar=True)
                if ruta:
                    print(" Ruta guardada exitosamente")
        else:
            print("\n No existe ruta entre los routers seleccionados")

    def ver_ruta_existente(self):
        """Ve una ruta existente"""
        print("\n" + "=" * 60)
        print("VER RUTA EXISTENTE")
        print("=" * 60)

        try:
            origen = int(input("ID del router origen: ").strip())
            destino = int(input("ID del router destino: ").strip())
        except ValueError:
            print(" IDs inválidos")
            return

        ruta = self.controlador.obtener_ruta(origen, destino)

        if ruta:
            router_origen = self.controlador.obtener_router(ruta.router_origen)
            router_destino = self.controlador.obtener_router(ruta.router_destino)

            print("\n" + "─" * 60)
            print(f"ID Ruta:        {ruta.id_ruta}")
            print(f"Origen:         R{ruta.router_origen} ({router_origen.nombre if router_origen else 'N/A'})")
            print(f"Destino:        R{ruta.router_destino} ({router_destino.nombre if router_destino else 'N/A'})")
            print(f"Camino:         {ruta.camino}")
            print(f"Costo Total:    {ruta.costo_total:.2f}")
            print(f"Nº Saltos:      {ruta.numero_saltos()}")
            print(f"Fecha Cálculo:  {ruta.fecha_calculo}")
        else:
            print(f"\n No existe ruta guardada entre R{origen} y R{destino}")

    def listar_todas_rutas(self):
        """Lista todas las rutas"""
        print("\n" + "=" * 60)
        print("LISTA DE TODAS LAS RUTAS")
        print("=" * 60)

        rutas = self.controlador.listar_rutas()

        if not rutas:
            print("\nNo hay rutas calculadas")
            return

        print(f"\nTotal de rutas: {len(rutas)}")
        print(f"\n{'ID':<6} {'Origen':<8} {'Destino':<8} {'Camino':<25} {'Costo':<8} {'Saltos':<8}")
        print("─" * 80)

        for ruta in rutas:
            camino_corto = ruta.camino[:22] + "..." if len(ruta.camino) > 25 else ruta.camino
            print(f"{ruta.id_ruta:<6} R{ruta.router_origen:<7} R{ruta.router_destino:<7} "
                  f"{camino_corto:<25} {ruta.costo_total:<8.2f} {ruta.numero_saltos():<8}")

    def ver_tabla_enrutamiento(self):
        """Ve la tabla de enrutamiento de un router"""
        print("\n" + "=" * 60)
        print("TABLA DE ENRUTAMIENTO")
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

        tabla = self.ruta_controller.obtener_tabla_enrutamiento(id_router)

        print(f"\nTabla de enrutamiento para: {router.nombre} ({router.ip})")
        print("=" * 80)

        if tabla:
            print(f"\n{'Destino':<30} {'Next Hop':<30} {'Costo':<8} {'Saltos':<8}")
            print("─" * 80)

            for entrada in tabla:
                print(f"{entrada['destino']:<30} {entrada['next_hop']:<30} "
                      f"{entrada['costo']:<8.2f} {entrada['saltos']:<8}")
        else:
            print("\nNo hay rutas calculadas para este router")

    def recalcular_rutas_router(self):
        """Recalcula las rutas de un router"""
        print("\n" + "=" * 60)
        print("RECALCULAR RUTAS DE UN ROUTER")
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

        print(f"\n Recalculando rutas para {router.nombre}...")
        total = self.controlador.recalcular_rutas_router(id_router)
        print(f" {total} rutas recalculadas exitosamente")

    def recalcular_todas_rutas(self):
        """Recalcula todas las rutas de la red"""
        print("\n" + "=" * 60)
        print("RECALCULAR TODAS LAS RUTAS")
        print("=" * 60)

        confirmar = input("\n Esto eliminará todas las rutas actuales. ¿Continuar? (s/n): ").strip().lower()

        if confirmar == 's':
            print("\n Recalculando todas las rutas de la red...")
            total = self.controlador.recalcular_todas_rutas()
            print(f" {total} rutas calculadas exitosamente")
        else:
            print("\n Operación cancelada")

    def analizar_congestion(self):
        """Analiza la congestión en la red"""
        print("\n" + "=" * 60)
        print("ANÁLISIS DE CONGESTIÓN")
        print("=" * 60)

        print("\n Analizando uso de enlaces...")
        congestion = self.ruta_controller.analizar_congestion()

        if congestion:
            print(f"\n Enlaces más utilizados (Top 10):")
            print("─" * 60)
            print(f"\n{'Enlace':<30} {'Uso':<10} {'% del Total':<15}")
            print("─" * 60)

            for item in congestion:
                enlace_str = f"{item['router1']} <-> {item['router2']}"
                print(f"{enlace_str:<30} {item['uso']:<10} {item['porcentaje']:<14.1f}%")

            # Identificar posibles cuellos de botella
            print("\n Posibles cuellos de botella:")
            for item in congestion[:3]:  # Top 3
                if item['porcentaje'] > 50:
                    print(f"  • {item['router1']} <-> {item['router2']} ({item['porcentaje']:.1f}% de uso)")
        else:
            print("\n No hay suficientes datos para analizar congestión")

    def calcular_rutas_alternativas(self):
        """Calcula rutas alternativas entre dos routers"""
        print("\n" + "=" * 60)
        print("CALCULAR RUTAS ALTERNATIVAS")
        print("=" * 60)

        # Mostrar routers disponibles
        routers = self.controlador.listar_routers(solo_activos=True)
        if len(routers) < 2:
            print(" No hay suficientes routers activos")
            return

        print("\nRouters disponibles:")
        for router in routers:
            print(f"  ID {router.id_router}: {router.nombre} ({router.ip})")

        try:
            origen = int(input("\nID del router origen: ").strip())
            destino = int(input("ID del router destino: ").strip())
            k = int(input("Número de rutas alternativas (default 3): ").strip() or "3")
        except ValueError:
            print(" Valores inválidos")
            return

        print(f"\n Calculando {k} rutas alternativas...")
        rutas_alt = self.ruta_controller.obtener_rutas_alternativas(origen, destino, k)

        if rutas_alt:
            print(f"\n Se encontraron {len(rutas_alt)} rutas alternativas:")
            print("=" * 60)

            for ruta in rutas_alt:
                print(f"\n Ruta {ruta['numero']}:")
                print(f"   Camino:      {ruta['camino_str']}")
                print(f"   Costo:       {ruta['costo_total']:.2f}")
                print(f"   Saltos:      {ruta['numero_saltos']}")
        else:
            print("\n No se encontraron rutas alternativas")

    def visualizar_ruta_especifica(self):
        """Visualiza una ruta específica en el grafo"""
        print("\n" + "=" * 60)
        print("VISUALIZAR RUTA ESPECÍFICA")
        print("=" * 60)

        # Mostrar routers disponibles
        routers = self.controlador.listar_routers(solo_activos=True)
        if len(routers) < 2:
            print(" No hay suficientes routers activos")
            return

        print("\nRouters disponibles:")
        for router in routers:
            print(f"  ID {router.id_router}: {router.nombre} ({router.ip})")

        try:
            origen = int(input("\nID del router origen: ").strip())
            destino = int(input("ID del router destino: ").strip())
        except ValueError:
            print(" IDs inválidos")
            return

        print("\n Generando visualización...")

        guardar = input("\n¿Guardar imagen? (s/n): ").strip().lower() == 's'

        if guardar:
            archivo = input("Nombre del archivo (default: ruta.png): ").strip() or "ruta.png"
            if not archivo.endswith('.png'):
                archivo += '.png'
        else:
            archivo = None

        try:
            self.controlador.visualizar_ruta(origen, destino, guardar=guardar, archivo=archivo)
        except Exception as e:
            print(f"\n Error al visualizar: {e}")

    def ejecutar(self):
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(" " * 20 + "CONTROLADOR SDN")
            print("=" * 60)
            self.mostrar_menu()

            opcion = input("\n Seleccione una opción: ").strip()

            if opcion == '1':
                self.calcular_ruta()
                input("\nPresione Enter para continuar...")

            elif opcion == '2':
                self.ver_ruta_existente()
                input("\nPresione Enter para continuar...")

            elif opcion == '3':
                self.listar_todas_rutas()
                input("\nPresione Enter para continuar...")

            elif opcion == '4':
                self.ver_tabla_enrutamiento()
                input("\nPresione Enter para continuar...")

            elif opcion == '5':
                self.recalcular_rutas_router()
                input("\nPresione Enter para continuar...")

            elif opcion == '6':
                self.recalcular_todas_rutas()
                input("\nPresione Enter para continuar...")

            elif opcion == '7':
                self.analizar_congestion()
                input("\nPresione Enter para continuar...")

            elif opcion == '8':  # ← NUEVO
                self.calcular_rutas_alternativas()
                input("\nPresione Enter para continuar...")

            elif opcion == '9':  # ← NUEVO
                self.visualizar_ruta_especifica()
                input("\nPresione Enter para continuar...")

            elif opcion == '0':
                break

            else:
                input("\n Opción inválida. Presione Enter para continuar...")