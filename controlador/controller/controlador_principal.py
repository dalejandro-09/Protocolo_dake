from datetime import datetime
from controlador.dao.router_dao import RouterDAO
from controlador.dao.enlace_dao import EnlaceDAO
from controlador.dao.ruta_dao import RutaDAO
from controlador.dao.log_controlador_dao import LogControladorDAO
from controlador.model.router import Router
from controlador.model.enlace import Enlace
from controlador.model.ruta import Ruta
from controlador.services.network_graph import NetworkGraph
from controlador.services.network_monitor import NetworkMonitor
from controlador.config.settings import ESTADOS_ROUTER, ESTADOS_ENLACE


class ControladorPrincipal:
    """Controlador principal del sistema SDN"""

    def __init__(self):
        self.router_dao = RouterDAO()
        self.enlace_dao = EnlaceDAO()
        self.ruta_dao = RutaDAO()
        self.log_dao = LogControladorDAO()
        self.network_graph = NetworkGraph()
        self.monitor = NetworkMonitor()

        self.tcp_server = None


        self.log_dao.registrar_evento(
            "Controlador iniciado",
            "Sistema SDN iniciado correctamente"
        )

    # ==================== GESTIÓN DE ROUTERS ====================

    def crear_router(self, nombre, ip, estado='Activo'):
        """
        Crea un nuevo router en la red

        Args:
            nombre: Nombre del router
            ip: Dirección IP del router
            estado: Estado inicial del router

        Returns:
            ID del router creado o None si falla
        """
        # Validar estado
        if estado not in ESTADOS_ROUTER:
            print(f"✗ Estado inválido. Debe ser uno de: {ESTADOS_ROUTER}")
            return None

        # Verificar si la IP ya existe
        if self.router_dao.existe_ip(ip):
            print(f"✗ La IP {ip} ya está en uso")
            return None

        # Crear router
        router = Router(nombre=nombre, ip=ip, estado=estado)
        router_id = self.router_dao.crear(router)

        if router_id:
            self.log_dao.registrar_evento(
                "Router creado",
                f"Router '{nombre}' creado con IP {ip}"
            )
            self.monitor.registrar_cambio_topologia(
                "router_agregado",
                f"ID: {router_id}, Nombre: {nombre}"
            )

        return router_id

    def obtener_router(self, id_router):
        """Obtiene un router por su ID"""
        return self.router_dao.obtener_por_id(id_router)

    def listar_routers(self, solo_activos=False):
        """
        Lista todos los routers

        Args:
            solo_activos: Si True, solo lista routers activos

        Returns:
            Lista de routers
        """
        if solo_activos:
            return self.router_dao.obtener_activos()
        return self.router_dao.obtener_todos()

    def actualizar_router(self, id_router, nombre=None, ip=None, estado=None):
        """
        Actualiza los datos de un router

        Args:
            id_router: ID del router
            nombre: Nuevo nombre (opcional)
            ip: Nueva IP (opcional)
            estado: Nuevo estado (opcional)

        Returns:
            True si la actualización fue exitosa
        """
        router = self.router_dao.obtener_por_id(id_router)
        if not router:
            print(f"✗ Router ID {id_router} no encontrado")
            return False

        # Actualizar campos si se proporcionan
        if nombre:
            router.nombre = nombre
        if ip:
            # Verificar que la IP no esté en uso por otro router
            if self.router_dao.existe_ip(ip, excluir_id=id_router):
                print(f"✗ La IP {ip} ya está en uso")
                return False
            router.ip = ip
        if estado:
            if estado not in ESTADOS_ROUTER:
                print(f"✗ Estado inválido. Debe ser uno de: {ESTADOS_ROUTER}")
                return False
            router.estado = estado

        router.ultima_actualizacion = datetime.now()

        if self.router_dao.actualizar(router):
            self.log_dao.registrar_evento(
                "Router actualizado",
                f"Router ID {id_router} actualizado"
            )
            return True
        return False

    def cambiar_estado_router(self, id_router, nuevo_estado):
        """
        Cambia el estado de un router

        Args:
            id_router: ID del router
            nuevo_estado: Nuevo estado

        Returns:
            True si el cambio fue exitoso
        """
        if nuevo_estado not in ESTADOS_ROUTER:
            print(f"✗ Estado inválido. Debe ser uno de: {ESTADOS_ROUTER}")
            return False

        if self.router_dao.cambiar_estado(id_router, nuevo_estado):
            self.log_dao.registrar_evento(
                "Estado de router cambiado",
                f"Router ID {id_router} cambió a estado '{nuevo_estado}'"
            )

            # Si el router se desactiva, recalcular rutas
            if nuevo_estado != 'Activo':
                self.recalcular_todas_rutas()

            return True
        return False

    def eliminar_router(self, id_router):
        """
        Elimina un router de la red

        Args:
            id_router: ID del router a eliminar

        Returns:
            True si la eliminación fue exitosa
        """
        router = self.router_dao.obtener_por_id(id_router)
        if not router:
            print(f"✗ Router ID {id_router} no encontrado")
            return False

        nombre = router.nombre

        # Eliminar rutas asociadas
        self.ruta_dao.eliminar_rutas_router(id_router)

        # Eliminar router (los enlaces se eliminan por CASCADE)
        if self.router_dao.eliminar(id_router):
            self.log_dao.registrar_evento(
                "Router eliminado",
                f"Router '{nombre}' (ID: {id_router}) eliminado"
            )
            self.monitor.registrar_cambio_topologia(
                "router_eliminado",
                f"ID: {id_router}, Nombre: {nombre}"
            )

            # Recalcular rutas
            self.recalcular_todas_rutas()
            return True
        return False

    # ==================== GESTIÓN DE ENLACES ====================

    def crear_enlace(self, router_origen, router_destino, costo=1.0,
                     ancho_banda=None, estado='Activo', retardo_ms=None):
        """
        Crea un nuevo enlace entre dos routers

        Args:
            router_origen: ID del router origen
            router_destino: ID del router destino
            costo: Costo del enlace
            ancho_banda: Ancho de banda (opcional)
            estado: Estado del enlace
            retardo_ms: Retardo en milisegundos (opcional)

        Returns:
            ID del enlace creado o None si falla
        """
        # Validar que los routers existan
        if not self.router_dao.obtener_por_id(router_origen):
            print(f"✗ Router origen ID {router_origen} no existe")
            return None

        if not self.router_dao.obtener_por_id(router_destino):
            print(f"✗ Router destino ID {router_destino} no existe")
            return None

        # Validar que no sean el mismo router
        if router_origen == router_destino:
            print("✗ No se puede crear un enlace de un router a sí mismo")
            return None

        # Validar estado
        if estado not in ESTADOS_ENLACE:
            print(f"✗ Estado inválido. Debe ser uno de: {ESTADOS_ENLACE}")
            return None

        # Verificar si ya existe el enlace
        if self.enlace_dao.existe_enlace(router_origen, router_destino):
            print(f"✗ Ya existe un enlace entre R{router_origen} y R{router_destino}")
            return None

        # Crear enlace
        enlace = Enlace(
            router_origen=router_origen,
            router_destino=router_destino,
            costo=costo,
            ancho_banda=ancho_banda,
            estado=estado,
            retardo_ms=retardo_ms
        )

        enlace_id = self.enlace_dao.crear(enlace)

        if enlace_id:
            self.log_dao.registrar_evento(
                "Enlace creado",
                f"Enlace entre R{router_origen} y R{router_destino} creado"
            )
            self.monitor.registrar_cambio_topologia(
                "enlace_agregado",
                f"ID: {enlace_id}, R{router_origen} <-> R{router_destino}"
            )

            # Recalcular rutas afectadas
            self.recalcular_rutas_router(router_origen)
            self.recalcular_rutas_router(router_destino)

        return enlace_id

    def obtener_enlace(self, id_enlace):
        return self.enlace_dao.obtener_por_id(id_enlace)

    def listar_enlaces(self, solo_activos=False):

        if solo_activos:
            return self.enlace_dao.obtener_activos()
        return self.enlace_dao.obtener_todos()

    def obtener_enlaces_router(self, id_router):
        """Obtiene todos los enlaces de un router"""
        return self.enlace_dao.obtener_por_router(id_router)

    def actualizar_enlace(self, id_enlace, costo=None, ancho_banda=None,
                          estado=None, retardo_ms=None):
        enlace = self.enlace_dao.obtener_por_id(id_enlace)
        if not enlace:
            print(f"✗ Enlace ID {id_enlace} no encontrado")
            return False

        # Actualizar campos si se proporcionan
        if costo is not None:
            enlace.costo = costo
        if ancho_banda is not None:
            enlace.ancho_banda = ancho_banda
        if estado is not None:
            if estado not in ESTADOS_ENLACE:
                print(f"✗ Estado inválido. Debe ser uno de: {ESTADOS_ENLACE}")
                return False
            enlace.estado = estado
        if retardo_ms is not None:
            enlace.retardo_ms = retardo_ms

        if self.enlace_dao.actualizar(enlace):
            self.log_dao.registrar_evento(
                "Enlace actualizado",
                f"Enlace ID {id_enlace} actualizado"
            )

            # Recalcular rutas si cambió el costo o estado
            if costo is not None or estado is not None:
                self.recalcular_rutas_router(enlace.router_origen)
                self.recalcular_rutas_router(enlace.router_destino)

            return True
        return False

    def cambiar_estado_enlace(self, id_enlace, nuevo_estado):
        if nuevo_estado not in ESTADOS_ENLACE:
            print(f"✗ Estado inválido. Debe ser uno de: {ESTADOS_ENLACE}")
            return False

        enlace = self.enlace_dao.obtener_por_id(id_enlace)
        if not enlace:
            return False

        if self.enlace_dao.cambiar_estado(id_enlace, nuevo_estado):
            self.log_dao.registrar_evento(
                "Estado de enlace cambiado",
                f"Enlace ID {id_enlace} cambió a estado '{nuevo_estado}'"
            )

            # Recalcular rutas
            self.recalcular_rutas_router(enlace.router_origen)
            self.recalcular_rutas_router(enlace.router_destino)

            return True
        return False

    def eliminar_enlace(self, id_enlace):
        enlace = self.enlace_dao.obtener_por_id(id_enlace)
        if not enlace:
            print(f"✗ Enlace ID {id_enlace} no encontrado")
            return False

        router_origen = enlace.router_origen
        router_destino = enlace.router_destino

        if self.enlace_dao.eliminar(id_enlace):
            self.log_dao.registrar_evento(
                "Enlace eliminado",
                f"Enlace ID {id_enlace} eliminado"
            )
            self.monitor.registrar_cambio_topologia(
                "enlace_eliminado",
                f"ID: {id_enlace}"
            )

            # Recalcular rutas
            self.recalcular_rutas_router(router_origen)
            self.recalcular_rutas_router(router_destino)

            return True
        return False

    # ==================== GESTIÓN DE RUTAS ====================

    def calcular_ruta(self, origen, destino, guardar=True):
        # Calcular ruta usando NetworkX
        camino, costo_total = self.network_graph.calcular_ruta(origen, destino)

        if camino is None:
            print(f"✗ No existe ruta entre R{origen} y R{destino}")
            return None

        # Crear objeto Ruta
        camino_str = self.network_graph.formato_camino(camino)
        ruta = Ruta(
            router_origen=origen,
            router_destino=destino,
            camino=camino_str,
            costo_total=costo_total
        )

        # Guardar en BD si se solicita
        if guardar:
            ruta_id = self.ruta_dao.crear(ruta)
            if ruta_id:
                ruta.id_ruta = ruta_id
                self.log_dao.registrar_evento(
                    "Ruta calculada",
                    f"Ruta de R{origen} a R{destino}: {camino_str} (Costo: {costo_total})"
                )

        return ruta

    def obtener_ruta(self, origen, destino):
        return self.ruta_dao.obtener_por_origen_destino(origen, destino)

    def listar_rutas(self):
        return self.ruta_dao.obtener_todas()

    def listar_rutas_desde(self, origen):
        return self.ruta_dao.obtener_rutas_desde(origen)

    def listar_rutas_hacia(self, destino):
        return self.ruta_dao.obtener_rutas_hacia(destino)

    def calcular_rutas_alternativas(self, origen, destino, k=3):
        return self.network_graph.calcular_rutas_alternativas(origen, destino, k)

    def recalcular_rutas_router(self, id_router):
        # Eliminar rutas antiguas del router
        self.ruta_dao.eliminar_rutas_router(id_router)

        # Calcular nuevas rutas desde este router a todos los demás
        rutas_calculadas = self.network_graph.calcular_todas_las_rutas(id_router)

        contador = 0
        for destino, (camino, costo) in rutas_calculadas.items():
            if camino:
                camino_str = self.network_graph.formato_camino(camino)
                ruta = Ruta(
                    router_origen=id_router,
                    router_destino=destino,
                    camino=camino_str,
                    costo_total=costo
                )
                if self.ruta_dao.crear(ruta):
                    contador += 1

        print(f"✓ {contador} rutas recalculadas para router R{id_router}")
        return contador

    def recalcular_todas_rutas(self):
        print(" Recalculando todas las rutas de la red...")

        # Obtener todos los routers activos
        routers = self.router_dao.obtener_activos()

        if len(routers) < 2:
            print("No hay suficientes routers activos para calcular rutas")
            return 0

        # Limpiar todas las rutas existentes
        for router in routers:
            self.ruta_dao.eliminar_rutas_router(router.id_router)

        # Calcular rutas para cada router
        total_rutas = 0
        for router in routers:
            rutas_calculadas = self.network_graph.calcular_todas_las_rutas(router.id_router)

            for destino, (camino, costo) in rutas_calculadas.items():
                if camino:
                    camino_str = self.network_graph.formato_camino(camino)
                    ruta = Ruta(
                        router_origen=router.id_router,
                        router_destino=destino,
                        camino=camino_str,
                        costo_total=costo
                    )
                    if self.ruta_dao.crear(ruta):
                        total_rutas += 1

        self.log_dao.registrar_evento(
            "Rutas recalculadas",
            f"Se calcularon {total_rutas} rutas en la red"
        )

        print(f"✓ {total_rutas} rutas calculadas exitosamente")
        return total_rutas

    # ==================== ANÁLISIS Y MONITOREO ====================

    def verificar_conectividad(self):
        conectividad = self.network_graph.verificar_conectividad()

        if conectividad['conectada']:
            print("✓ La red está completamente conectada")
        else:
            print(f" La red tiene {conectividad['componentes']} componentes desconectadas")
            if conectividad['routers_aislados']:
                print(f"  Routers aislados: {conectividad['routers_aislados']}")

        return conectividad

    def identificar_routers_criticos(self):

        return self.network_graph.encontrar_routers_criticos()

    def identificar_enlaces_criticos(self):
        return self.network_graph.encontrar_enlaces_criticos()

    def obtener_estadisticas_grafo(self):
        return self.network_graph.obtener_estadisticas_grafo()

    def calcular_centralidad_routers(self):
        return self.network_graph.calcular_centralidad()

    def visualizar_topologia(self, guardar=False, archivo="topologia.png"):
        self.network_graph.visualizar_topologia(
            guardar_archivo=archivo if guardar else None,
            mostrar=True
        )

    def visualizar_ruta(self, origen, destino, guardar=False, archivo="ruta.png"):
        self.network_graph.visualizar_ruta(
            origen, destino,
            guardar_archivo=archivo if guardar else None,
            mostrar=True
        )

    # ==================== ANÁLISIS Y MONITOREO ====================
    def obtener_resumen_red(self):
        """Obtiene un resumen del estado de la red"""
        return self.monitor.obtener_resumen_red()

    def generar_reporte(self):
        """Genera un reporte completo de la red"""
        return self.monitor.generar_reporte_red()

    def obtener_metricas(self):
        """Obtiene métricas de rendimiento de la red"""
        return self.monitor.obtener_metricas_rendimiento()

    def detectar_problemas(self):
        """Detecta routers con problemas"""
        return self.monitor.detectar_routers_problematicos()

    # ==================== LOGS ====================

    def obtener_logs_recientes(self, limite=20):
        """Obtiene los logs más recientes"""
        return self.log_dao.obtener_todos(limite)

    def obtener_logs_por_evento(self, evento, limite=20):
        """Obtiene logs de un tipo de evento específico"""
        return self.log_dao.obtener_por_evento(evento, limite)

    def limpiar_datos_antiguos(self, dias=30):

        logs_eliminados = self.log_dao.limpiar_logs_antiguos(dias)
        rutas_eliminadas = self.ruta_dao.limpiar_rutas_antiguas(dias)

        print(f"✓ Limpieza completada: {logs_eliminados} logs y {rutas_eliminadas} rutas eliminadas")

        self.log_dao.registrar_evento(
            "Limpieza de datos",
            f"Eliminados {logs_eliminados} logs y {rutas_eliminadas} rutas antiguas"
        )

    # ==================== SERVIDOR TCP ====================

    def iniciar_servidor_tcp(self, host='0.0.0.0', port=6633):
        from shared.communication.tcp_server import TCPServer

        if self.tcp_server and self.tcp_server.running:
            print(" El servidor TCP ya está en ejecución")
            return False

        self.tcp_server = TCPServer(host=host, port=port, controlador=self)

        if self.tcp_server.start():
            self.log_dao.registrar_evento(
                "Servidor TCP iniciado",
                f"Servidor escuchando en {host}:{port}"
            )
            return True
        return False

    def detener_servidor_tcp(self):
        """Detiene el servidor TCP"""
        if self.tcp_server:
            self.tcp_server.stop()
            self.log_dao.registrar_evento(
                "Servidor TCP detenido",
                "Servidor TCP cerrado correctamente"
            )

    def obtener_routers_conectados(self):
        if self.tcp_server:
            return self.tcp_server.get_connected_routers()
        return []

    def broadcast_rutas_actualizadas(self):
        if not self.tcp_server:
            return

        routers_conectados = self.obtener_routers_conectados()
        rutas_por_router = {}

        for router_nombre in routers_conectados:
            router = self.obtener_router_por_nombre(router_nombre)
            if router:
                rutas = self.listar_rutas_desde(router.id_router)

                rutas_data = []
                for ruta in rutas:
                    router_destino = self.obtener_router(ruta.router_destino)
                    if router_destino:
                        camino = ruta.obtener_saltos()
                        next_hop_id = camino[1] if len(camino) > 1 else None

                        if next_hop_id:
                            next_hop_router = self.obtener_router(next_hop_id)

                            rutas_data.append({
                                'destino': router_destino.ip,
                                'next_hop': next_hop_router.ip if next_hop_router else None,
                                'interfaz_salida': f"eth_to_R{next_hop_id}",
                                'costo': ruta.costo_total,
                                'origen_info': 'Controlador'
                            })

                rutas_por_router[router_nombre] = rutas_data

        self.tcp_server.broadcast_route_update(rutas_por_router)
        print(f"✓ Rutas actualizadas enviadas a {len(rutas_por_router)} routers")

    def obtener_router_por_nombre(self, nombre):
        return self.router_dao.obtener_por_nombre(nombre)

    def obtener_router_por_ip(self, ip):
        return self.router_dao.obtener_por_ip(ip)

    def cambiar_estado_router_por_nombre(self, nombre, nuevo_estado):
        router = self.obtener_router_por_nombre(nombre)
        if router:
            return self.cambiar_estado_router(router.id_router, nuevo_estado)
        return False