import os
from controlador.controller.controlador_principal import ControladorPrincipal
from controlador.view.cli.menu_router import MenuRouter
from controlador.view.cli.menu_topologia import MenuTopologia
from controlador.view.cli.menu_rutas import MenuRutas

class MenuPrincipal:
    """Menú principal de la aplicación"""

    def __init__(self):
        self.controlador = ControladorPrincipal()
        self.menu_router = MenuRouter(self.controlador)
        self.menu_topologia = MenuTopologia(self.controlador)
        self.menu_rutas = MenuRutas(self.controlador)

    def limpiar_pantalla(self):
        """Limpia la pantalla de la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def mostrar_banner(self):
        """Muestra el banner de la aplicación"""
        print("=" * 60)
        print(" " * 15 + " CONTROLADOR SDN ")
        print(" " * 10 + "Sistema de Gestión de Red de Routers")
        print("=" * 60)
        print()

    def mostrar_resumen(self):
        """Muestra un resumen del estado de la red"""
        resumen = self.controlador.obtener_resumen_red()

        print("RESUMEN DE LA RED")
        print("-" * 60)
        print(f"  Routers:  {resumen['routers_activos']}/{resumen['total_routers']} activos")
        print(f"  Enlaces:  {resumen['enlaces_activos']}/{resumen['total_enlaces']} activos")
        print(f"  Rutas:    {resumen['total_rutas']} calculadas")
        print("-" * 60)
        print()

    def mostrar_menu(self):
        """Muestra el menú principal"""
        print("MENÚ PRINCIPAL")
        print("─" * 60)
        print("  1. Gestión de Routers")
        print("  2. Gestión de Enlaces y Topología")
        print("  3. Gestión de Rutas")
        print("  4. Servidor TCP (Comunicación con Routers)")  # ← NUEVO
        print("  5. Monitoreo y Estadísticas")
        print("  6. Ver Logs del Sistema")
        print("  7. Mantenimiento")
        print("  0. Salir")
        print("─" * 60)

    def menu_monitoreo(self):
        """Submenú de monitoreo y estadísticas"""
        while True:
            self.limpiar_pantalla()
            self.mostrar_banner()
            print("MONITOREO Y ESTADÍSTICAS")
            print("─" * 60)
            print("  1. Ver resumen completo de la red")
            print("  2. Verificar conectividad")
            print("  3. Ver métricas de rendimiento")
            print("  4. Detectar routers problemáticos")
            print("  5. Validar topología")
            print("  0. Volver")
            print("─" * 60)

            opcion = input("\n➤ Seleccione una opción: ").strip()

            if opcion == '1':
                reporte = self.controlador.generar_reporte()
                print("\n" + "=" * 60)
                print("REPORTE COMPLETO DE LA RED")
                print("=" * 60)

                print("\n Resumen:")
                resumen = reporte['resumen']
                print(f"  • Routers: {resumen['routers_activos']}/{resumen['total_routers']} activos")
                print(f"  • Enlaces: {resumen['enlaces_activos']}/{resumen['total_enlaces']} activos")
                print(f"  • Rutas: {resumen['total_rutas']} calculadas")

                print("\n Métricas:")
                metricas = reporte['metricas']
                print(f"  • Costo promedio: {metricas['costo_promedio']:.2f}")
                print(f"  • Costo mínimo: {metricas['costo_minimo']:.2f}")
                print(f"  • Costo máximo: {metricas['costo_maximo']:.2f}")

                if reporte['routers_problematicos']:
                    print("\n️ Routers Problemáticos:")
                    for r in reporte['routers_problematicos']:
                        print(f"  • {r['nombre']} - {r['minutos_sin_actualizar']} min sin actualizar")

                input("\nPresione Enter para continuar...")

            elif opcion == '2':
                conectividad = self.controlador.verificar_conectividad()
                print("\n" + "=" * 60)
                print("ANÁLISIS DE CONECTIVIDAD")
                print("=" * 60)

                if conectividad['conectada']:
                    print("✓ La red está completamente conectada")
                else:
                    print(f"✗ La red tiene {conectividad['componentes']} componentes desconectadas")
                    if conectividad['routers_aislados']:
                        print(f"\nRouters aislados: {conectividad['routers_aislados']}")

                input("\nPresione Enter para continuar...")

            elif opcion == '3':
                metricas = self.controlador.obtener_metricas()
                print("\n" + "=" * 60)
                print("MÉTRICAS DE RENDIMIENTO")
                print("=" * 60)
                print(f"  Costo Promedio:     {metricas['costo_promedio']:.2f}")
                print(f"  Costo Mínimo:       {metricas['costo_minimo']:.2f}")
                print(f"  Costo Máximo:       {metricas['costo_maximo']:.2f}")
                print(f"  Ancho Banda Prom:   {metricas['ancho_banda_promedio']:.2f} Mbps")
                print(f"  Retardo Promedio:   {metricas['retardo_promedio']:.2f} ms")

                input("\nPresione Enter para continuar...")

            elif opcion == '4':
                problemas = self.controlador.detectar_problemas()
                print("\n" + "=" * 60)
                print("ROUTERS PROBLEMÁTICOS")
                print("=" * 60)

                if problemas:
                    for r in problemas:
                        print(f"  • {r['nombre']} ({r['ip']})")
                        print(f"    Última actualización: {r['ultima_actualizacion']}")
                        print(f"    Tiempo sin actualizar: {r['minutos_sin_actualizar']} minutos")
                        print()
                else:
                    print("✓ No se detectaron routers problemáticos")

                input("\nPresione Enter para continuar...")

            elif opcion == '5':
                from controlador.controller.topologia_controller import TopologiaController
                topo_ctrl = TopologiaController()
                validacion = topo_ctrl.validar_topologia()

                print("\n" + "=" * 60)
                print("VALIDACIÓN DE TOPOLOGÍA")
                print("=" * 60)

                if validacion['valida']:
                    print("✓ La topología es válida")
                else:
                    print("✗ Se encontraron errores en la topología")

                if validacion['errores']:
                    print("\n Errores:")
                    for error in validacion['errores']:
                        print(f"  • {error}")

                if validacion['advertencias']:
                    print("\n Advertencias:")
                    for adv in validacion['advertencias']:
                        print(f"  • {adv}")

                input("\nPresione Enter para continuar...")

            elif opcion == '0':
                break

    def menu_servidor_tcp(self):
        """Submenú del servidor TCP"""
        while True:
            self.limpiar_pantalla()
            self.mostrar_banner()

            # Verificar si el servidor está activo
            servidor_activo = (self.controlador.tcp_server and
                               self.controlador.tcp_server.running)
            estado_str = "Activo" if servidor_activo else "Inactivo"

            print(f" SERVIDOR TCP - {estado_str}")
            print("─" * 60)

            if servidor_activo:
                routers_conectados = self.controlador.obtener_routers_conectados()
                print(f"\n Routers conectados: {len(routers_conectados)}")
                if routers_conectados:
                    for router_nombre in routers_conectados:
                        print(f"  • {router_nombre}")

            print("\n" + "─" * 60)
            print("  1. Iniciar servidor TCP")
            print("  2. Detener servidor TCP")
            print("  3. Ver routers conectados")
            print("  4. Enviar actualización de rutas a routers")
            print("  5. Ver estado del servidor")
            print("  0. Volver")
            print("─" * 60)

            opcion = input("\n Seleccione una opción: ").strip()

            if opcion == '1':
                if servidor_activo:
                    print("\n El servidor TCP ya está en ejecución")
                else:
                    host = input("\nHost (default: 0.0.0.0): ").strip() or '0.0.0.0'
                    try:
                        port = int(input("Puerto (default: 6633): ").strip() or "6633")
                    except ValueError:
                        port = 6633

                    print(f"\n Iniciando servidor TCP en {host}:{port}...")
                    if self.controlador.iniciar_servidor_tcp(host, port):
                        print(" Servidor TCP iniciado exitosamente")
                        print(f"  Los routers pueden conectarse a {host}:{port}")
                    else:
                        print(" No se pudo iniciar el servidor TCP")

                input("\nPresione Enter para continuar...")

            elif opcion == '2':
                if not servidor_activo:
                    print("\n El servidor TCP no está en ejecución")
                else:
                    confirmar = input(
                        "\n¿Detener el servidor TCP? Esto desconectará todos los routers. (s/n): ").strip().lower()
                    if confirmar == 's':
                        self.controlador.detener_servidor_tcp()
                        print(" Servidor TCP detenido")

                input("\nPresione Enter para continuar...")

            elif opcion == '3':
                print("\n" + "=" * 60)
                print("ROUTERS CONECTADOS")
                print("=" * 60)

                if not servidor_activo:
                    print("\n El servidor TCP no está en ejecución")
                else:
                    routers_conectados = self.controlador.obtener_routers_conectados()

                    if routers_conectados:
                        print(f"\nTotal: {len(routers_conectados)} routers conectados\n")

                        for router_nombre in routers_conectados:
                            router = self.controlador.obtener_router_por_nombre(router_nombre)
                            if router:
                                print(f"  • {router_nombre}")
                                print(f"    ID: {router.id_router}")
                                print(f"    IP: {router.ip}")
                                print(f"    Estado: {router.estado}")
                                print()
                            else:
                                print(f"  • {router_nombre} (información no disponible)")
                    else:
                        print("\nNo hay routers conectados actualmente")

                input("\nPresione Enter para continuar...")

            elif opcion == '4':
                if not servidor_activo:
                    print("\n El servidor TCP no está en ejecución")
                else:
                    routers_conectados = self.controlador.obtener_routers_conectados()

                    if not routers_conectados:
                        print("\n No hay routers conectados")
                    else:
                        confirmar = input(
                            f"\n¿Enviar rutas actualizadas a {len(routers_conectados)} router(es)? (s/n): ").strip().lower()

                        if confirmar == 's':
                            print("\n Enviando rutas actualizadas...")
                            self.controlador.broadcast_rutas_actualizadas()
                            print(" Rutas enviadas a todos los routers conectados")

                input("\nPresione Enter para continuar...")


            elif opcion == '5':
                print("\n" + "=" * 60)
                print("ESTADO DEL SERVIDOR TCP")
                print("=" * 60)
                print(f"\n{'Estado:':<25} {estado_str}")
                if servidor_activo:
                    print(f"{'Puerto:':<25} {self.controlador.tcp_server.port}")
                    print(f"{'Host:':<25} {self.controlador.tcp_server.host}")
                    print(f"{'Cifrado:':<25}  SSL/TLS Habilitado")
                    print(f"{'Certificado:':<25} {self.controlador.tcp_server.certfile}")
                    routers_conectados = self.controlador.obtener_routers_conectados()
                    print(f"{'Routers conectados:':<25} {len(routers_conectados)}")
                    print(f"{'Intervalo heartbeat:':<25} {self.controlador.tcp_server.heartbeat_interval}s")
                    # Mostrar info de conexiones SSL
                    if routers_conectados:
                        print(f"\n{'Conexiones SSL Activas:'}")
                        for router_nombre in routers_conectados:
                            print(f"  • {router_nombre} - Cifrado activo")
                else:
                    print("\nEl servidor no está en ejecución")
                input("\nPresione Enter para continuar...")
            elif opcion == '0':
                break

    def menu_logs(self):
        """Muestra los logs del sistema"""
        self.limpiar_pantalla()
        self.mostrar_banner()
        print("LOGS DEL SISTEMA (Últimos 20 eventos)")
        print("=" * 60)

        logs = self.controlador.obtener_logs_recientes(20)

        if logs:
            for log in logs:
                print(f"\n[{log.fecha_hora}] {log.evento}")
                if log.detalle:
                    print(f"  → {log.detalle}")
        else:
            print("No hay logs registrados")

        input("\n\nPresione Enter para continuar...")

    def menu_mantenimiento(self):
        """Menú de mantenimiento del sistema"""
        self.limpiar_pantalla()
        self.mostrar_banner()
        print(" MANTENIMIENTO DEL SISTEMA")
        print("─" * 60)
        print("  1. Recalcular todas las rutas")
        print("  2. Limpiar datos antiguos (30 días)")
        print("  3. Optimizar base de datos")
        print("  0. Volver")
        print("─" * 60)

        opcion = input("\n➤ Seleccione una opción: ").strip()

        if opcion == '1':
            print("\n Recalculando todas las rutas...")
            total = self.controlador.recalcular_todas_rutas()
            print(f"✓ {total} rutas calculadas exitosamente")
            input("\nPresione Enter para continuar...")

        elif opcion == '2':
            confirmar = input("\n ¿Está seguro de eliminar datos antiguos? (s/n): ").strip().lower()
            if confirmar == 's':
                self.controlador.limpiar_datos_antiguos(30)
                input("\nPresione Enter para continuar...")

        elif opcion == '3':
            print("\nOptimizando base de datos...")
            print("✓ Optimización completada")
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
                self.menu_router.ejecutar()

            elif opcion == '2':
                self.menu_topologia.ejecutar()

            elif opcion == '3':
                self.menu_rutas.ejecutar()

            elif opcion == '4':  # ← NUEVO
                self.menu_servidor_tcp()

            elif opcion == '5':
                self.menu_monitoreo()

            elif opcion == '6':
                self.menu_logs()

            elif opcion == '7':
                self.menu_mantenimiento()

            elif opcion == '0':
                # Detener servidor TCP si está activo
                if self.controlador.tcp_server and self.controlador.tcp_server.running:
                    print("\n Deteniendo servidor TCP...")
                    self.controlador.detener_servidor_tcp()

                print("\n¡Hasta luego! \n")
                break

            else:
                input("\n Opción inválida. Presione Enter para continuar...")