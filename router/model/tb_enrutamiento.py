class TbEnrutamiento:
    def __init__(self, id_ruta=None, destino=None, next_hop=None,
                 interfaz_salida=None, costo_total=0.0, origen_info='Interna'):
        self.id_ruta = id_ruta
        self.destino = destino
        self.next_hop = next_hop
        self.interfaz_salida = interfaz_salida
        self.costo_total = costo_total
        self.origen_info = origen_info

    def __str__(self):
        return f"Ruta({self.destino} via {self.next_hop}, Costo: {self.costo_total})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id_ruta': self.id_ruta,
            'destino': self.destino,
            'next_hop': self.next_hop,
            'interfaz_salida': self.interfaz_salida,
            'costo_total': self.costo_total,
            'origen_info': self.origen_info
        }

    @staticmethod
    def from_tuple(data):
        """Crea un objeto TbEnrutamiento desde una tupla de BD"""
        if data:
            return TbEnrutamiento(
                id_ruta=data[0],
                destino=data[1],
                next_hop=data[2],
                interfaz_salida=data[3],
                costo_total=data[4],
                origen_info=data[5]
            )
        return None

    def es_ruta_directa(self):
        """Verifica si es una ruta directa (costo 0 o muy bajo)"""
        return self.costo_total <= 1.0

    def es_desde_controlador(self):
        """Verifica si la ruta proviene del controlador SDN"""
        return self.origen_info == 'Controlador'