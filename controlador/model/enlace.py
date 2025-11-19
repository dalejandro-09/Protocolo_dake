class Enlace:
    """Clase que representa un enlace entre dos routers"""

    def __init__(self, id_enlace=None, router_origen=None, router_destino=None,
                 costo=1.0, ancho_banda=None, estado='Activo', retardo_ms=None):
        self.id_enlace = id_enlace
        self.router_origen = router_origen
        self.router_destino = router_destino
        self.costo = costo
        self.ancho_banda = ancho_banda
        self.estado = estado
        self.retardo_ms = retardo_ms

    def __str__(self):
        return f"Enlace(R{self.router_origen} -> R{self.router_destino}, Costo: {self.costo}, Estado: {self.estado})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id_enlace': self.id_enlace,
            'router_origen': self.router_origen,
            'router_destino': self.router_destino,
            'costo': self.costo,
            'ancho_banda': self.ancho_banda,
            'estado': self.estado,
            'retardo_ms': self.retardo_ms
        }

    @staticmethod
    def from_tuple(data):
        """Crea un objeto Enlace desde una tupla de BD"""
        if data:
            return Enlace(
                id_enlace=data[0],
                router_origen=data[1],
                router_destino=data[2],
                costo=data[3],
                ancho_banda=data[4],
                estado=data[5],
                retardo_ms=data[6]
            )
        return None

    def es_activo(self):
        """Verifica si el enlace está activo"""
        return self.estado == 'Activo'

    def calcular_metrica(self):
        """Calcula métrica considerando costo y retardo"""
        metrica = self.costo
        if self.retardo_ms:
            metrica += (self.retardo_ms / 1000.0)  # Sumar retardo en segundos
        return metrica