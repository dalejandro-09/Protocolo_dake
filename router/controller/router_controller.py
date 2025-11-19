from datetime import datetime
from router.dao.vecino_dao import VecinoDAO
from router.dao.tb_enrutamiento_dao import TbEnrutamientoDAO
from router.dao.mensaje_dao import MensajeDAO
from router.dao.log_router_dao import LogRouterDAO
from router.model.vecino import Vecino
from router.model.tb_enrutamiento import TbEnrutamiento
from router.model.mensaje import Mensaje
from router.services.ospf_simulator import OSPFSimulator
from router.services.hello_protocol import HelloProtocol
from router.config.settings import ESTADOS_VECINO, TIPOS_MENSAJE, ORIGEN_INFO

class RouterController:
    def __init__(self, router_id, router_nombre, router_ip):
        self.router_id = router_id
        self.router_nombre = router_nombre
        self.router_ip = router_ip

        self.vecino_dao = VecinoDAO()
        self.enrutamiento_dao = TbEnrutamientoDAO()
        self.mensaje_dao = MensajeDAO()
        self.log_dao = LogRouterDAO()

        self.ospf = OSPFSimulator(router_id, router_nombre)
        self.hello_protocol = HelloProtocol(router_nombre, router_ip)  # ← PASAR router_ip

        # Cliente TCP
        self.tcp_client = None

        # Registrar inicio del router
        self.log_dao.registrar_evento(
            "Router iniciado",
            f"Router '{router_nombre}' ({router_ip}) iniciado correctamente"
        )

    # ==================== INFORMACIÓN DEL ROUTER ====================

    def obtener_info_router(self):
        """
        Obtiene información básica del router

        Returns:
            Diccionario con información del router
        """
        return {
            'nombre': self.router_nombre,
            'ip': self.router_ip,
            'total_vecinos': self.vecino_dao.contar_vecinos(),
            'total_rutas': self.enrutamiento_dao.contar_rutas(),
            'total_mensajes': self.mensaje_dao.contar_mensajes(),
            'estado_ospf': self.ospf.obtener_estado_ospf()
        }

    def obtener_resumen(self):
        """
        Obtiene un resumen del estado del router

        Returns:
            Diccionario con estadísticas
        """
        total_vecinos = self.vecino_dao.contar_vecinos()
        vecinos_activos = len(self.vecino_dao.obtener_activos())
        total_rutas = self.enrutamiento_dao.contar_rutas()
        total_mensajes = self.mensaje_dao.contar_mensajes()

        return {
            'router_nombre': self.router_nombre,
            'router_ip': self.router_ip,
            'total_vecinos': total_vecinos,
            'vecinos_activos': vecinos_activos,
            'vecinos_inactivos': total_vecinos - vecinos_activos,
            'total_rutas': total_rutas,
            'total_mensajes': total_mensajes,
            'hello_activo': self.hello_protocol.esta_activo(),
            'timestamp': datetime.now()
        }

    # ==================== GESTIÓN DE VECINOS ====================

    def agregar_vecino(self, router_vecino, ip_vecino, costo_enlace=1.0, estado='Down'):

        # Validar estado
        if estado not in ESTADOS_VECINO:
            print(f"✗ Estado inválido. Debe ser uno de: {ESTADOS_VECINO}")
            return None

        # Verificar si ya existe
        if self.vecino_dao.existe_vecino(router_vecino=router_vecino):
            print(f"✗ Ya existe un vecino con nombre '{router_vecino}'")
            return None

        if self.vecino_dao.existe_vecino(ip_vecino=ip_vecino):
            print(f"✗ Ya existe un vecino con IP '{ip_vecino}'")
            return None

        # Crear vecino
        vecino = Vecino(
            router_vecino=router_vecino,
            ip_vecino=ip_vecino,
            costo_enlace=costo_enlace,
            estado_vecino=estado
        )

        vecino_id = self.vecino_dao.crear(vecino)

        if vecino_id:
            self.log_dao.registrar_evento(
                "Vecino agregado",
                f"Vecino '{router_vecino}' agregado con IP {ip_vecino}"
            )

        return vecino_id

    def obtener_vecino(self, id_vecino):
        """Obtiene un vecino por ID"""
        return self.vecino_dao.obtener_por_id(id_vecino)

    def listar_vecinos(self, solo_activos=False):
        """
        Lista todos los vecinos

        Args:
            solo_activos: Si True, solo lista vecinos activos (Full/2-Way)

        Returns:
            Lista de vecinos
        """
        if solo_activos:
            return self.vecino_dao.obtener_activos()
        return self.vecino_dao.obtener_todos()

    def actualizar_vecino(self, id_vecino, router_vecino=None, ip_vecino=None,
                          costo_enlace=None, estado=None):
        """
        Actualiza los datos de un vecino

        Args:
            id_vecino: ID del vecino
            router_vecino: Nuevo nombre (opcional)
            ip_vecino: Nueva IP (opcional)
            costo_enlace: Nuevo costo (opcional)
            estado: Nuevo estado (opcional)

        Returns:
            True si fue exitoso
        """
        vecino = self.vecino_dao.obtener_por_id(id_vecino)
        if not vecino:
            print(f"✗ Vecino ID {id_vecino} no encontrado")
            return False

        # Actualizar campos
        if router_vecino:
            vecino.router_vecino = router_vecino
        if ip_vecino:
            vecino.ip_vecino = ip_vecino
        if costo_enlace is not None:
            vecino.costo_enlace = costo_enlace
        if estado:
            if estado not in ESTADOS_VECINO:
                print(f"✗ Estado inválido. Debe ser uno de: {ESTADOS_VECINO}")
                return False
            vecino.estado_vecino = estado

        vecino.tiempo_ultimo_hello = datetime.now()

        if self.vecino_dao.actualizar(vecino):
            self.log_dao.registrar_evento(
                "Vecino actualizado",
                f"Vecino ID {id_vecino} actualizado"
            )
            return True
        return False

    def cambiar_estado_vecino(self, id_vecino, nuevo_estado):
        """
        Cambia el estado de un vecino

        Args:
            id_vecino: ID del vecino
            nuevo_estado: Nuevo estado

        Returns:
            True si fue exitoso
        """
        if nuevo_estado not in ESTADOS_VECINO:
            print(f"✗ Estado inválido. Debe ser uno de: {ESTADOS_VECINO}")
            return False

        if self.vecino_dao.cambiar_estado(id_vecino, nuevo_estado):
            self.log_dao.registrar_evento(
                "Estado de vecino cambiado",
                f"Vecino ID {id_vecino} cambió a estado '{nuevo_estado}'"
            )
            return True
        return False

    def eliminar_vecino(self, id_vecino):
        """
        Elimina un vecino

        Args:
            id_vecino: ID del vecino

        Returns:
            True si fue exitoso
        """
        vecino = self.vecino_dao.obtener_por_id(id_vecino)
        if not vecino:
            print(f"✗ Vecino ID {id_vecino} no encontrado")
            return False

        nombre = vecino.router_vecino

        # Eliminar rutas que usan este vecino
        rutas = self.enrutamiento_dao.obtener_por_next_hop(vecino.ip_vecino)
        for ruta in rutas:
            self.enrutamiento_dao.eliminar(ruta.id_ruta)

        if self.vecino_dao.eliminar(id_vecino):
            self.log_dao.registrar_evento(
                "Vecino eliminado",
                f"Vecino '{nombre}' eliminado"
            )
            return True
        return False

    # ==================== GESTIÓN DE TABLA DE ENRUTAMIENTO ====================

    def agregar_ruta(self, destino, next_hop, interfaz_salida,
                     costo_total=0.0, origen_info='Interna'):
        """
        Agrega una nueva ruta a la tabla de enrutamiento

        Args:
            destino: Dirección de destino
            next_hop: Next hop
            interfaz_salida: Interfaz de salida
            costo_total: Costo total
            origen_info: Origen de la información

        Returns:
            ID de la ruta creada o None
        """
        # Validar origen
        if origen_info not in ORIGEN_INFO:
            print(f"✗ Origen inválido. Debe ser uno de: {ORIGEN_INFO}")
            return None

        # Verificar si ya existe ruta al destino
        if self.enrutamiento_dao.existe_destino(destino):
            print(f"⚠ Ya existe una ruta a {destino}. Actualizando...")
            ruta_existente = self.enrutamiento_dao.obtener_por_destino(destino)

            # Actualizar si el nuevo costo es menor
            if costo_total < ruta_existente.costo_total:
                ruta_existente.next_hop = next_hop
                ruta_existente.interfaz_salida = interfaz_salida
                ruta_existente.costo_total = costo_total
                ruta_existente.origen_info = origen_info

                if self.enrutamiento_dao.actualizar(ruta_existente):
                    print(f"✓ Ruta a {destino} actualizada con mejor costo")
                    return ruta_existente.id_ruta
            else:
                print(f"✗ Ruta existente tiene mejor o igual costo")
                return None

        # Crear nueva ruta
        ruta = TbEnrutamiento(
            destino=destino,
            next_hop=next_hop,
            interfaz_salida=interfaz_salida,
            costo_total=costo_total,
            origen_info=origen_info
        )

        ruta_id = self.enrutamiento_dao.crear(ruta)

        if ruta_id:
            self.log_dao.registrar_evento(
                "Ruta agregada",
                f"Ruta a {destino} via {next_hop} agregada (costo: {costo_total})"
            )

        return ruta_id

    def obtener_ruta(self, id_ruta):
        """Obtiene una ruta por ID"""
        return self.enrutamiento_dao.obtener_por_id(id_ruta)

    def obtener_ruta_a_destino(self, destino):
        """Obtiene la ruta a un destino específico"""
        return self.enrutamiento_dao.obtener_por_destino(destino)

    def listar_rutas(self, filtro_origen=None):
        """
        Lista todas las rutas

        Args:
            filtro_origen: Filtrar por origen ('Interna', 'Controlador', 'Externa')

        Returns:
            Lista de rutas
        """
        if filtro_origen:
            return self.enrutamiento_dao.obtener_por_origen(filtro_origen)
        return self.enrutamiento_dao.obtener_todas()

    def actualizar_ruta(self, id_ruta, destino=None, next_hop=None,
                        interfaz_salida=None, costo_total=None, origen_info=None):
        """
        Actualiza una ruta

        Args:
            id_ruta: ID de la ruta
            destino: Nuevo destino (opcional)
            next_hop: Nuevo next hop (opcional)
            interfaz_salida: Nueva interfaz (opcional)
            costo_total: Nuevo costo (opcional)
            origen_info: Nuevo origen (opcional)

        Returns:
            True si fue exitoso
        """
        ruta = self.enrutamiento_dao.obtener_por_id(id_ruta)
        if not ruta:
            print(f"✗ Ruta ID {id_ruta} no encontrada")
            return False

        # Actualizar campos
        if destino:
            ruta.destino = destino
        if next_hop:
            ruta.next_hop = next_hop
        if interfaz_salida:
            ruta.interfaz_salida = interfaz_salida
        if costo_total is not None:
            ruta.costo_total = costo_total
        if origen_info:
            if origen_info not in ORIGEN_INFO:
                print(f"✗ Origen inválido. Debe ser uno de: {ORIGEN_INFO}")
                return False
            ruta.origen_info = origen_info

        if self.enrutamiento_dao.actualizar(ruta):
            self.log_dao.registrar_evento(
                "Ruta actualizada",
                f"Ruta ID {id_ruta} actualizada"
            )
            return True
        return False

    def eliminar_ruta(self, id_ruta):
        """
        Elimina una ruta

        Args:
            id_ruta: ID de la ruta

        Returns:
            True si fue exitoso
        """
        ruta = self.enrutamiento_dao.obtener_por_id(id_ruta)
        if not ruta:
            print(f"✗ Ruta ID {id_ruta} no encontrada")
            return False

        destino = ruta.destino

        if self.enrutamiento_dao.eliminar(id_ruta):
            self.log_dao.registrar_evento(
                "Ruta eliminada",
                f"Ruta a {destino} eliminada"
            )
            return True
        return False

    def limpiar_rutas_origen(self, origen_info):
        """
        Limpia todas las rutas de un origen específico

        Args:
            origen_info: Origen a limpiar

        Returns:
            Número de rutas eliminadas
        """
        if origen_info not in ORIGEN_INFO:
            print(f"✗ Origen inválido. Debe ser uno de: {ORIGEN_INFO}")
            return 0

        eliminadas = self.enrutamiento_dao.eliminar_por_origen(origen_info)

        if eliminadas > 0:
            self.log_dao.registrar_evento(
                f"Rutas de origen '{origen_info}' limpiadas",
                f"{eliminadas} rutas eliminadas"
            )

        return eliminadas

    def limpiar_tabla_enrutamiento(self):
        """
        Limpia toda la tabla de enrutamiento

        Returns:
            True si fue exitoso
        """
        if self.enrutamiento_dao.limpiar_tabla():
            self.log_dao.registrar_evento(
                "Tabla de enrutamiento limpiada",
                "Todas las rutas eliminadas"
            )
            return True
        return False

    # ==================== GESTIÓN DE MENSAJES ====================

    def enviar_mensaje(self, tipo, receptor, contenido):
        """
        Envía un mensaje

        Args:
            tipo: Tipo de mensaje
            receptor: Router receptor
            contenido: Contenido del mensaje

        Returns:
            ID del mensaje o None
        """
        if tipo not in TIPOS_MENSAJE:
            print(f"✗ Tipo de mensaje inválido. Debe ser uno de: {TIPOS_MENSAJE}")
            return None

        mensaje_id = self.mensaje_dao.registrar_mensaje(
            tipo=tipo,
            emisor=self.router_nombre,
            receptor=receptor,
            contenido=contenido
        )

        if mensaje_id:
            self.log_dao.registrar_evento(
                f"Mensaje {tipo} enviado",
                f"A: {receptor}"
            )

        return mensaje_id

    def obtener_mensajes_recibidos(self, limite=50):
        """
        Obtiene los mensajes recibidos por este router

        Args:
            limite: Número máximo de mensajes

        Returns:
            Lista de mensajes
        """
        return self.mensaje_dao.obtener_por_receptor(self.router_nombre, limite)

    def obtener_mensajes_enviados(self, limite=50):
        """
        Obtiene los mensajes enviados por este router

        Args:
            limite: Número máximo de mensajes

        Returns:
            Lista de mensajes
        """
        return self.mensaje_dao.obtener_por_emisor(self.router_nombre, limite)

    def obtener_conversacion(self, otro_router, limite=50):
        """
        Obtiene la conversación con otro router

        Args:
            otro_router: Nombre del otro router
            limite: Número máximo de mensajes

        Returns:
            Lista de mensajes
        """
        return self.mensaje_dao.obtener_conversacion(
            self.router_nombre, otro_router, limite
        )

    # ==================== PROTOCOLO OSPF ====================

    def iniciar_ospf(self):
        """
        Inicia el protocolo OSPF (envío automático de HELLOs)
        """
        self.hello_protocol.iniciar_hello_timer()
        self.log_dao.registrar_evento(
            "Protocolo OSPF iniciado",
            "Envío automático de HELLOs activado"
        )

    def detener_ospf(self):
        """
        Detiene el protocolo OSPF
        """
        self.hello_protocol.detener_hello_timer()
        self.log_dao.registrar_evento(
            "Protocolo OSPF detenido",
            "Envío automático de HELLOs desactivado"
        )

    def enviar_hello_manual(self, vecino_nombre):
        """
        Envía un HELLO manual a un vecino

        Args:
            vecino_nombre: Nombre del vecino

        Returns:
            True si fue enviado
        """
        return self.ospf.enviar_hello(vecino_nombre)

    def enviar_hello_a_todos(self):
        """
        Envía HELLOs a todos los vecinos activos

        Returns:
            Número de mensajes enviados
        """
        return self.ospf.enviar_hello_a_todos()

    def procesar_hello(self, emisor):
        """
        Procesa un HELLO recibido

        Args:
            emisor: Router emisor

        Returns:
            True si fue procesado
        """
        return self.ospf.procesar_hello_recibido(emisor)

    def verificar_vecinos_caidos(self):
        """
        Verifica y marca vecinos caídos

        Returns:
            Lista de vecinos marcados como caídos
        """
        return self.ospf.verificar_vecinos_caidos()

    def establecer_adyacencia(self, vecino_id):
        """
        Establece adyacencia Full con un vecino

        Args:
            vecino_id: ID del vecino

        Returns:
            True si fue exitoso
        """
        return self.ospf.establecer_adyacencia(vecino_id)

    def obtener_estado_ospf(self):
        """
        Obtiene el estado del protocolo OSPF

        Returns:
            Diccionario con estado
        """
        return self.ospf.obtener_estado_vecinos()

    # ==================== LOGS ====================

    def obtener_logs_recientes(self, limite=20):
        """Obtiene los logs más recientes"""
        return self.log_dao.obtener_todos(limite)

    def obtener_logs_por_evento(self, evento, limite=20):
        """Obtiene logs de un tipo de evento"""
        return self.log_dao.obtener_por_evento(evento, limite)

    def limpiar_datos_antiguos(self, dias=30):
        """
        Limpia datos antiguos (logs y mensajes)

        Args:
            dias: Antigüedad de los datos
        """
        logs_eliminados = self.log_dao.limpiar_logs_antiguos(dias)
        mensajes_eliminados = self.mensaje_dao.limpiar_mensajes_antiguos(dias)

        print(f"✓ Limpieza completada: {logs_eliminados} logs y {mensajes_eliminados} mensajes eliminados")

        self.log_dao.registrar_evento(
            "Limpieza de datos",
            f"Eliminados {logs_eliminados} logs y {mensajes_eliminados} mensajes antiguos"
        )

    # ==================== CLIENTE TCP ====================

    def conectar_a_controlador(self, controller_host='localhost', controller_port=6633):
        """
        Conecta al controlador SDN

        Args:
            controller_host: Host del controlador
            controller_port: Puerto del controlador

        Returns:
            True si la conexión fue exitosa
        """
        from shared.communication.tcp_client import TCPClient

        if self.tcp_client and self.tcp_client.is_connected():
            print("Ya existe una conexión con el controlador")
            return False

        self.tcp_client = TCPClient(
            router_id=self.router_id,
            router_nombre=self.router_nombre,
            router_ip=self.router_ip,
            controller_host=controller_host,
            controller_port=controller_port,
            router_controller=self
        )

        if self.tcp_client.connect():
            self.log_dao.registrar_evento(
                "Conectado al controlador",
                f"Conexión establecida con {controller_host}:{controller_port}"
            )
            return True
        return False

    def desconectar_de_controlador(self):
        """Desconecta del controlador SDN"""
        if self.tcp_client:
            self.tcp_client.disconnect()
            self.log_dao.registrar_evento(
                "Desconectado del controlador",
                "Conexión con controlador cerrada"
            )

    def esta_conectado_a_controlador(self):
        if self.tcp_client:
            return self.tcp_client.is_connected()
        return False

    def notificar_vecinos_a_controlador(self):
        if not self.tcp_client or not self.tcp_client.is_connected():
            print(" No hay conexión con el controlador")
            return False

        vecinos = self.listar_vecinos(solo_activos=True)
        self.tcp_client.send_neighbor_update(vecinos)
        return True

    def solicitar_ruta_a_controlador(self, destino_ip):
        """
        Solicita una ruta al controlador

        Args:
            destino_ip: IP de destino
        """
        if not self.tcp_client or not self.tcp_client.is_connected():
            print(" No hay conexión con el controlador")
            return False

        self.tcp_client.request_route(destino_ip)
        return True