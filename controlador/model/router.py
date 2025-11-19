from datetime import datetime


class Router:
    """Clase que representa un router en la topología"""

    def __init__(self, id_router=None, nombre=None, ip=None,
                 estado='Activo', ultima_actualizacion=None):
        self.id_router = id_router
        self.nombre = nombre
        self.ip = ip
        self.estado = estado
        self.ultima_actualizacion = ultima_actualizacion or datetime.now()

    def __str__(self):
        return f"Router({self.nombre}, IP: {self.ip}, Estado: {self.estado})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id_router,
            'id_router': self.id_router,
            'nombre': self.nombre,
            'ip': self.ip,
            'estado': self.estado,
            'ultima_actualizacion': self.ultima_actualizacion
        }

    @staticmethod
    def from_tuple(data):
        """Crea un objeto Router desde una tupla de BD"""
        if data:
            return Router(
                id_router=data[0],
                nombre=data[1],
                ip=data[2],
                estado=data[3],
                ultima_actualizacion=data[4]
            )
        return None

    def es_activo(self):
        """Verifica si el router está activo"""
        return self.estado == 'Activo'