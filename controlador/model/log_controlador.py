from datetime import datetime

class LogControlador:
    """Clase que representa un log del controlador"""

    def __init__(self, id_log=None, evento=None, detalle=None, fecha_hora=None):
        self.id_log = id_log
        self.evento = evento
        self.detalle = detalle
        self.fecha_hora = fecha_hora or datetime.now()

    def __str__(self):
        return f"Log({self.evento}, {self.fecha_hora})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id_log': self.id_log,
            'evento': self.evento,
            'detalle': self.detalle,
            'fecha_hora': self.fecha_hora
        }

    @staticmethod
    def from_tuple(data):
        """Crea un objeto LogControlador desde una tupla de BD"""
        if data:
            return LogControlador(
                id_log=data[0],
                evento=data[1],
                detalle=data[2],
                fecha_hora=data[3]
            )
        return None