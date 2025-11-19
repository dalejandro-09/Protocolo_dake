from router.dao.vecino_dao import VecinoDAO
from router.dao.mensaje_dao import MensajeDAO

class VecinoController:
    def __init__(self):
        self.vecino_dao = VecinoDAO()
        self.mensaje_dao = MensajeDAO()

    def obtener_estadisticas_vecinos(self):
        """
        Obtiene estadísticas de los vecinos

        Returns:
            Diccionario con estadísticas
        """
        vecinos = self.vecino_dao.obtener_todos()

        if not vecinos:
            return {
                'total': 0,
                'por_estado': {},
                'costo_promedio': 0
            }

        # Contar por estado
        por_estado = {}
        for vecino in vecinos:
            estado = vecino.estado_vecino
            por_estado[estado] = por_estado.get(estado, 0) + 1

        # Costo promedio
        costos = [v.costo_enlace for v in vecinos]
        costo_promedio = sum(costos) / len(costos) if costos else 0

        return {
            'total': len(vecinos),
            'por_estado': por_estado,
            'costo_promedio': costo_promedio,
            'costo_minimo': min(costos) if costos else 0,
            'costo_maximo': max(costos) if costos else 0
        }

    def obtener_vecinos_con_problemas(self, timeout_segundos=40):
        """
        Identifica vecinos con problemas de conectividad

        Args:
            timeout_segundos: Tiempo sin HELLO para considerar problemático

        Returns:
            Lista de vecinos problemáticos
        """
        vecinos_problema = []
        vecinos = self.vecino_dao.obtener_todos()

        for vecino in vecinos:
            tiempo_sin_hello = vecino.tiempo_sin_hello()

            if tiempo_sin_hello > timeout_segundos and vecino.estado_vecino != 'Down':
                vecinos_problema.append({
                    'id': vecino.id_vecino,
                    'nombre': vecino.router_vecino,
                    'ip': vecino.ip_vecino,
                    'estado': vecino.estado_vecino,
                    'tiempo_sin_hello': tiempo_sin_hello
                })

        return vecinos_problema

    def obtener_historial_comunicacion(self, vecino_nombre, limite=20):
        """
        Obtiene el historial de comunicación con un vecino

        Args:
            vecino_nombre: Nombre del vecino
            limite: Número máximo de mensajes

        Returns:
            Lista de mensajes
        """
        # Obtener el vecino
        vecino = self.vecino_dao.obtener_por_nombre(vecino_nombre)

        if not vecino:
            return []

        # Obtener mensajes HELLO intercambiados
        mensajes = self.mensaje_dao.obtener_por_tipo('HELLO', limite * 2)

        # Filtrar solo los relacionados con este vecino
        mensajes_vecino = [
            m for m in mensajes
            if m.emisor == vecino_nombre or m.receptor == vecino_nombre
        ]

        return mensajes_vecino[:limite]