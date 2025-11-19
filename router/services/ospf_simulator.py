"""
Simulador del protocolo OSPF
"""

import time
from datetime import datetime, timedelta
from router.dao.vecino_dao import VecinoDAO
from router.dao.tb_enrutamiento_dao import TbEnrutamientoDAO
from router.dao.mensaje_dao import MensajeDAO
from router.dao.log_router_dao import LogRouterDAO
from router.model.vecino import Vecino
from router.model.mensaje import Mensaje
from router.config.settings import ROUTER_CONFIG


class OSPFSimulator:
    """Clase para simular el protocolo OSPF"""

    def __init__(self, router_nombre, router_ip):
        """
        Inicializa el simulador OSPF

        Args:
            router_nombre: Nombre del router
            router_ip: IP del router
        """
        self.router_nombre = router_nombre
        self.router_ip = router_ip
        self.vecino_dao = VecinoDAO()
        self.enrutamiento_dao = TbEnrutamientoDAO()
        self.mensaje_dao = MensajeDAO()
        self.log_dao = LogRouterDAO()

        self.hello_interval = ROUTER_CONFIG['hello_interval']
        self.dead_interval = ROUTER_CONFIG['dead_interval']

    def enviar_hello(self, vecino_nombre):
        """
        Envía un mensaje HELLO a un vecino

        Args:
            vecino_nombre: Nombre del router vecino

        Returns:
            True si el mensaje fue enviado
        """
        contenido = f"HELLO from {self.router_nombre} ({self.router_ip}) at {datetime.now()}"

        mensaje_id = self.mensaje_dao.registrar_mensaje(
            tipo='HELLO',
            emisor=self.router_nombre,
            receptor=vecino_nombre,
            contenido=contenido
        )

        if mensaje_id:
            self.log_dao.registrar_evento(
                f"HELLO enviado a {vecino_nombre}",
                contenido
            )
            return True
        return False

    def enviar_hello_a_todos(self):
        """
        Envía mensajes HELLO a todos los vecinos activos

        Returns:
            Número de mensajes enviados
        """
        vecinos = self.vecino_dao.obtener_activos()
        contador = 0

        for vecino in vecinos:
            if self.enviar_hello(vecino.router_vecino):
                contador += 1

        if contador > 0:
            print(f"✓ {contador} mensajes HELLO enviados")

        return contador

    def procesar_hello_recibido(self, emisor):
        """
        Procesa un mensaje HELLO recibido

        Args:
            emisor: Router que envió el HELLO

        Returns:
            True si fue procesado correctamente
        """
        # Buscar el vecino
        vecino = self.vecino_dao.obtener_por_nombre(emisor)

        if vecino:
            # Actualizar tiempo del último HELLO
            self.vecino_dao.actualizar_tiempo_hello(vecino.id_vecino)

            # Si estaba Down, cambiar a 2-Way
            if vecino.estado_vecino == 'Down':
                self.vecino_dao.cambiar_estado(vecino.id_vecino, '2-Way')
                self.log_dao.registrar_evento(
                    f"Vecino {emisor} cambió a 2-Way",
                    "HELLO recibido, vecindad establecida"
                )

            return True
        else:
            print(f"⚠️ HELLO recibido de vecino desconocido: {emisor}")
            return False

    def verificar_vecinos_caidos(self):
        """
        Verifica si hay vecinos que no han enviado HELLO

        Returns:
            Lista de vecinos marcados como caídos
        """
        vecinos_caidos = self.vecino_dao.obtener_vecinos_caidos(self.dead_interval)

        for vecino in vecinos_caidos:
            # Cambiar estado a Down
            self.vecino_dao.cambiar_estado(vecino.id_vecino, 'Down')

            self.log_dao.registrar_evento(
                f"Vecino {vecino.router_vecino} caído",
                f"No se recibió HELLO en {self.dead_interval} segundos"
            )

            # Eliminar rutas que usan este vecino como next_hop
            rutas_afectadas = self.enrutamiento_dao.obtener_por_next_hop(vecino.ip_vecino)
            for ruta in rutas_afectadas:
                self.enrutamiento_dao.eliminar(ruta.id_ruta)
                print(f"✗ Ruta a {ruta.destino} eliminada (vecino caído)")

        return vecinos_caidos

    def enviar_lsa(self, tipo_lsa, contenido):
        """
        Envía un LSA (Link State Advertisement)

        Args:
            tipo_lsa: Tipo de LSA
            contenido: Contenido del LSA

        Returns:
            Número de LSAs enviados
        """
        vecinos = self.vecino_dao.obtener_por_estado('Full')
        contador = 0

        for vecino in vecinos:
            mensaje_id = self.mensaje_dao.registrar_mensaje(
                tipo='LSA',
                emisor=self.router_nombre,
                receptor=vecino.router_vecino,
                contenido=f"{tipo_lsa}|{contenido}"
            )

            if mensaje_id:
                contador += 1

        if contador > 0:
            self.log_dao.registrar_evento(
                f"LSA enviado ({tipo_lsa})",
                f"Propagado a {contador} vecinos"
            )

        return contador

    def procesar_lsa(self, emisor, contenido):
        """
        Procesa un LSA recibido

        Args:
            emisor: Router que envió el LSA
            contenido: Contenido del LSA

        Returns:
            True si fue procesado correctamente
        """
        self.log_dao.registrar_evento(
            f"LSA recibido de {emisor}",
            contenido
        )

        # Aquí se implementaría el procesamiento del LSA
        # Por ahora solo lo registramos

        return True

    def establecer_adyacencia(self, vecino_nombre):
        """
        Establece adyacencia completa con un vecino (estado Full)

        Args:
            vecino_nombre: Nombre del vecino

        Returns:
            True si se estableció la adyacencia
        """
        vecino = self.vecino_dao.obtener_por_nombre(vecino_nombre)

        if not vecino:
            print(f"✗ Vecino {vecino_nombre} no encontrado")
            return False

        # Proceso de establecimiento de adyacencia OSPF
        # 1. Down -> Init (primer HELLO)
        if vecino.estado_vecino == 'Down':
            self.enviar_hello(vecino_nombre)
            time.sleep(0.5)

        # 2. Init -> 2-Way (HELLO bidireccional)
        if vecino.estado_vecino in ['Down', 'Init']:
            self.vecino_dao.cambiar_estado(vecino.id_vecino, '2-Way')
            self.log_dao.registrar_evento(
                f"Adyacencia 2-Way establecida con {vecino_nombre}",
                "Comunicación bidireccional confirmada"
            )

        # 3. 2-Way -> Full (intercambio de LSAs)
        if vecino.estado_vecino == '2-Way':
            # Cambiar a Full
            self.vecino_dao.cambiar_estado(vecino.id_vecino, 'Full')

            self.log_dao.registrar_evento(
                f"Adyacencia Full con {vecino.router_vecino}",
                "Intercambio de bases de datos completado"
            )

            # Enviar LSA para notificar el cambio
            self.enviar_lsa(
                "ROUTER_LSA",
                f"Adyacencia establecida con {vecino.router_vecino}"
            )

            return True

        return False

    def obtener_estado_ospf(self):
        """
        Obtiene el estado actual del protocolo OSPF

        Returns:
            Diccionario con información del estado
        """
        vecinos = self.vecino_dao.obtener_todos()

        estado = {
            'router': self.router_nombre,
            'ip': self.router_ip,
            'total_vecinos': len(vecinos),
            'vecinos_full': len([v for v in vecinos if v.estado_vecino == 'Full']),
            'vecinos_2way': len([v for v in vecinos if v.estado_vecino == '2-Way']),
            'vecinos_down': len([v for v in vecinos if v.estado_vecino == 'Down']),
            'hello_interval': self.hello_interval,
            'dead_interval': self.dead_interval
        }

        return estado

    def obtener_estado_vecinos(self):
        """
        Obtiene el estado de todos los vecinos

        Returns:
            Diccionario con estado de vecinos
        """
        vecinos = self.vecino_dao.obtener_todos()

        estado = {
            'total': len(vecinos),
            'full': 0,
            'two_way': 0,
            'down': 0,
            'detalles': []
        }

        for vecino in vecinos:
            # Contar por estado
            if vecino.estado_vecino == 'Full':
                estado['full'] += 1
            elif vecino.estado_vecino == '2-Way':
                estado['two_way'] += 1
            elif vecino.estado_vecino == 'Down':
                estado['down'] += 1

            # Agregar detalles
            estado['detalles'].append({
                'nombre': vecino.router_vecino,
                'ip': vecino.ip_vecino,
                'estado': vecino.estado_vecino,
                'tiempo_sin_hello': vecino.tiempo_sin_hello()
            })

        return estado

    def anunciar_red(self, red, mascara):
        """
        Anuncia una red conectada directamente

        Args:
            red: Dirección de red
            mascara: Máscara de subred

        Returns:
            True si se anunció correctamente
        """
        contenido = f"NETWORK|{red}|{mascara}"
        return self.enviar_lsa("NETWORK_LSA", contenido) > 0

    def calcular_spf(self):
        """
        Calcula el árbol SPF (Shortest Path First)
        Simulación simplificada del algoritmo de Dijkstra de OSPF

        Returns:
            Diccionario con rutas calculadas
        """
        print("🔄 Calculando árbol SPF...")

        # Obtener vecinos Full (con adyacencia completa)
        vecinos_full = self.vecino_dao.obtener_por_estado('Full')

        if not vecinos_full:
            print("⚠️ No hay vecinos Full para calcular SPF")
            return {}

        # Crear rutas directas a vecinos
        rutas_calculadas = {}

        for vecino in vecinos_full:
            rutas_calculadas[vecino.ip_vecino] = {
                'destino': vecino.ip_vecino,
                'next_hop': vecino.ip_vecino,
                'costo': vecino.costo_enlace,
                'tipo': 'directo'
            }

        self.log_dao.registrar_evento(
            "SPF calculado",
            f"{len(rutas_calculadas)} rutas directas calculadas"
        )

        return rutas_calculadas

    def actualizar_tabla_enrutamiento_ospf(self):
        """
        Actualiza la tabla de enrutamiento con rutas OSPF

        Returns:
            Número de rutas actualizadas
        """
        print("🔄 Actualizando tabla de enrutamiento OSPF...")

        # Calcular SPF
        rutas_spf = self.calcular_spf()

        # Limpiar rutas OSPF anteriores (origen Interna)
        self.enrutamiento_dao.eliminar_por_origen('Interna')

        # Agregar nuevas rutas
        contador = 0
        for destino, info_ruta in rutas_spf.items():
            # Crear entrada en tabla de enrutamiento
            from router.model.tb_enrutamiento import TbEnrutamiento

            ruta = TbEnrutamiento(
                destino=destino,
                next_hop=info_ruta['next_hop'],
                interfaz_salida=f"eth_to_{info_ruta['next_hop']}",
                costo_total=info_ruta['costo'],
                origen_info='Interna'
            )

            if self.enrutamiento_dao.crear(ruta):
                contador += 1

        print(f"✓ {contador} rutas OSPF agregadas a la tabla")

        self.log_dao.registrar_evento(
            "Tabla de enrutamiento actualizada",
            f"{contador} rutas OSPF instaladas"
        )

        return contador

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas del protocolo OSPF

        Returns:
            Diccionario con estadísticas
        """
        mensajes_hello = len(self.mensaje_dao.obtener_por_tipo('HELLO', 100))
        mensajes_lsa = len(self.mensaje_dao.obtener_por_tipo('LSA', 100))

        vecinos = self.vecino_dao.obtener_todos()

        return {
            'total_vecinos': len(vecinos),
            'vecinos_activos': len([v for v in vecinos if v.esta_activo()]),
            'mensajes_hello_enviados': mensajes_hello,
            'mensajes_lsa_enviados': mensajes_lsa,
            'adyacencias_full': len(self.vecino_dao.obtener_por_estado('Full'))
        }