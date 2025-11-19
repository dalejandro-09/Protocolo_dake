from controlador.dao.router_dao import RouterDAO
from controlador.dao.enlace_dao import EnlaceDAO
from controlador.services.network_graph import NetworkGraph

class TopologiaController:
    def __init__(self):
        self.router_dao = RouterDAO()
        self.enlace_dao = EnlaceDAO()
        self.network_graph = NetworkGraph()  # ← CAMBIADO

    def obtener_topologia_completa(self):
        routers = self.router_dao.obtener_todos()
        enlaces = self.enlace_dao.obtener_todos()

        return {
            'routers': [r.to_dict() for r in routers],
            'enlaces': [e.to_dict() for e in enlaces]
        }

    def obtener_vecinos_router(self, id_router):
        vecinos_data = self.enlace_dao.obtener_vecinos(id_router)

        vecinos = []
        for vecino_id, costo, enlace_id in vecinos_data:
            router_vecino = self.router_dao.obtener_por_id(vecino_id)
            if router_vecino:
                vecinos.append({
                    'id': vecino_id,
                    'nombre': router_vecino.nombre,
                    'ip': router_vecino.ip,
                    'costo': costo,
                    'enlace_id': enlace_id
                })

        return vecinos

    def obtener_matriz_adyacencia(self):
        """
        Genera la matriz de adyacencia de la red usando NetworkX

        Returns:
            Diccionario con la matriz
        """
        self.network_graph.construir_grafo()
        grafo = self.network_graph.grafo

        router_ids = list(grafo.nodes())

        # Inicializar matriz con infinito
        matriz = {}
        for i in router_ids:
            matriz[i] = {}
            for j in router_ids:
                if i == j:
                    matriz[i][j] = 0
                elif grafo.has_edge(i, j):
                    matriz[i][j] = grafo[i][j]['weight']
                else:
                    matriz[i][j] = float('inf')

        return {
            'router_ids': router_ids,
            'matriz': matriz
        }

    def obtener_grado_router(self, id_router):
        """
        Calcula el grado de un router (número de conexiones)

        Args:
            id_router: ID del router

        Returns:
            Número de enlaces del router
        """
        self.network_graph.construir_grafo()
        grafo = self.network_graph.grafo

        if id_router in grafo.nodes:
            return grafo.degree(id_router)
        return 0

    def encontrar_routers_criticos(self):
        """
        Identifica routers críticos usando NetworkX

        Returns:
            Lista de routers críticos
        """
        return self.network_graph.encontrar_routers_criticos()

    def encontrar_enlaces_criticos(self):
        """
        Identifica enlaces críticos (puentes) usando NetworkX

        Returns:
            Lista de enlaces críticos con información
        """
        puentes = self.network_graph.encontrar_enlaces_criticos()

        enlaces_criticos = []
        for (router1, router2) in puentes:
            r1 = self.router_dao.obtener_por_id(router1)
            r2 = self.router_dao.obtener_por_id(router2)

            if r1 and r2:
                enlaces_criticos.append({
                    'router1_id': router1,
                    'router1_nombre': r1.nombre,
                    'router2_id': router2,
                    'router2_nombre': r2.nombre
                })

        return enlaces_criticos

    def validar_topologia(self):
        """
        Valida la consistencia de la topología

        Returns:
            Diccionario con resultados de validación
        """
        errores = []
        advertencias = []

        # Verificar routers sin enlaces
        routers = self.router_dao.obtener_activos()
        for router in routers:
            grado = self.obtener_grado_router(router.id_router)
            if grado == 0:
                advertencias.append(f"Router {router.nombre} no tiene enlaces")
            elif grado == 1:
                advertencias.append(f"Router {router.nombre} tiene solo 1 enlace (punto de fallo)")

        # Verificar enlaces con routers inactivos
        enlaces = self.enlace_dao.obtener_activos()
        for enlace in enlaces:
            router_origen = self.router_dao.obtener_por_id(enlace.router_origen)
            router_destino = self.router_dao.obtener_por_id(enlace.router_destino)

            if not router_origen or router_origen.estado != 'Activo':
                errores.append(f"Enlace {enlace.id_enlace} tiene router origen inactivo")

            if not router_destino or router_destino.estado != 'Activo':
                errores.append(f"Enlace {enlace.id_enlace} tiene router destino inactivo")

        # Verificar conectividad
        conectividad = self.network_graph.verificar_conectividad()
        if not conectividad['conectada']:
            advertencias.append(f"La red tiene {conectividad['componentes']} componentes desconectadas")

        return {
            'valida': len(errores) == 0,
            'errores': errores,
            'advertencias': advertencias
        }

    def obtener_estadisticas_topologia(self):
        """
        Obtiene estadísticas avanzadas de la topología

        Returns:
            Diccionario con estadísticas
        """
        return self.network_graph.obtener_estadisticas_grafo()

    def obtener_centralidad_routers(self):
        """
        Calcula centralidad de routers

        Returns:
            Diccionario con métricas de centralidad
        """
        return self.network_graph.calcular_centralidad()