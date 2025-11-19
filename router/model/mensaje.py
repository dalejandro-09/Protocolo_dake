from datetime import datetime

class Mensaje:
    """Clase que representa un mensaje OSPF"""

    def __init__(self, id_mensaje=None, tipo=None, emisor=None,
                 receptor=None, contenido=None, fecha_hora=None):
        self.id_mensaje = id_mensaje
        self.tipo = tipo
        self.emisor = emisor
        self.receptor = receptor
        self.contenido = contenido
        self.fecha_hora = fecha_hora or datetime.now()

    def __str__(self):
        return f"Mensaje({self.tipo}, {self.emisor} -> {self.receptor})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id_mensaje': self.id_mensaje,
            'tipo': self.tipo,
            'emisor': self.emisor,
            'receptor': self.receptor,
            'contenido': self.contenido,
            'fecha_hora': self.fecha_hora
        }

    @staticmethod
    def from_tuple(data):
        """Crea un objeto Mensaje desde una tupla de BD"""
        if data:
            return Mensaje(
                id_mensaje=data[0],
                tipo=data[1],
                emisor=data[2],
                receptor=data[3],
                contenido=data[4],
                fecha_hora=data[5]
            )
        return None

    def es_hello(self):
        """Verifica si es un mensaje HELLO"""
        return self.tipo == 'HELLO'

    def es_lsa(self):
        """Verifica si es un mensaje LSA (Link State Advertisement)"""
        return self.tipo == 'LSA'

    def es_control(self):
        """Verifica si es un mensaje de control del SDN"""
        return self.tipo in ['START', 'ACK', 'UPDATE', 'FAIL']