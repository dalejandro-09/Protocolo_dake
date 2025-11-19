from controlador.config.database import Database
from controlador.model.ruta import Ruta

class RutaDAO:
    """Clase para acceso a datos de Ruta"""

    def __init__(self):
        self.db = Database()

    def crear(self, ruta):
        """
        Crea una nueva ruta en la base de datos

        Args:
            ruta: Objeto Ruta

        Returns:
            ID de la ruta creada o None si falla
        """
        query = """
            INSERT INTO Ruta (router_origen, router_destino, camino, 
                            costo_total, fecha_calculo)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (ruta.router_origen, ruta.router_destino, ruta.camino,
                  ruta.costo_total, ruta.fecha_calculo)

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            ruta_id = cursor.lastrowid
            cursor.close()
            print(f"✓ Ruta creada: R{ruta.router_origen} -> R{ruta.router_destino} (ID: {ruta_id})")
            return ruta_id
        except Exception as e:
            print(f"✗ Error al crear ruta: {e}")
            return None

    def obtener_por_id(self, id_ruta):
        """
        Obtiene una ruta por su ID

        Args:
            id_ruta: ID de la ruta

        Returns:
            Objeto Ruta o None
        """
        query = "SELECT * FROM Ruta WHERE id_ruta = %s"
        result = self.db.fetch_one(query, (id_ruta,))
        return Ruta.from_tuple(result)

    def obtener_todas(self):
        """
        Obtiene todas las rutas

        Returns:
            Lista de objetos Ruta
        """
        query = "SELECT * FROM Ruta ORDER BY fecha_calculo DESC"
        results = self.db.fetch_all(query)
        return [Ruta.from_tuple(row) for row in results]

    def obtener_por_origen_destino(self, router_origen, router_destino):
        """
        Obtiene la ruta más reciente entre dos routers

        Args:
            router_origen: ID del router origen
            router_destino: ID del router destino

        Returns:
            Objeto Ruta o None
        """
        query = """
            SELECT * FROM Ruta 
            WHERE router_origen = %s AND router_destino = %s
            ORDER BY fecha_calculo DESC
            LIMIT 1
        """
        result = self.db.fetch_one(query, (router_origen, router_destino))
        return Ruta.from_tuple(result)

    def obtener_rutas_desde(self, router_origen):
        """
        Obtiene todas las rutas desde un router específico

        Args:
            router_origen: ID del router origen

        Returns:
            Lista de objetos Ruta
        """
        query = """
            SELECT * FROM Ruta 
            WHERE router_origen = %s
            ORDER BY router_destino, fecha_calculo DESC
        """
        results = self.db.fetch_all(query, (router_origen,))
        return [Ruta.from_tuple(row) for row in results]

    def obtener_rutas_hacia(self, router_destino):
        """
        Obtiene todas las rutas hacia un router específico

        Args:
            router_destino: ID del router destino

        Returns:
            Lista de objetos Ruta
        """
        query = """
            SELECT * FROM Ruta 
            WHERE router_destino = %s
            ORDER BY router_origen, fecha_calculo DESC
        """
        results = self.db.fetch_all(query, (router_destino,))
        return [Ruta.from_tuple(row) for row in results]

    def actualizar(self, ruta):
        """
        Actualiza una ruta existente

        Args:
            ruta: Objeto Ruta con datos actualizados

        Returns:
            True si la actualización fue exitosa
        """
        query = """
            UPDATE Ruta 
            SET router_origen = %s, router_destino = %s, camino = %s,
                costo_total = %s, fecha_calculo = %s
            WHERE id_ruta = %s
        """
        params = (ruta.router_origen, ruta.router_destino, ruta.camino,
                  ruta.costo_total, ruta.fecha_calculo, ruta.id_ruta)

        if self.db.execute_query(query, params):
            print(f"✓ Ruta ID {ruta.id_ruta} actualizada")
            return True
        return False

    def eliminar(self, id_ruta):
        """
        Elimina una ruta

        Args:
            id_ruta: ID de la ruta a eliminar

        Returns:
            True si la eliminación fue exitosa
        """
        query = "DELETE FROM Ruta WHERE id_ruta = %s"
        if self.db.execute_query(query, (id_ruta,)):
            print(f"✓ Ruta ID {id_ruta} eliminada")
            return True
        return False

    def eliminar_rutas_router(self, id_router):
        """
        Elimina todas las rutas asociadas a un router

        Args:
            id_router: ID del router

        Returns:
            True si la eliminación fue exitosa
        """
        query = """
            DELETE FROM Ruta 
            WHERE router_origen = %s OR router_destino = %s
        """
        if self.db.execute_query(query, (id_router, id_router)):
            print(f"✓ Rutas del router ID {id_router} eliminadas")
            return True
        return False

    def limpiar_rutas_antiguas(self, dias=30):
        """
        Elimina rutas más antiguas que X días

        Args:
            dias: Número de días

        Returns:
            Número de rutas eliminadas
        """
        query = """
            DELETE FROM Ruta 
            WHERE fecha_calculo < DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, (dias,))
            connection.commit()
            filas_eliminadas = cursor.rowcount
            cursor.close()
            print(f"✓ {filas_eliminadas} rutas antiguas eliminadas")
            return filas_eliminadas
        except Exception as e:
            print(f"✗ Error al limpiar rutas antiguas: {e}")
            return 0

    def contar_rutas(self):
        """
        Cuenta el total de rutas

        Returns:
            Número de rutas
        """
        query = "SELECT COUNT(*) FROM Ruta"
        result = self.db.fetch_one(query)
        return result[0] if result else 0