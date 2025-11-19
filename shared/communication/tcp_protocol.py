import json
from enum import Enum
from datetime import datetime

class MessageType(Enum):
    # Mensajes de control
    REGISTER = "REGISTER"  # Router se registra en el controlador
    REGISTER_ACK = "REGISTER_ACK"  # Confirmación de registro
    HEARTBEAT = "HEARTBEAT"  # Mensaje de keep-alive
    HEARTBEAT_ACK = "HEARTBEAT_ACK"  # Confirmación de heartbeat
    DISCONNECT = "DISCONNECT"  # Desconexión voluntaria

    # Mensajes de topología
    NEIGHBOR_UPDATE = "NEIGHBOR_UPDATE"  # Router notifica vecinos
    LINK_STATE = "LINK_STATE"  # Estado de enlaces
    TOPOLOGY_UPDATE = "TOPOLOGY_UPDATE"  # Controlador envía topología

    # Mensajes de enrutamiento
    ROUTE_UPDATE = "ROUTE_UPDATE"  # Controlador envía rutas
    ROUTE_REQUEST = "ROUTE_REQUEST"  # Router solicita ruta
    ROUTE_RESPONSE = "ROUTE_RESPONSE"  # Respuesta con ruta

    # Mensajes de error
    ERROR = "ERROR"  # Mensaje de error
    NACK = "NACK"  # Negative acknowledgment


class Message:
    """Clase para representar un mensaje del protocolo"""

    def __init__(self, msg_type, sender, receiver, payload=None):
        """
        Inicializa un mensaje

        Args:
            msg_type: Tipo de mensaje (MessageType)
            sender: Identificador del emisor
            receiver: Identificador del receptor
            payload: Datos del mensaje (diccionario)
        """
        self.msg_type = msg_type if isinstance(msg_type, MessageType) else MessageType(msg_type)
        self.sender = sender
        self.receiver = receiver
        self.payload = payload or {}
        self.timestamp = datetime.now().isoformat()

    def to_json(self):
        """
        Serializa el mensaje a JSON

        Returns:
            String JSON del mensaje
        """
        data = {
            'type': self.msg_type.value,
            'sender': self.sender,
            'receiver': self.receiver,
            'payload': self.payload,
            'timestamp': self.timestamp
        }
        return json.dumps(data)

    def to_bytes(self):
        """
        Convierte el mensaje a bytes para envío por socket

        Returns:
            Bytes del mensaje con delimitador
        """
        json_str = self.to_json()
        # Agregar delimitador de fin de mensaje
        return (json_str + '\n').encode('utf-8')

    @staticmethod
    def from_json(json_str):
        """
        Deserializa un mensaje desde JSON

        Args:
            json_str: String JSON del mensaje

        Returns:
            Objeto Message
        """
        try:
            data = json.loads(json_str)
            return Message(
                msg_type=data['type'],
                sender=data['sender'],
                receiver=data['receiver'],
                payload=data.get('payload', {})
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Error al deserializar mensaje: {e}")

    @staticmethod
    def from_bytes(data):
        """
        Convierte bytes a objeto Message

        Args:
            data: Bytes del mensaje

        Returns:
            Objeto Message
        """
        json_str = data.decode('utf-8').strip()
        return Message.from_json(json_str)

    def __str__(self):
        return f"Message({self.msg_type.value}, {self.sender} -> {self.receiver})"

    def __repr__(self):
        return self.__str__()


class MessageFactory:
    """Fábrica para crear mensajes comunes"""

    @staticmethod
    def create_register(router_id, router_nombre, router_ip):
        """Crea mensaje de registro de router"""
        return Message(
            msg_type=MessageType.REGISTER,
            sender=router_nombre,
            receiver="CONTROLLER",
            payload={
                'router_id': router_id,
                'router_nombre': router_nombre,
                'router_ip': router_ip
            }
        )

    @staticmethod
    def create_register_ack(router_nombre, success=True, message=""):
        """Crea confirmación de registro"""
        return Message(
            msg_type=MessageType.REGISTER_ACK,
            sender="CONTROLLER",
            receiver=router_nombre,
            payload={
                'success': success,
                'message': message
            }
        )

    @staticmethod
    def create_heartbeat(router_nombre):
        """Crea mensaje de heartbeat"""
        return Message(
            msg_type=MessageType.HEARTBEAT,
            sender=router_nombre,
            receiver="CONTROLLER",
            payload={}
        )

    @staticmethod
    def create_heartbeat_ack(router_nombre):
        """Crea confirmación de heartbeat"""
        return Message(
            msg_type=MessageType.HEARTBEAT_ACK,
            sender="CONTROLLER",
            receiver=router_nombre,
            payload={}
        )

    @staticmethod
    def create_neighbor_update(router_nombre, vecinos):
        """
        Crea mensaje de actualización de vecinos

        Args:
            router_nombre: Nombre del router
            vecinos: Lista de diccionarios con info de vecinos
        """
        return Message(
            msg_type=MessageType.NEIGHBOR_UPDATE,
            sender=router_nombre,
            receiver="CONTROLLER",
            payload={
                'vecinos': vecinos
            }
        )

    @staticmethod
    def create_route_update(router_nombre, rutas):
        """
        Crea mensaje con actualización de rutas

        Args:
            router_nombre: Nombre del router destino
            rutas: Lista de diccionarios con rutas
        """
        return Message(
            msg_type=MessageType.ROUTE_UPDATE,
            sender="CONTROLLER",
            receiver=router_nombre,
            payload={
                'rutas': rutas
            }
        )

    @staticmethod
    def create_route_request(router_nombre, destino):
        """Crea solicitud de ruta"""
        return Message(
            msg_type=MessageType.ROUTE_REQUEST,
            sender=router_nombre,
            receiver="CONTROLLER",
            payload={
                'destino': destino
            }
        )

    @staticmethod
    def create_route_response(router_nombre, ruta_info):
        """Crea respuesta con ruta"""
        return Message(
            msg_type=MessageType.ROUTE_RESPONSE,
            sender="CONTROLLER",
            receiver=router_nombre,
            payload={
                'ruta': ruta_info
            }
        )

    @staticmethod
    def create_error(sender, receiver, error_msg):
        """Crea mensaje de error"""
        return Message(
            msg_type=MessageType.ERROR,
            sender=sender,
            receiver=receiver,
            payload={
                'error': error_msg
            }
        )

    @staticmethod
    def create_disconnect(router_nombre):
        """Crea mensaje de desconexión"""
        return Message(
            msg_type=MessageType.DISCONNECT,
            sender=router_nombre,
            receiver="CONTROLLER",
            payload={}
        )