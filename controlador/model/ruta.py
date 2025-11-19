from datetime import datetime

class Ruta:
    """Clase que representa una ruta calculada"""

    def __init__(self, id_ruta=None, router_origen=None, router_destino=None,
                 camino=None, costo_total=0.0, fecha_calculo=None):
        self.id_ruta = id_ruta
        self.router_origen = router_origen
        self.router_destino = router_destino
        self.camino = camino  # String con formato "R1->R3->R5"
        self.costo_total = costo_total
        self.fecha_calculo = fecha_calculo or datetime.now()

    def __str__(self):
        return f"Ruta(R{self.router_origen} -> R{self.router_destino}, Camino: {self.camino}, Costo: {self.costo_total})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id_ruta': self.id_ruta,
            'router_origen': self.router_origen,
            'router_destino': self.router_destino,
            'camino': self.camino,
            'costo_total': self.costo_total,
            'fecha_calculo': self.fecha_calculo
        }

    @staticmethod
    def from_tuple(data):
        """Crea un objeto Ruta desde una tupla de BD"""
        if data:
            return Ruta(
                id_ruta=data[0],
                router_origen=data[1],
                router_destino=data[2],
                camino=data[3],
                costo_total=data[4],
                fecha_calculo=data[5]
            )
        return None

    def obtener_saltos(self):
        """Retorna lista de IDs de routers en el camino"""
        if self.camino:
            # Asume formato "R1->R3->R5"
            return [int(r.replace('R', '')) for r in self.camino.split('->')]
        return []

    def numero_saltos(self):
        """Retorna el número de saltos en la ruta"""
        return len(self.obtener_saltos()) - 1