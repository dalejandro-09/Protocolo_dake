import socket
import ssl
import threading
import time
import os
from datetime import datetime
from shared.communication.tcp_protocol import Message, MessageType, MessageFactory

class TCPClient:
    def __init__(self, router_id, router_nombre, router_ip,
                 controller_host='localhost', controller_port=6633, router_controller=None):

        self.router_id = router_id
        self.router_nombre = router_nombre
        self.router_ip = router_ip
        self.controller_host = controller_host
        self.controller_port = controller_port
        self.router_controller = router_controller

        self.socket = None
        self.ssl_socket = None
        self.ssl_context = None
        self.connected = False
        self.running = False

        # Threads
        self.receive_thread = None
        self.heartbeat_thread = None

        # Configuración
        self.heartbeat_interval = 20
        self.reconnect_interval = 5  # segundos

        # Rutas de certificados SSL
        self.cert_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'certs')
        self.certfile = os.path.join(self.cert_dir, 'client.crt')
        self.keyfile = os.path.join(self.cert_dir, 'client.key')
        self.ca_cert = os.path.join(self.cert_dir, 'server.crt')  # Para verificar servidor

    def _setup_ssl_context(self):
        try:
            # Crear contexto SSL con TLS (protocolo más seguro)
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

            # Para desarrollo: no verificar hostname ni certificado
            # En producción, cambiar a CERT_REQUIRED y check_hostname=True
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE

            # Configurar cifrados fuertes
            self.ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')

            print("✓ Contexto SSL del cliente configurado")
            return self.ssl_context

        except Exception as e:
            print(f"✗ Error al configurar SSL del cliente: {e}")
            return None

    def connect(self):
        """Conecta al controlador SDN con SSL"""
        try:
            # Configurar SSL
            if not self._setup_ssl_context():
                print(" No se pudo configurar SSL, intentando conexión sin cifrado...")
                return False

            # Crear socket TCP
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Envolver socket con SSL
            self.ssl_socket = self.ssl_context.wrap_socket(
                self.socket,
                server_hostname=self.controller_host  # Para SNI (Server Name Indication)
            )

            # Conectar al servidor
            self.ssl_socket.connect((self.controller_host, self.controller_port))

            self.connected = True
            self.running = True

            # Obtener información del cifrado
            cipher = self.ssl_socket.cipher()
            if cipher:
                print(f"✓ Conectado al controlador en {self.controller_host}:{self.controller_port}")
                print(f" Cifrado SSL/TLS habilitado")
                print(f"   Algoritmo: {cipher[0]}")
                print(f"   Versión TLS: {cipher[1]}")
                print(f"   Bits: {cipher[2]}")
            else:
                print(f"✓ Conectado al controlador en {self.controller_host}:{self.controller_port}")

            # Enviar mensaje de registro
            self._send_register()

            # Iniciar thread de recepción
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()

            # Iniciar thread de heartbeat
            self.heartbeat_thread = threading.Thread(target=self._send_heartbeat, daemon=True)
            self.heartbeat_thread.start()

            return True

        except ssl.SSLError as e:
            print(f"✗ Error SSL al conectar al controlador: {e}")
            self.connected = False
            return False
        except Exception as e:
            print(f"✗ Error al conectar al controlador: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Desconecta del controlador"""
        print(" Desconectando del controlador...")
        self.running = False
        self.connected = False

        # Enviar mensaje de desconexión
        if self.ssl_socket:
            try:
                disconnect_msg = MessageFactory.create_disconnect(self.router_nombre)
                self._send_message(disconnect_msg)
            except:
                pass

        # Cerrar socket SSL
        if self.ssl_socket:
            try:
                self.ssl_socket.close()
            except:
                pass

        # Cerrar socket base
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

        print("✓ Desconectado del controlador")

    def _send_register(self):

        message = MessageFactory.create_register(
            self.router_id,
            self.router_nombre,
            self.router_ip
        )
        self._send_message(message)
        print(f"📤 Mensaje de registro enviado (cifrado)")

    def _send_message(self, message):

        if not self.connected or not self.ssl_socket:
            print("✗ No hay conexión con el controlador")
            return False

        try:
            # SSL cifra automáticamente
            self.ssl_socket.sendall(message.to_bytes())
            return True
        except ssl.SSLError as e:
            print(f"✗ Error SSL al enviar mensaje: {e}")
            self.connected = False
            return False
        except Exception as e:
            print(f"✗ Error al enviar mensaje: {e}")
            self.connected = False
            return False

    def _receive_messages(self):
        """Thread que recibe mensajes del controlador (descifrados automáticamente)"""
        buffer = ""

        while self.running and self.connected:
            try:
                # Recibir datos (SSL descifra automáticamente)
                data = self.ssl_socket.recv(4096)

                if not data:
                    # Conexión cerrada por el servidor
                    print(" Conexión cerrada por el controlador")
                    self.connected = False
                    break

                # Agregar al buffer
                buffer += data.decode('utf-8')

                # Procesar mensajes completos (delimitados por \n)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)

                    if line.strip():
                        try:
                            message = Message.from_json(line)
                            self._process_message(message)
                        except Exception as e:
                            print(f"✗ Error al procesar mensaje: {e}")

            except ssl.SSLError as e:
                if self.running:
                    print(f"✗ Error SSL al recibir mensajes: {e}")
                    self.connected = False
                break
            except Exception as e:
                if self.running:
                    print(f"✗ Error al recibir mensajes: {e}")
                    self.connected = False
                break

    def _process_message(self, message):
        print(f"📨 Mensaje recibido (descifrado): {message}")

        if message.msg_type == MessageType.REGISTER_ACK:
            # Confirmación de registro
            self._handle_register_ack(message)

        elif message.msg_type == MessageType.HEARTBEAT_ACK:
            # Confirmación de heartbeat
            pass  # Solo confirma que estamos conectados

        elif message.msg_type == MessageType.ROUTE_UPDATE:
            # Actualización de rutas
            self._handle_route_update(message)

        elif message.msg_type == MessageType.ROUTE_RESPONSE:
            # Respuesta de ruta
            self._handle_route_response(message)

        elif message.msg_type == MessageType.TOPOLOGY_UPDATE:
            # Actualización de topología
            self._handle_topology_update(message)

        elif message.msg_type == MessageType.ERROR:
            # Error del controlador
            error = message.payload.get('error', 'Error desconocido')
            print(f" Error del controlador: {error}")

        else:
            print(f" Tipo de mensaje no manejado: {message.msg_type}")

    def _handle_register_ack(self, message):
        """Maneja confirmación de registro"""
        payload = message.payload
        success = payload.get('success', False)
        msg = payload.get('message', '')

        if success:
            print(f"✓ Registro exitoso: {msg}")
        else:
            print(f"✗ Registro fallido: {msg}")
            self.connected = False

    def _handle_route_update(self, message):

        rutas = message.payload.get('rutas', [])

        print(f" Actualización de rutas recibida (cifrada): {len(rutas)} rutas")

        if self.router_controller:
            # Limpiar rutas del controlador existentes
            self.router_controller.limpiar_rutas_por_origen('Controlador')

            # Agregar nuevas rutas
            contador = 0
            for ruta in rutas:
                destino = ruta.get('destino')
                next_hop = ruta.get('next_hop')
                interfaz = ruta.get('interfaz_salida', 'eth0')
                costo = ruta.get('costo', 1.0)

                if destino and next_hop:
                    ruta_id = self.router_controller.agregar_ruta(
                        destino=destino,
                        next_hop=next_hop,
                        interfaz_salida=interfaz,
                        costo_total=costo,
                        origen_info='Controlador'
                    )
                    if ruta_id:
                        contador += 1

            print(f"✓ {contador} rutas actualizadas en la tabla de enrutamiento")

    def _handle_route_response(self, message):
        """Maneja respuesta de ruta solicitada"""
        ruta_info = message.payload.get('ruta', {})
        print(f"🛣️ Ruta recibida (cifrada): {ruta_info}")

    def _handle_topology_update(self, message):
        print(f" Actualización de topología recibida (cifrada)")


    def _send_heartbeat(self):
        while self.running:
            time.sleep(self.heartbeat_interval)

            if self.connected:
                message = MessageFactory.create_heartbeat(self.router_nombre)
                if not self._send_message(message):
                    print(" Error al enviar heartbeat")
                    self.connected = False

    def send_neighbor_update(self, vecinos):
        # Convertir vecinos a formato de mensaje
        vecinos_data = []
        for vecino in vecinos:
            if vecino.esta_activo():
                vecinos_data.append({
                    'nombre': vecino.router_vecino,
                    'ip': vecino.ip_vecino,
                    'costo': vecino.costo_enlace,
                    'estado': vecino.estado_vecino
                })

        message = MessageFactory.create_neighbor_update(self.router_nombre, vecinos_data)
        self._send_message(message)
        print(f" Actualización de vecinos enviada (cifrada): {len(vecinos_data)} vecinos")

    def request_route(self, destino):

        message = MessageFactory.create_route_request(self.router_nombre, destino)
        self._send_message(message)
        print(f" Solicitud de ruta enviada (cifrada) para destino: {destino}")

    def is_connected(self):
        """Verifica si está conectado al controlador"""
        return self.connected

    def auto_reconnect(self):
        """Intenta reconectar automáticamente"""
        while self.running and not self.connected:
            print(f" Intentando reconectar en {self.reconnect_interval} segundos...")
            time.sleep(self.reconnect_interval)
            self.connect()

    def get_ssl_info(self):
        if self.ssl_socket:
            try:
                cipher = self.ssl_socket.cipher()
                version = self.ssl_socket.version()

                return {
                    'connected': self.connected,
                    'cipher_name': cipher[0] if cipher else None,
                    'cipher_version': cipher[1] if cipher else None,
                    'cipher_bits': cipher[2] if cipher else None,
                    'tls_version': version
                }
            except:
                return None
        return None