import os
from router.controller.router_controller import RouterController
from router.view.cli.menu_vecinos import MenuVecinos
from router.view.cli.menu_enrutamiento import MenuEnrutamiento
from router.view.cli.menu_mensajes import MenuMensajes


class MenuPrincipal:
    def __init__(self, router_id, router_nombre, router_ip):
        self.router_controller = RouterController(router_id, router_nombre, router_ip)
        self.router_id = router_id
        self.router_nombre = router_nombre
        self.router_ip = router_ip

        self.menu_vecinos = MenuVecinos(self.router_controller)
        self.menu_enrutamiento = MenuEnrutamiento(self.router_controller)
        self.menu_mensajes = MenuMensajes(self.router_controller)

    def limpiar_pantalla(self):
        """Limpia la pantalla de la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def mostrar_banner(self):
        """Muestra el banner de la aplicación"""
        print("=" * 60)
        print(" " * 20 + f" ROUTER {self.router_nombre}")
        print(" " * 18 + f"IP: {self.router_ip}")
        print("=" * 60)
        print()

    def mostrar_resumen(self):
        """Muestra un resumen del estado del router"""
        resumen = self.router_controller.obtener_resumen()

        print(" RESUMEN DEL ROUTER")
        print("-" * 60)
        print(f"  Nombre:   {resumen['router_nombre']}")
        print(f"  IP:       {resumen['router_ip']}")
        print(f"  Vecinos:  {resumen['vecinos_activos']}/{resumen['total_vecinos']} activos")
        print(f"  Rutas:    {resumen['total_rutas']}")
        print(f"  Mensajes: {resumen['total_mensajes']}")
        print(f"  HELLO:    {' Activo' if resumen['hello_activo'] else ' Inactivo'}")
        print("-" * 60)
        print()

    def mostrar_menu(self):
        """Muestra el menú principal"""
        print("MENÚ PRINCIPAL")
        print("─" * 60)
        print("  1. Gestión de Vecinos")
        print("  2.️  Gestión de Tabla de Enrutamiento")
        print("  3. Gestión de Mensajes")
        print("  4. Protocolo OSPF")
        print("  5. Conexión con Controlador SDN")
        print("  6. Estadísticas y Monitoreo")
        print("  7. Ver Logs del Router")
        print("  8. Mantenimiento")
        print("  0. Salir")
        print("─" * 60)

    def menu_ospf(self):
        while True:
            self.limpiar_pantalla()
            self.mostrar_banner()
            print(" PROTOCOLO OSPF")
            print("─" * 60)

            estado = self.router_controller.obtener_estado_ospf()
            print(f"\nEstado de vecinos OSPF:")
            print(f"  • Total:  {estado['total']}")
            print(f"  • Full:   {estado['full']}")
            print(f"  • 2-Way:  {estado['two_way']}")
            print(f"  • Down:   {estado['down']}")

            print("\n" + "─" * 60)
            print("  1. Iniciar protocolo HELLO")
            print("  2. Detener protocolo HELLO")
            print("  3. Enviar HELLO manual a un vecino")
            print("  4. Establecer adyacencia con vecino")
            print("  5. Verificar vecinos caídos")
            print("  6. Ver estado detallado de vecinos")
            print("  0. Volver")
            print("─" * 60)

            opcion = input("\n Seleccione una opción: ").strip()

            if opcion == '1':
                self.router_controller.iniciar_hello_protocol()
                input("\nPresione Enter para continuar...")

            elif opcion == '2':
                self.router_controller.detener_hello_protocol()
                input("\nPresione Enter para continuar...")

            elif opcion == '3':
                vecino_nombre = input("\nNombre del vecino: ").strip()
                if vecino_nombre:
                    if self.router_controller.enviar_hello_manual(vecino_nombre):
                        print(" HELLO enviado exitosamente")
                    else:
                        print(" Error al enviar HELLO")
                input("\nPresione Enter para continuar...")

            elif opcion == '4':
                vecinos = self.router_controller.listar_vecinos()
                if vecinos:
                    print("\nVecinos disponibles:")
                    for v in vecinos:
                        print(f"  ID {v.id_vecino}: {v.router_vecino} ({v.ip_vecino}) - {v.estado_vecino}")

                    try:
                        id_vecino = int(input("\nID del vecino: ").strip())
                        if self.router_controller.establecer_adyacencia(id_vecino):
                            print(" Adyacencia establecida")
                        else:
                            print(" Error al establecer adyacencia")
                    except ValueError:
                        print(" ID inválido")
                else:
                    print("\nNo hay vecinos registrados")

                input("\nPresione Enter para continuar...")

            elif opcion == '5':
                print("\n Verificando vecinos...")
                vecinos_caidos = self.router_controller.verificar_vecinos_caidos()

                if vecinos_caidos:
                    print(f"\n {len(vecinos_caidos)} vecinos caídos detectados:")
                    for v in vecinos_caidos:
                        print(f"  • {v.router_vecino} ({v.ip_vecino})")
                else:
                    print("\n Todos los vecinos están respondiendo")

                input("\nPresione Enter para continuar...")

            elif opcion == '6':
                print("\n" + "=" * 60)
                print("ESTADO DETALLADO DE VECINOS")
                print("=" * 60)

                for detalle in estado['detalles']:
                    print(f"\n{detalle['nombre']} ({detalle['ip']})")
                    print(f"  Estado: {detalle['estado']}")
                    print(f"  Tiempo sin HELLO: {detalle['tiempo_sin_hello']:.1f}s")

                input("\nPresione Enter para continuar...")

            elif opcion == '0':
                break

    def menu_estadisticas(self):
        """Submenú de estadísticas y monitoreo"""
        while True:
            self.limpiar_pantalla()
            self.mostrar_banner()
            print(" ESTADÍSTICAS Y MONITOREO")
            print("─" * 60)
            print("  1. Ver resumen completo del router")
            print("  2. Estadísticas de vecinos")
            print("  3. Estadísticas de rutas")
            print("  4. Identificar vecinos problemáticos")
            print("  5. Validar tabla de enrutamiento")
            print("  0. Volver")
            print("─" * 60)

            opcion = input("\n Seleccione una opción: ").strip()

            if opcion == '1':
                resumen = self.router_controller.obtener_resumen()
                print("\n" + "=" * 60)
                print("RESUMEN COMPLETO")
                print("=" * 60)
                print(f"\n{'Campo':<20} {'Valor'}")
                print("─" * 60)
                print(f"{'Nombre:':<20} {resumen['router_nombre']}")
                print(f"{'IP:':<20} {resumen['router_ip']}")
                print(f"{'Total Vecinos:':<20} {resumen['total_vecinos']}")
                print(f"{'Vecinos Activos:':<20} {resumen['vecinos_activos']}")
                print(f"{'Vecinos Inactivos:':<20} {resumen['vecinos_inactivos']}")
                print(f"{'Total Rutas:':<20} {resumen['total_rutas']}")
                print(f"{'Total Mensajes:':<20} {resumen['total_mensajes']}")
                print(f"{'HELLO Activo:':<20} {'Sí' if resumen['hello_activo'] else 'No'}")

                input("\nPresione Enter para continuar...")

            elif opcion == '2':
                from router.controller.vecino_controller import VecinoController
                vecino_ctrl = VecinoController()
                stats = vecino_ctrl.obtener_estadisticas_vecinos()

                print("\n" + "=" * 60)
                print("ESTADÍSTICAS DE VECINOS")
                print("=" * 60)
                print(f"\nTotal de vecinos:    {stats['total']}")
                print(f"  • Full:            {stats['full']}")
                print(f"  • 2-Way:           {stats['two_way']}")
                print(f"  • Down:            {stats['down']}")
                print(f"\nCosto promedio:      {stats['costo_promedio']:.2f}")
                print(f"Costo mínimo:        {stats['costo_minimo']:.2f}")
                print(f"Costo máximo:        {stats['costo_maximo']:.2f}")

                input("\nPresione Enter para continuar...")

            elif opcion == '3':
                from router.controller.enrutamiento_controller import EnrutamientoController
                ruta_ctrl = EnrutamientoController()
                stats = ruta_ctrl.obtener_estadisticas_rutas()

                print("\n" + "=" * 60)
                print("ESTADÍSTICAS DE RUTAS")
                print("=" * 60)
                print(f"\nTotal de rutas:      {stats['total']}")
                print(f"\nPor origen:")
                print(f"  • Interna:         {stats['por_origen']['Interna']}")
                print(f"  • Controlador:     {stats['por_origen']['Controlador']}")
                print(f"  • Externa:         {stats['por_origen']['Externa']}")
                print(f"\nCosto promedio:      {stats['costo_promedio']:.2f}")
                print(f"Costo mínimo:        {stats['costo_minimo']:.2f}")
                print(f"Costo máximo:        {stats['costo_maximo']:.2f}")

                input("\nPresione Enter para continuar...")

            elif opcion == '4':
                from router.controller.vecino_controller import VecinoController
                vecino_ctrl = VecinoController()
                problematicos = vecino_ctrl.obtener_vecinos_problematicos(30)

                print("\n" + "=" * 60)
                print("VECINOS PROBLEMÁTICOS")
                print("=" * 60)

                if problematicos:
                    for v in problematicos:
                        print(f"\n  • {v['nombre']} ({v['ip']})")
                        print(f"    Estado: {v['estado']}")
                        print(f"    Tiempo sin HELLO: {v['tiempo_sin_hello']:.1f}s")
                else:
                    print("\n✓ No se detectaron vecinos problemáticos")

                input("\nPresione Enter para continuar...")

            elif opcion == '5':
                from router.controller.enrutamiento_controller import EnrutamientoController
                ruta_ctrl = EnrutamientoController()
                validacion = ruta_ctrl.validar_tabla_enrutamiento()

                print("\n" + "=" * 60)
                print("VALIDACIÓN DE TABLA DE ENRUTAMIENTO")
                print("=" * 60)

                if validacion['valida']:
                    print("\n La tabla de enrutamiento es válida")
                else:
                    print("\n Se encontraron errores en la tabla")

                if validacion['errores']:
                    print("\n Errores:")
                    for error in validacion['errores']:
                        print(f"  • {error}")

                if validacion['advertencias']:
                    print("\n Advertencias:")
                    for adv in validacion['advertencias']:
                        print(f"  • {adv}")

                print(f"\nTotal de rutas analizadas: {validacion['total_rutas']}")

                input("\nPresione Enter para continuar...")

            elif opcion == '0':
                break

    def menu_logs(self):
        """Muestra los logs del router"""
        self.limpiar_pantalla()
        self.mostrar_banner()
        print(" LOGS DEL ROUTER (Últimos 20 eventos)")
        print("=" * 60)

        logs = self.router_controller.obtener_logs_recientes(20)

        if logs:
            for log in logs:
                print(f"\n[{log.fecha_hora}] {log.evento}")
                if log.detalle:
                    print(f"  → {log.detalle}")
        else:
            print("No hay logs registrados")

        input("\n\nPresione Enter para continuar...")

    def menu_controlador_sdn(self):
        """Submenú de conexión con controlador SDN"""
        while True:
            self.limpiar_pantalla()
            self.mostrar_banner()

            # Verificar estado de conexión
            conectado = self.router_controller.esta_conectado_a_controlador()
            estado_str = "Conectado" if conectado else "Desconectado"

            print(f" CONEXIÓN CON CONTROLADOR SDN - {estado_str}")
            print("─" * 60)
            print("  1. Conectar al controlador")
            print("  2. Desconectar del controlador")
            print("  3. Verificar estado de conexión")
            print("  4. Notificar vecinos al controlador")
            print("  5. Solicitar ruta al controlador")
            print("  0. Volver")
            print("─" * 60)

            opcion = input("\n Seleccione una opción: ").strip()

            if opcion == '1':
                if conectado:
                    print("\n Ya existe una conexión con el controlador")
                else:
                    host = input("\nHost del controlador (default: localhost): ").strip() or 'localhost'
                    try:
                        port = int(input("Puerto (default: 6633): ").strip() or "6633")
                    except ValueError:
                        port = 6633

                    print(f"\n Conectando a {host}:{port}...")
                    if self.router_controller.conectar_a_controlador(host, port):
                        print(" Conexión establecida exitosamente")
                    else:
                        print(" No se pudo establecer la conexión")

                input("\nPresione Enter para continuar...")

            elif opcion == '2':
                if not conectado:
                    print("\n No hay conexión activa")
                else:
                    confirmar = input("\n¿Desconectar del controlador? (s/n): ").strip().lower()
                    if confirmar == 's':
                        self.router_controller.desconectar_de_controlador()
                        print(" Desconectado del controlador")

                input("\nPresione Enter para continuar...")


            elif opcion == '3':
                print(f"\n{'Estado:':<20} {estado_str}")
                if conectado:
                    print(f"{'Servidor:':<20} Controlador SDN")
                    ssl_info = self.router_controller.tcp_client.get_ssl_info()
                    if ssl_info:
                        print(f"{'Cifrado:':<20} SSL/TLS Habilitado")
                        print(f"{'Versión TLS:':<20} {ssl_info.get('tls_version', 'N/A')}")
                        print(f"{'Algoritmo:':<20} {ssl_info.get('cipher_name', 'N/A')}")
                        print(f"{'Bits:':<20} {ssl_info.get('cipher_bits', 'N/A')}")
                    else:
                        print(f"{'Cifrado:':<20}  No disponible")
                input("\nPresione Enter para continuar...")

            elif opcion == '4':
                if not conectado:
                    print("\n No hay conexión con el controlador")
                else:
                    print("\n Notificando vecinos al controlador...")
                    if self.router_controller.notificar_vecinos_a_controlador():
                        print(" Vecinos notificados exitosamente")
                    else:
                        print(" Error al notificar vecinos")
                input("\nPresione Enter para continuar...")

            elif opcion == '5':
                if not conectado:
                    print("\n No hay conexión con el controlador")
                else:
                    destino_ip = input("\nIP de destino: ").strip()
                    if destino_ip:
                        print(f"\n Solicitando ruta a {destino_ip}...")
                        if self.router_controller.solicitar_ruta_a_controlador(destino_ip):
                            print(" Solicitud enviada. Esperando respuesta...")
                        else:
                            print(" Error al solicitar ruta")

                input("\nPresione Enter para continuar...")

            elif opcion == '0':
                break

    def menu_mantenimiento(self):
        """Menú de mantenimiento del router"""
        self.limpiar_pantalla()
        self.mostrar_banner()
        print(" MANTENIMIENTO DEL ROUTER")
        print("─" * 60)
        print("  1. Reconstruir tabla de enrutamiento")
        print("  2. Limpiar datos antiguos (7 días)")
        print("  3. Limpiar rutas por origen")
        print("  0. Volver")
        print("─" * 60)

        opcion = input("\n Seleccione una opción: ").strip()

        if opcion == '1':
            confirmar = input("\n Esto reconstruirá la tabla de enrutamiento. ¿Continuar? (s/n): ").strip().lower()
            if confirmar == 's':
                print("\n Reconstruyendo tabla de enrutamiento...")
                total = self.router_controller.reconstruir_tabla_enrutamiento()
                print(f"✓ {total} rutas creadas")
            input("\nPresione Enter para continuar...")

        elif opcion == '2':
            confirmar = input("\n ¿Está seguro de eliminar datos antiguos? (s/n): ").strip().lower()
            if confirmar == 's':
                self.router_controller.limpiar_datos_antiguos(7)
            input("\nPresione Enter para continuar...")

        elif opcion == '3':
            print("\nOrigen de rutas:")
            print("  1. Interna")
            print("  2. Controlador")
            print("  3. Externa")

            origen_opcion = input("\nSeleccione origen: ").strip()
            origen_map = {'1': 'Interna', '2': 'Controlador', '3': 'Externa'}

            if origen_opcion in origen_map:
                origen = origen_map[origen_opcion]
                confirmar = input(f"\n Eliminar todas las rutas de origen '{origen}'? (s/n): ").strip().lower()

                if confirmar == 's':
                    num = self.router_controller.limpiar_rutas_por_origen(origen)
                    print(f"✓ {num} rutas eliminadas")

            input("\nPresione Enter para continuar...")

    def ejecutar(self):
        """Ejecuta el menú principal"""
        while True:
            self.limpiar_pantalla()
            self.mostrar_banner()
            self.mostrar_resumen()
            self.mostrar_menu()

            opcion = input("\n Seleccione una opción: ").strip()

            if opcion == '1':
                self.menu_vecinos.ejecutar()

            elif opcion == '2':
                self.menu_enrutamiento.ejecutar()

            elif opcion == '3':
                self.menu_mensajes.ejecutar()

            elif opcion == '4':
                self.menu_ospf()

            elif opcion == '5':  # ← NUEVO
                self.menu_controlador_sdn()

            elif opcion == '6':
                self.menu_estadisticas()

            elif opcion == '7':
                self.menu_logs()

            elif opcion == '8':
                self.menu_mantenimiento()

            elif opcion == '0':
                # Desconectar del controlador si está conectado
                if self.router_controller.esta_conectado_a_controlador():
                    self.router_controller.desconectar_de_controlador()

                # Detener HELLO si está activo
                if self.router_controller.hello_protocol.esta_activo():
                    self.router_controller.detener_hello_protocol()

                print("\n¡Hasta luego! \n")
                break

            else:
                input("\n Opción inválida. Presione Enter para continuar...")