from router.dao.tb_enrutamiento_dao import TbEnrutamientoDAO
from router.dao.vecino_dao import VecinoDAO

class EnrutamientoController:
    def __init__(self):
        self.enrutamiento_dao = TbEnrutamientoDAO()
        self.vecino_dao = VecinoDAO()

    def buscar_ruta_optima(self, destino):
        """
        Busca la ruta óptima a un destino

        Args:
            destino: Dirección de destino

        Returns:
            Objeto TbEnrutamiento o None
        """
        return self.enrutamiento_dao.obtener_por_destino(destino)

    def obtener_estadisticas_rutas(self):
        """
        Obtiene estadísticas de las rutas

        Returns:
            Diccionario con estadísticas
        """
        rutas = self.enrutamiento_dao.obtener_todas()

        if not rutas:
            return {
                'total': 0,
                'por_origen': {},
                'costo_promedio': 0
            }

        # Contar por origen
        por_origen = {}
        for ruta in rutas:
            origen = ruta.origen_info
            por_origen[origen] = por_origen.get(origen, 0) + 1

        # Costo promedio
        costos = [r.costo_total for r in rutas]
        costo_promedio = sum(costos) / len(costos) if costos else 0

        return {
            'total': len(rutas),
            'por_origen': por_origen,
            'costo_promedio': costo_promedio,
            'costo_minimo': min(costos) if costos else 0,
            'costo_maximo': max(costos) if costos else 0
        }

    def validar_tabla_enrutamiento(self):
        """
        Valida la consistencia de la tabla de enrutamiento

        Returns:
            Diccionario con resultados de validación
        """
        rutas = self.enrutamiento_dao.obtener_todas()
        vecinos = self.vecino_dao.obtener_todos()

        errores = []
        advertencias = []

        # IPs de vecinos conocidos
        ips_vecinos = {v.ip_vecino for v in vecinos}

        # Validar cada ruta
        for ruta in rutas:
            # Verificar que el next_hop sea un vecino conocido (para rutas no directas)
            if ruta.costo_total > 1.0:
                if ruta.next_hop not in ips_vecinos:
                    advertencias.append(
                        f"Ruta a {ruta.destino}: next_hop {ruta.next_hop} no es un vecino conocido"
                    )

            # Verificar costos negativos
            if ruta.costo_total < 0:
                errores.append(
                    f"Ruta a {ruta.destino}: costo negativo ({ruta.costo_total})"
                )

        return {
            'valida': len(errores) == 0,
            'errores': errores,
            'advertencias': advertencias
        }

    def obtener_next_hops_mas_usados(self):
        """
        Identifica los next_hops más utilizados

        Returns:
            Lista de next_hops ordenados por uso
        """
        rutas = self.enrutamiento_dao.obtener_todas()

        uso_next_hops = {}
        for ruta in rutas:
            next_hop = ruta.next_hop
            uso_next_hops[next_hop] = uso_next_hops.get(next_hop, 0) + 1

        # Ordenar por uso
        next_hops_ordenados = sorted(
            uso_next_hops.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {'next_hop': nh, 'rutas': count}
            for nh, count in next_hops_ordenados
        ]