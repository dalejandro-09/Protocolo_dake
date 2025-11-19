import socket
import ssl
import threading
import time
import os
from datetime import datetime
from shared.communication.tcp_protocol import Message, MessageType, MessageFactory

class TCPServer:
    def __init__(self, host='0.0.0.0', port=6633, controlador=None):
        self.host = host
        self.port = port
        self.controlador = controlador

        self.server_socket = None
        self.ssl_context = None
        self.running = False
        self.clients = {}  # {router_nombre: (socket, thread)}
        self.clients_lock = threading.Lock()

        # Thread para el servidor principal
        self.server_thread = None

        # Thread para heartbeat
        self.heartbeat_thread = None
        self.heartbeat_interval = 10  # segundos

        # Rutas de certificados SSL
        self.cert_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'certs')
        self.certfile = os.path.join(self.cert_dir, 'server.crt')
        self.keyfile = os.path.join(self.cert_dir, 'server.key')

    def _setup_ssl_context(self):
        try:
            # Crear contexto SSL con TLS (protocolo más seguro)
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

            # Cargar certificado y clave privada del servidor
            self.ssl_context.load_cert_chain(
                certfile=self.certfile,
                keyfile=self.keyfile
            )

            # Configuraciones de seguridad
            self.ssl_context.check_hostname = False  # Desactivado para localhost
            self.ssl_context.verify_mode = ssl.CERT_NONE  # Para desarrollo (CERT_REQUIRED en producción)

            # Configurar cifrados fuertes
            self.ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')

            print("✓ Contexto SSL configurado correctamente")
            return self.ssl_context

        except FileNotFoundError as e:
            print(f"✗ Error: No se encontraron los certificados SSL")
            print(f"  Buscar en: {self.cert_dir}")
            print(f"  Certificado: {self.certfile}")
            print(f"  Clave: {self.keyfile}")
            print(f"\n  Genera los certificados con:")
            print(f"  openssl genrsa -out server.key 2048")
            print(f"  openssl req -new -x509 -key server.key -out server.crt -days 365")
            return None

        except Exception as e:
            print(f"✗ Error al configurar SSL: {e}")
            return None

    def start(self):
        """Inicia el servidor TCP con SSL"""
        try:
            # Configurar SSL
            if not self._setup_ssl_context():
                return False

            # Crear socket TCP
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)

            # Envolver socket con SSL
            self.server_socket = self.ssl_context.wrap_socket(
                self.server_socket,
                server_side=True
            )

            self.running = True

            print(f"✓ Servidor TCP con SSL/TLS iniciado en {self.host}:{self.port}")
            print(f" Cifrado: Habilitado (TLS)")

            # Iniciar thread de aceptación de conexiones
            self.server_thread = threading.Thread(target=self._accept_connections, daemon=True)
            self.server_thread.start()

            # Iniciar thread de heartbeat
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
            self.heartbeat_thread.start()

            return True

        except Exception as e:
            print(f"✗ Error al iniciar servidor TCP con SSL: {e}")
            import traceback
            traceback.print_exc()
            return False

    def stop(self):
        """Detiene el servidor TCP"""
        print(" Deteniendo servidor TCP...")
        self.running = False

        # Cerrar todas las conexiones de clientes
        with self.clients_lock:
            for router_nombre, (client_socket, _) in self.clients.items():
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear()

        # Cerrar socket del servidor
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        print("✓ Servidor TCP detenido")

    def _accept_connections(self):
        while self.running:
            try:
                # Aceptar conexión (ya viene cifrada por SSL)
                client_socket, address = self.server_socket.accept()

                # Obtener información del cifrado
                cipher = client_socket.cipher()
                if cipher:
                    print(f" Nueva conexión SSL desde {address}")
                    print(f"   Cifrado: {cipher[0]}, Versión: {cipher[1]}, Bits: {cipher[2]}")
                else:
                    print(f" Nueva conexión desde {address}")

                # Crear thread para manejar este cliente
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()

            except Exception as e:
                if self.running:
                    print(f"✗ Error al aceptar conexión: {e}")

    def _handle_client(self, client_socket, address):
        router_nombre = None
        buffer = ""

        try:
            while self.running:
                # Recibir datos cifrados (SSL los descifra automáticamente)
                data = client_socket.recv(4096)

                if not data:
                    # Conexión cerrada por el cliente
                    break

                # Agregar al buffer
                buffer += data.decode('utf-8')

                # Procesar mensajes completos (delimitados por \n)
                while '\n' in buffer:
                    # Extraer mensaje
                    line, buffer = buffer.split('\n', 1)

                    if line.strip():
                        # Procesar mensaje
                        try:
                            message = Message.from_json(line)
                            router_nombre = self._process_message(message, client_socket)
                        except Exception as e:
                            print(f"✗ Error al procesar mensaje: {e}")

        except ssl.SSLError as e:
            print(f"✗ Error SSL en conexión con {address}: {e}")
        except Exception as e:
            print(f"✗ Error en conexión con {address}: {e}")

        finally:
            # Limpiar conexión
            if router_nombre:
                with self.clients_lock:
                    if router_nombre in self.clients:
                        del self.clients[router_nombre]
                print(f" Router {router_nombre} desconectado")

                # Actualizar estado en BD
                if self.controlador:
                    self.controlador.cambiar_estado_router_por_nombre(router_nombre, 'Inactivo')

            try:
                client_socket.close()
            except:
                pass

    def _process_message(self, message, client_socket):

        router_nombre = message.sender

        print(f" Mensaje recibido (cifrado): {message}")

        # Procesar según tipo de mensaje
        if message.msg_type == MessageType.REGISTER:
            # Registro de router
            router_nombre = self._handle_register(message, client_socket)
            return router_nombre

        elif message.msg_type == MessageType.HEARTBEAT:
            # Heartbeat
            self._handle_heartbeat(message, client_socket)

        elif message.msg_type == MessageType.NEIGHBOR_UPDATE:
            # Actualización de vecinos
            self._handle_neighbor_update(message)

        elif message.msg_type == MessageType.ROUTE_REQUEST:
            # Solicitud de ruta
            self._handle_route_request(message, client_socket)

        elif message.msg_type == MessageType.DISCONNECT:
            # Desconexión
            print(f" Router {router_nombre} solicitó desconexión")

        else:
            print(f" Tipo de mensaje no manejado: {message.msg_type}")

        return router_nombre

    def _handle_register(self, message, client_socket):
        """Maneja el registro de un router"""
        payload = message.payload
        router_id = payload.get('router_id')
        router_nombre = payload.get('router_nombre')
        router_ip = payload.get('router_ip')

        print(f" Registrando router: {router_nombre} (ID: {router_id}, IP: {router_ip})")

        success = False
        msg = ""

        try:
            if self.controlador:
                # Verificar si el router existe
                router = self.controlador.obtener_router(router_id)

                if router:
                    # Actualizar router existente
                    self.controlador.actualizar_router(
                        router_id,
                        nombre=router_nombre,
                        ip=router_ip,
                        estado='Activo'
                    )
                    msg = "Router actualizado y activado"
                else:
                    # Crear nuevo router
                    new_id = self.controlador.crear_router(router_nombre, router_ip, 'Activo')
                    if new_id:
                        router_id = new_id
                    msg = "Router registrado exitosamente"

                success = True

                # Guardar conexión
                with self.clients_lock:
                    self.clients[router_nombre] = (client_socket, threading.current_thread())

                # Enviar rutas iniciales al router
                self._send_initial_routes(router_id, client_socket)

        except Exception as e:
            msg = f"Error al registrar router: {e}"
            print(f"✗ {msg}")

        # Enviar confirmación (cifrada automáticamente por SSL)
        ack = MessageFactory.create_register_ack(router_nombre, success, msg)
        self._send_message(client_socket, ack)

        return router_nombre

    def _handle_heartbeat(self, message, client_socket):
        router_nombre = message.sender

        # Actualizar timestamp
        with self.clients_lock:
            if router_nombre in self.clients:
                # Actualizar última actividad
                pass

        # Enviar ACK
        ack = MessageFactory.create_heartbeat_ack(router_nombre)
        self._send_message(client_socket, ack)

    def _handle_neighbor_update(self, message):

        router_nombre = message.sender
        vecinos = message.payload.get('vecinos', [])

        print(f"Actualización de vecinos de {router_nombre}: {len(vecinos)} vecinos")

        if self.controlador:
            pass

    def _handle_route_request(self, message, client_socket):

        router_nombre = message.sender
        destino = message.payload.get('destino')

        print(f" Solicitud de ruta desde {router_nombre} hacia {destino}")

        if self.controlador:
            # Calcular ruta
            router_origen = self.controlador.obtener_router_por_nombre(router_nombre)
            router_destino = self.controlador.obtener_router_por_ip(destino)

            if router_origen and router_destino:
                ruta = self.controlador.calcular_ruta(
                    router_origen.id_router,
                    router_destino.id_router,
                    guardar=False
                )

                if ruta:
                    ruta_info = {
                        'destino': destino,
                        'next_hop': None,  # Calcular next hop
                        'costo': ruta.costo_total,
                        'camino': ruta.camino
                    }

                    response = MessageFactory.create_route_response(router_nombre, ruta_info)
                    self._send_message(client_socket, response)

    def _send_initial_routes(self, router_id, client_socket):
        """Envía rutas iniciales a un router recién conectado"""
        if not self.controlador:
            return

        try:
            # Obtener router
            router = self.controlador.obtener_router(router_id)
            if not router:
                return

            # Calcular o obtener rutas para este router
            rutas = self.controlador.listar_rutas_desde(router_id)

            if not rutas:
                # No hay rutas, calcularlas
                self.controlador.recalcular_rutas_router(router_id)
                rutas = self.controlador.listar_rutas_desde(router_id)

            # Convertir rutas a formato para envío
            rutas_data = []
            for ruta in rutas:
                router_destino = self.controlador.obtener_router(ruta.router_destino)
                if router_destino:
                    # Obtener next hop (primer salto después del origen)
                    camino = ruta.obtener_saltos()
                    next_hop_id = camino[1] if len(camino) > 1 else None

                    if next_hop_id:
                        next_hop_router = self.controlador.obtener_router(next_hop_id)

                        rutas_data.append({
                            'destino': router_destino.ip,
                            'next_hop': next_hop_router.ip if next_hop_router else None,
                            'interfaz_salida': f"eth_to_R{next_hop_id}",
                            'costo': ruta.costo_total,
                            'origen_info': 'Controlador'
                        })

            # Enviar mensaje con rutas (cifrado automáticamente por SSL)
            if rutas_data:
                message = MessageFactory.create_route_update(router.nombre, rutas_data)
                self._send_message(client_socket, message)
                print(f"✓ {len(rutas_data)} rutas enviadas a {router.nombre} (cifradas)")

        except Exception as e:
            print(f"✗ Error al enviar rutas iniciales: {e}")

    def _send_message(self, client_socket, message):
        try:
            # SSL cifra automáticamente
            client_socket.sendall(message.to_bytes())
        except Exception as e:
            print(f"✗ Error al enviar mensaje: {e}")

    def broadcast_route_update(self, rutas_por_router):

        with self.clients_lock:
            for router_nombre, (client_socket, _) in self.clients.items():
                if router_nombre in rutas_por_router:
                    rutas = rutas_por_router[router_nombre]
                    message = MessageFactory.create_route_update(router_nombre, rutas)
                    self._send_message(client_socket, message)

    def _heartbeat_monitor(self):
        """Thread que monitorea heartbeats"""
        while self.running:
            time.sleep(self.heartbeat_interval)

            # Aquí podrías verificar routers que no han enviado heartbeat
            # y marcarlos como inactivos

    def get_connected_routers(self):
        with self.clients_lock:
            return list(self.clients.keys())