from datetime import datetime

class Vecino:
    """Clase que representa un vecino del router"""

    def __init__(self, id_vecino=None, router_vecino=None, ip_vecino=None,
                 estado_vecino='Down', costo_enlace=1.0, tiempo_ultimo_hello=None):
        self.id_vecino = id_vecino
        self.router_vecino = router_vecino
        self.ip_vecino = ip_vecino
        self.estado_vecino = estado_vecino
        self.costo_enlace = costo_enlace
        self.tiempo_ultimo_hello = tiempo_ultimo_hello or datetime.now()

    def __str__(self):
        return f"Vecino({self.router_vecino}, IP: {self.ip_vecino}, Estado: {self.estado_vecino})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id_vecino': self.id_vecino,
            'router_vecino': self.router_vecino,
            'ip_vecino': self.ip_vecino,
            'estado_vecino': self.estado_vecino,
            'costo_enlace': self.costo_enlace,
            'tiempo_ultimo_hello': self.tiempo_ultimo_hello
        }

    @staticmethod
    def from_tuple(data):
        """Crea un objeto Vecino desde una tupla de BD"""
        if data:
            return Vecino(
                id_vecino=data[0],
                router_vecino=data[1],
                ip_vecino=data[2],
                estado_vecino=data[3],
                costo_enlace=data[4],
                tiempo_ultimo_hello=data[5]
            )
        return None

    def esta_activo(self):
        """Verifica si el vecino está en estado Full o 2-Way"""
        return self.estado_vecino in ['Full', '2-Way']

    def tiempo_sin_hello(self):
        """Calcula el tiempo transcurrido desde el último HELLO en segundos"""
        if self.tiempo_ultimo_hello:
            delta = datetime.now() - self.tiempo_ultimo_hello
            return delta.total_seconds()
        return 0