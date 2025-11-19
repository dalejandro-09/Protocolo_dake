from datetime import datetime, timedelta
from controlador.dao.router_dao import RouterDAO
from controlador.dao.enlace_dao import EnlaceDAO
from controlador.dao.ruta_dao import RutaDAO
from controlador.dao.log_controlador_dao import LogControladorDAO

class NetworkMonitor:
    """Clase para monitorear el estado de la red"""

    def __init__(self):
        self.router_dao = RouterDAO()
        self.enlace_dao = EnlaceDAO()
        self.ruta_dao = RutaDAO()
        self.log_dao = LogControladorDAO()

    def obtener_resumen_red(self):
        """
        Obtiene un resumen del estado actual de la red

        Returns:
            Diccionario con estadísticas de la red
        """
        total_routers = self.router_dao.contar_routers()
        routers_activos = len(self.router_dao.obtener_activos())

        total_enlaces = self.enlace_dao.contar_enlaces()
        enlaces_activos = len(self.enlace_dao.obtener_activos())

        total_rutas = self.ruta_dao.contar_rutas()

        return {
            'total_routers': total_routers,
            'routers_activos': routers_activos,
            'routers_inactivos': total_routers - routers_activos,
            'total_enlaces': total_enlaces,
            'enlaces_activos': enlaces_activos,
            'enlaces_inactivos': total_enlaces - enlaces_activos,
            'total_rutas': total_rutas,
            'timestamp': datetime.now()
        }

    def obtener_estado_routers(self):
        """
        Obtiene el estado detallado de todos los routers

        Returns:
            Lista de diccionarios con información de cada router
        """
        routers = self.router_dao.obtener_todos()
        estado_routers = []

        for router in routers:
            # Contar enlaces del router
            enlaces = self.enlace_dao.obtener_por_router(router.id_router)
            enlaces_activos = sum(1 for e in enlaces if e.es_activo())

            estado_routers.append({
                'id': router.id_router,
                'nombre': router.nombre,
                'ip': router.ip,
                'estado': router.estado,
                'total_enlaces': len(enlaces),
                'enlaces_activos': enlaces_activos,
                'ultima_actualizacion': router.ultima_actualizacion
            })

        return estado_routers

    def obtener_estado_enlaces(self):
        """
        Obtiene el estado detallado de todos los enlaces

        Returns:
            Lista de diccionarios con información de cada enlace
        """
        enlaces = self.enlace_dao.obtener_todos()
        estado_enlaces = []

        for enlace in enlaces:
            # Obtener información de routers
            router_origen = self.router_dao.obtener_por_id(enlace.router_origen)
            router_destino = self.router_dao.obtener_por_id(enlace.router_destino)

            estado_enlaces.append({
                'id': enlace.id_enlace,
                'origen': router_origen.nombre if router_origen else f"R{enlace.router_origen}",
                'destino': router_destino.nombre if router_destino else f"R{enlace.router_destino}",
                'costo': enlace.costo,
                'ancho_banda': enlace.ancho_banda,
                'estado': enlace.estado,
                'retardo_ms': enlace.retardo_ms
            })

        return estado_enlaces

    def detectar_routers_problematicos(self, minutos=30):
        """
        Detecta routers que no se han actualizado recientemente

        Args:
            minutos: Tiempo sin actualización para considerar problemático

        Returns:
            Lista de routers problemáticos
        """
        routers = self.router_dao.obtener_activos()
        tiempo_limite = datetime.now() - timedelta(minutes=minutos)

        problematicos = []
        for router in routers:
            if router.ultima_actualizacion < tiempo_limite:
                problematicos.append({
                    'id': router.id_router,
                    'nombre': router.nombre,
                    'ip': router.ip,
                    'ultima_actualizacion': router.ultima_actualizacion,
                    'minutos_sin_actualizar': (datetime.now() - router.ultima_actualizacion).seconds // 60
                })

        return problematicos

    def obtener_metricas_rendimiento(self):
        """
        Calcula métricas de rendimiento de la red

        Returns:
            Diccionario con métricas
        """
        enlaces = self.enlace_dao.obtener_activos()

        if not enlaces:
            return {
                'costo_promedio': 0,
                'costo_minimo': 0,
                'costo_maximo': 0,
                'ancho_banda_promedio': 0,
                'retardo_promedio': 0
            }

        costos = [e.costo for e in enlaces]
        anchos_banda = [e.ancho_banda for e in enlaces if e.ancho_banda]
        retardos = [e.retardo_ms for e in enlaces if e.retardo_ms]

        return {
            'costo_promedio': sum(costos) / len(costos),
            'costo_minimo': min(costos),
            'costo_maximo': max(costos),
            'ancho_banda_promedio': sum(anchos_banda) / len(anchos_banda) if anchos_banda else 0,
            'retardo_promedio': sum(retardos) / len(retardos) if retardos else 0
        }

    def generar_reporte_red(self):
        """
        Genera un reporte completo del estado de la red

        Returns:
            Diccionario con reporte completo
        """
        return {
            'resumen': self.obtener_resumen_red(),
            'routers': self.obtener_estado_routers(),
            'enlaces': self.obtener_estado_enlaces(),
            'routers_problematicos': self.detectar_routers_problematicos(),
            'metricas': self.obtener_metricas_rendimiento()
        }

    def registrar_cambio_topologia(self, tipo_cambio, detalle):
        """
        Registra un cambio en la topología de la red

        Args:
            tipo_cambio: Tipo de cambio ('router_agregado', 'enlace_eliminado', etc.)
            detalle: Detalles del cambio
        """
        evento = f"Cambio topología: {tipo_cambio}"
        self.log_dao.registrar_evento(evento, detalle)