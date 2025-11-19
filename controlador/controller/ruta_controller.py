from controlador.dao.ruta_dao import RutaDAO
from controlador.dao.router_dao import RouterDAO
from controlador.services.network_graph import NetworkGraph

class RutaController:
    def __init__(self):
        self.ruta_dao = RutaDAO()
        self.router_dao = RouterDAO()
        self.network_graph = NetworkGraph()  # ← CAMBIADO

    def obtener_ruta_optima(self, origen, destino):
        """
        Obtiene la ruta óptima entre dos routers usando NetworkX

        Args:
            origen: ID del router origen
            destino: ID del router destino

        Returns:
            Diccionario con información de la ruta
        """
        camino, costo = self.network_graph.calcular_ruta(origen, destino)

        if camino is None:
            return None

        # Obtener información de los routers en el camino
        routers_en_camino = []
        for router_id in camino:
            router = self.router_dao.obtener_por_id(router_id)
            if router:
                routers_en_camino.append({
                    'id': router.id_router,
                    'nombre': router.nombre,
                    'ip': router.ip
                })

        return {
            'origen': origen,
            'destino': destino,
            'camino': camino,
            'camino_str': self.network_graph.formato_camino(camino),
            'costo_total': costo,
            'numero_saltos': len(camino) - 1,
            'routers': routers_en_camino
        }

    def obtener_rutas_alternativas(self, origen, destino, max_alternativas=3):
        """
        Busca rutas alternativas entre dos routers usando NetworkX

        Args:
            origen: ID del router origen
            destino: ID del router destino
            max_alternativas: Número máximo de rutas alternativas

        Returns:
            Lista de rutas alternativas
        """
        rutas_alt = self.network_graph.calcular_rutas_alternativas(origen, destino, max_alternativas)

        resultado = []
        for i, (camino, costo) in enumerate(rutas_alt, 1):
            # Obtener información de routers
            routers_en_camino = []
            for router_id in camino:
                router = self.router_dao.obtener_por_id(router_id)
                if router:
                    routers_en_camino.append({
                        'id': router.id_router,
                        'nombre': router.nombre,
                        'ip': router.ip
                    })

            resultado.append({
                'numero': i,
                'camino': camino,
                'camino_str': self.network_graph.formato_camino(camino),
                'costo_total': costo,
                'numero_saltos': len(camino) - 1,
                'routers': routers_en_camino
            })

        return resultado

    def comparar_rutas(self, origen, destino, metrica='costo'):
        """
        Compara diferentes rutas entre dos puntos según una métrica

        Args:
            origen: ID del router origen
            destino: ID del router destino
            metrica: Métrica a usar ('costo', 'saltos', etc.)

        Returns:
            Diccionario con comparación
        """
        ruta = self.obtener_ruta_optima(origen, destino)

        if not ruta:
            return None

        return {
            'ruta': ruta,
            'metricas': {
                'costo': ruta['costo_total'],
                'saltos': ruta['numero_saltos'],
                'eficiencia': ruta['costo_total'] / max(ruta['numero_saltos'], 1)
            }
        }

    def obtener_tabla_enrutamiento(self, id_router):
        """
        Genera la tabla de enrutamiento para un router específico

        Args:
            id_router: ID del router

        Returns:
            Lista con entradas de tabla de enrutamiento
        """
        rutas = self.ruta_dao.obtener_rutas_desde(id_router)

        tabla = []
        for ruta in rutas:
            # Obtener el siguiente salto (primer router después del origen)
            camino_list = ruta.obtener_saltos()

            if len(camino_list) > 1:
                siguiente_salto = camino_list[1]
                router_destino = self.router_dao.obtener_por_id(ruta.router_destino)
                router_salto = self.router_dao.obtener_por_id(siguiente_salto)

                if router_destino and router_salto:
                    tabla.append({
                        'destino': f"{router_destino.nombre} ({router_destino.ip})",
                        'next_hop': f"{router_salto.nombre} ({router_salto.ip})",
                        'costo': ruta.costo_total,
                        'saltos': ruta.numero_saltos()
                    })

        return tabla

    def analizar_congestion(self):
        """
        Analiza posibles puntos de congestión en la red usando NetworkX

        Returns:
            Lista de enlaces más utilizados
        """
        # Usar NetworkX para calcular betweenness de aristas
        edge_centrality = self.network_graph.analizar_congestion_enlaces()

        if not edge_centrality:
            return []

        # Obtener total de pares de rutas posibles
        self.network_graph.construir_grafo()
        num_nodos = self.network_graph.grafo.number_of_nodes()
        total_pares = num_nodos * (num_nodos - 1) if num_nodos > 1 else 1

        # Formatear resultado
        resultado = []
        for (r1, r2), centralidad in list(edge_centrality.items())[:10]:  # Top 10
            router1 = self.router_dao.obtener_por_id(r1)
            router2 = self.router_dao.obtener_por_id(r2)

            if router1 and router2:
                resultado.append({
                    'router1': router1.nombre,
                    'router2': router2.nombre,
                    'centralidad': centralidad,
                    'porcentaje': (centralidad * 100)
                })

        return resultado