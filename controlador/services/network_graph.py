import networkx as nx
import matplotlib.pyplot as plt
from controlador.dao.router_dao import RouterDAO
from controlador.dao.enlace_dao import EnlaceDAO

class NetworkGraph:
    """Clase para gestionar el grafo de la red con NetworkX"""

    def __init__(self):
        self.router_dao = RouterDAO()
        self.enlace_dao = EnlaceDAO()
        self.grafo = nx.Graph()

    def construir_grafo(self):
        """
        Construye el grafo de la red desde la base de datos

        Returns:
            networkx.Graph: Grafo construido
        """
        # Limpiar grafo anterior
        self.grafo.clear()

        # Obtener routers activos
        routers = self.router_dao.obtener_activos()

        # Agregar nodos (routers)
        for router in routers:
            self.grafo.add_node(
                router.id_router,
                nombre=router.nombre,
                ip=router.ip,
                estado=router.estado
            )

        # Obtener enlaces activos
        enlaces = self.enlace_dao.obtener_activos()

        # Agregar aristas (enlaces)
        for enlace in enlaces:
            if enlace.router_origen in self.grafo.nodes and enlace.router_destino in self.grafo.nodes:
                self.grafo.add_edge(
                    enlace.router_origen,
                    enlace.router_destino,
                    weight=enlace.costo,
                    id_enlace=enlace.id_enlace,
                    ancho_banda=enlace.ancho_banda,
                    retardo_ms=enlace.retardo_ms
                )

        return self.grafo

    def calcular_ruta(self, origen, destino):
        """
        Calcula la ruta más corta entre dos routers usando Dijkstra

        Args:
            origen: ID del router origen
            destino: ID del router destino

        Returns:
            Tupla (camino, costo_total) o (None, None) si no hay ruta
        """
        # Construir grafo actualizado
        self.construir_grafo()

        # Verificar que origen y destino existan
        if origen not in self.grafo.nodes or destino not in self.grafo.nodes:
            print(f"✗ Router origen ({origen}) o destino ({destino}) no existe o no está activo")
            return None, None

        # Verificar que haya conectividad
        if not nx.has_path(self.grafo, origen, destino):
            print(f"✗ No existe ruta entre R{origen} y R{destino}")
            return None, None

        try:
            # Calcular camino más corto
            camino = nx.shortest_path(self.grafo, origen, destino, weight='weight')
            costo_total = nx.shortest_path_length(self.grafo, origen, destino, weight='weight')

            return camino, costo_total

        except nx.NetworkXNoPath:
            print(f"✗ No existe ruta entre R{origen} y R{destino}")
            return None, None
        except Exception as e:
            print(f"✗ Error al calcular ruta: {e}")
            return None, None

    def calcular_todas_las_rutas(self, origen):
        """
        Calcula las rutas más cortas desde un origen a todos los demás routers

        Args:
            origen: ID del router origen

        Returns:
            Diccionario {destino: (camino, costo)}
        """
        self.construir_grafo()

        if origen not in self.grafo.nodes:
            print(f"✗ Router origen ({origen}) no existe o no está activo")
            return {}

        rutas = {}

        # Calcular rutas a todos los nodos
        for destino in self.grafo.nodes:
            if destino == origen:
                continue

            camino, costo = self.calcular_ruta(origen, destino)
            rutas[destino] = (camino, costo)

        return rutas

    def calcular_rutas_alternativas(self, origen, destino, k=3):
        """
        Calcula K rutas alternativas entre dos routers

        Args:
            origen: ID del router origen
            destino: ID del router destino
            k: Número de rutas alternativas a buscar

        Returns:
            Lista de tuplas [(camino1, costo1), (camino2, costo2), ...]
        """
        self.construir_grafo()

        if origen not in self.grafo.nodes or destino not in self.grafo.nodes:
            return []

        try:
            # Algoritmo de k-shortest paths
            rutas_alternativas = []

            # Obtener k caminos más cortos
            for camino in nx.shortest_simple_paths(self.grafo, origen, destino, weight='weight'):
                if len(rutas_alternativas) >= k:
                    break

                # Calcular costo del camino
                costo = sum(
                    self.grafo[camino[i]][camino[i + 1]]['weight']
                    for i in range(len(camino) - 1)
                )

                rutas_alternativas.append((camino, costo))

            return rutas_alternativas

        except Exception as e:
            print(f"✗ Error al calcular rutas alternativas: {e}")
            return []

    def verificar_conectividad(self):
        """
        Verifica la conectividad de la red

        Returns:
            Diccionario con información de conectividad
        """
        self.construir_grafo()

        if len(self.grafo.nodes) == 0:
            return {
                'conectada': False,
                'componentes': 0,
                'routers_aislados': [],
                'detalles_componentes': []
            }

        # Verificar si el grafo es conexo
        conectada = nx.is_connected(self.grafo)

        # Obtener componentes conectadas
        componentes = list(nx.connected_components(self.grafo))

        # Routers aislados (componentes de tamaño 1)
        routers_aislados = [list(comp)[0] for comp in componentes if len(comp) == 1]

        return {
            'conectada': conectada,
            'componentes': len(componentes),
            'routers_aislados': routers_aislados,
            'detalles_componentes': [list(comp) for comp in componentes]
        }

    def encontrar_routers_criticos(self):
        """
        Identifica routers críticos (puntos de articulación)
        Routers cuya eliminación desconectaría la red

        Returns:
            Lista de IDs de routers críticos
        """
        self.construir_grafo()

        if len(self.grafo.nodes) < 2:
            return []

        # NetworkX tiene función para encontrar puntos de articulación
        puntos_articulacion = list(nx.articulation_points(self.grafo))

        # Obtener información de cada router crítico
        routers_criticos = []
        for router_id in puntos_articulacion:
            router = self.router_dao.obtener_por_id(router_id)
            if router:
                routers_criticos.append({
                    'id': router.id_router,
                    'nombre': router.nombre,
                    'grado': self.grafo.degree(router_id)
                })

        return routers_criticos

    def encontrar_enlaces_criticos(self):
        """
        Identifica enlaces críticos (puentes)
        Enlaces cuya eliminación desconectaría la red

        Returns:
            Lista de tuplas (router_origen, router_destino)
        """
        self.construir_grafo()

        if len(self.grafo.edges) == 0:
            return []

        # NetworkX tiene función para encontrar puentes
        puentes = list(nx.bridges(self.grafo))

        return puentes

    def calcular_centralidad(self):
        """
        Calcula métricas de centralidad para cada router

        Returns:
            Diccionario con diferentes métricas de centralidad
        """
        self.construir_grafo()

        if len(self.grafo.nodes) < 2:
            return {}

        metricas = {
            'degree': nx.degree_centrality(self.grafo),
            'betweenness': nx.betweenness_centrality(self.grafo, weight='weight'),
            'closeness': nx.closeness_centrality(self.grafo, distance='weight')
        }

        return metricas

    def analizar_congestion_enlaces(self):
        """
        Analiza qué enlaces son más utilizados en las rutas

        Returns:
            Diccionario con centralidad de aristas
        """
        self.construir_grafo()

        if len(self.grafo.edges) == 0:
            return {}

        # Calcular betweenness centrality de aristas
        edge_centrality = nx.edge_betweenness_centrality(self.grafo, weight='weight')

        # Ordenar por uso
        enlaces_ordenados = sorted(
            edge_centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return dict(enlaces_ordenados)

    def obtener_estadisticas_grafo(self):
        """
        Obtiene estadísticas generales del grafo

        Returns:
            Diccionario con estadísticas
        """
        self.construir_grafo()

        if len(self.grafo.nodes) == 0:
            return {
                'num_routers': 0,
                'num_enlaces': 0,
                'densidad': 0,
                'diametro': 0,
                'radio': 0
            }

        stats = {
            'num_routers': self.grafo.number_of_nodes(),
            'num_enlaces': self.grafo.number_of_edges(),
            'densidad': nx.density(self.grafo)
        }

        # Solo si el grafo es conexo
        if nx.is_connected(self.grafo):
            stats['diametro'] = nx.diameter(self.grafo)
            stats['radio'] = nx.radius(self.grafo)
        else:
            stats['diametro'] = None
            stats['radio'] = None

        return stats

    def formato_camino(self, camino):
        """
        Convierte una lista de IDs a formato string "R1->R3->R5"

        Args:
            camino: Lista de IDs de routers

        Returns:
            String con el formato del camino
        """
        if not camino:
            return ""
        return "->".join([f"R{nodo}" for nodo in camino])

    def visualizar_topologia(self, guardar_archivo=None, mostrar=True):
        """
        Visualiza la topología de la red usando matplotlib

        Args:
            guardar_archivo: Nombre de archivo para guardar (None para no guardar)
            mostrar: Si True, muestra la ventana interactiva
        """
        self.construir_grafo()

        if len(self.grafo.nodes) == 0:
            print("⚠️ No hay routers para visualizar")
            return

        # Crear figura
        plt.figure(figsize=(12, 8))

        # Layout del grafo (spring layout es bueno para redes)
        pos = nx.spring_layout(self.grafo, k=2, iterations=50, seed=42)

        # Obtener información para colorear
        conectividad = self.verificar_conectividad()
        routers_criticos = self.encontrar_routers_criticos()
        ids_criticos = [r['id'] for r in routers_criticos]

        # Colores de nodos
        colores_nodos = []
        for nodo in self.grafo.nodes:
            if nodo in ids_criticos:
                colores_nodos.append('#ff4444')  # Rojo para críticos
            else:
                colores_nodos.append('#4CAF50')  # Verde para normales

        # Dibujar nodos
        nx.draw_networkx_nodes(
            self.grafo, pos,
            node_color=colores_nodos,
            node_size=1500,
            alpha=0.9,
            edgecolors='black',
            linewidths=2
        )

        # Etiquetas de nodos (nombres de routers)
        labels = {}
        for nodo in self.grafo.nodes:
            router = self.router_dao.obtener_por_id(nodo)
            if router:
                labels[nodo] = router.nombre
            else:
                labels[nodo] = f"R{nodo}"

        nx.draw_networkx_labels(
            self.grafo, pos,
            labels,
            font_size=12,
            font_weight='bold',
            font_color='white'
        )

        # Dibujar aristas
        nx.draw_networkx_edges(
            self.grafo, pos,
            width=2,
            alpha=0.6,
            edge_color='#666666'
        )

        # Etiquetas de aristas (costos)
        edge_labels = {
            (u, v): f"{self.grafo[u][v]['weight']:.1f}"
            for u, v in self.grafo.edges
        }

        nx.draw_networkx_edge_labels(
            self.grafo, pos,
            edge_labels,
            font_size=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
        )

        # Título
        plt.title(
            f"Topología de Red SDN\n"
            f"Routers: {self.grafo.number_of_nodes()} | "
            f"Enlaces: {self.grafo.number_of_edges()} | "
            f"Conectada: {'Sí' if conectividad['conectada'] else 'No'}",
            fontsize=16,
            fontweight='bold',
            pad=20
        )

        # Leyenda
        from matplotlib.patches import Patch
        leyenda = [
            Patch(facecolor='#4CAF50', edgecolor='black', label='Router Normal'),
            Patch(facecolor='#ff4444', edgecolor='black', label='Router Crítico')
        ]
        plt.legend(handles=leyenda, loc='upper left', fontsize=10)

        plt.axis('off')
        plt.tight_layout()

        # Guardar si se especifica
        if guardar_archivo:
            plt.savefig(guardar_archivo, dpi=300, bbox_inches='tight')
            print(f"✓ Topología guardada en: {guardar_archivo}")

        # Mostrar
        if mostrar:
            plt.show()
        else:
            plt.close()

    def visualizar_ruta(self, origen, destino, guardar_archivo=None, mostrar=True):
        """
        Visualiza una ruta específica en la topología

        Args:
            origen: ID del router origen
            destino: ID del router destino
            guardar_archivo: Nombre de archivo para guardar
            mostrar: Si True, muestra la ventana interactiva
        """
        self.construir_grafo()

        # Calcular ruta
        camino, costo = self.calcular_ruta(origen, destino)

        if camino is None:
            print("✗ No se puede visualizar: no existe ruta")
            return

        # Crear figura
        plt.figure(figsize=(12, 8))

        # Layout
        pos = nx.spring_layout(self.grafo, k=2, iterations=50, seed=42)

        # Colores de nodos
        colores_nodos = []
        for nodo in self.grafo.nodes:
            if nodo == origen:
                colores_nodos.append('#2196F3')  # Azul para origen
            elif nodo == destino:
                colores_nodos.append('#FF9800')  # Naranja para destino
            elif nodo in camino:
                colores_nodos.append('#4CAF50')  # Verde para ruta
            else:
                colores_nodos.append('#CCCCCC')  # Gris para otros

        # Dibujar todos los nodos
        nx.draw_networkx_nodes(
            self.grafo, pos,
            node_color=colores_nodos,
            node_size=1500,
            alpha=0.9,
            edgecolors='black',
            linewidths=2
        )

        # Etiquetas
        labels = {}
        for nodo in self.grafo.nodes:
            router = self.router_dao.obtener_por_id(nodo)
            labels[nodo] = router.nombre if router else f"R{nodo}"

        nx.draw_networkx_labels(
            self.grafo, pos,
            labels,
            font_size=12,
            font_weight='bold',
            font_color='white'
        )

        # Dibujar todas las aristas (gris claro)
        nx.draw_networkx_edges(
            self.grafo, pos,
            width=1,
            alpha=0.3,
            edge_color='#999999'
        )

        # Dibujar aristas de la ruta (destacadas)
        aristas_ruta = [(camino[i], camino[i + 1]) for i in range(len(camino) - 1)]
        nx.draw_networkx_edges(
            self.grafo, pos,
            edgelist=aristas_ruta,
            width=4,
            alpha=1.0,
            edge_color='#4CAF50',
            arrows=True,
            arrowsize=20,
            arrowstyle='->'
        )

        # Etiquetas de costos
        edge_labels = {
            (u, v): f"{self.grafo[u][v]['weight']:.1f}"
            for u, v in self.grafo.edges
        }
        nx.draw_networkx_edge_labels(
            self.grafo, pos,
            edge_labels,
            font_size=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
        )

        # Título
        camino_str = self.formato_camino(camino)
        plt.title(
            f"Ruta: {camino_str}\n"
            f"Costo Total: {costo:.2f} | Saltos: {len(camino) - 1}",
            fontsize=16,
            fontweight='bold',
            pad=20
        )

        # Leyenda
        from matplotlib.patches import Patch
        leyenda = [
            Patch(facecolor='#2196F3', edgecolor='black', label='Origen'),
            Patch(facecolor='#FF9800', edgecolor='black', label='Destino'),
            Patch(facecolor='#4CAF50', edgecolor='black', label='En Ruta'),
            Patch(facecolor='#CCCCCC', edgecolor='black', label='Otro Router')
        ]
        plt.legend(handles=leyenda, loc='upper left', fontsize=10)

        plt.axis('off')
        plt.tight_layout()

        if guardar_archivo:
            plt.savefig(guardar_archivo, dpi=300, bbox_inches='tight')
            print(f"✓ Ruta guardada en: {guardar_archivo}")

        if mostrar:
            plt.show()
        else:
            plt.close()