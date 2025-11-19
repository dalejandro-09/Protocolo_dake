from router.config.database import Database
from router.model.log_router import LogRouter

class LogRouterDAO:
    """Clase para acceso a datos de Log_Router"""

    def __init__(self):
        self.db = Database()

    def crear(self, log):
        """
        Crea un nuevo log en la base de datos

        Args:
            log: Objeto LogRouter

        Returns:
            ID del log creado o None si falla
        """
        query = """
            INSERT INTO Log_Router (evento, detalle, fecha_hora)
            VALUES (%s, %s, %s)
        """
        params = (log.evento, log.detalle, log.fecha_hora)

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            log_id = cursor.lastrowid
            cursor.close()
            return log_id
        except Exception as e:
            print(f" Error al crear log: {e}")
            return None

    def registrar_evento(self, evento, detalle=None):
        """
        Método simplificado para registrar un evento

        Args:
            evento: Descripción del evento
            detalle: Detalles adicionales del evento

        Returns:
            ID del log creado
        """
        log = LogRouter(evento=evento, detalle=detalle)
        return self.crear(log)

    def obtener_por_id(self, id_log):
        """
        Obtiene un log por su ID

        Args:
            id_log: ID del log

        Returns:
            Objeto LogRouter o None
        """
        query = "SELECT * FROM Log_Router WHERE id_log = %s"
        result = self.db.fetch_one(query, (id_log,))
        return LogRouter.from_tuple(result)

    def obtener_todos(self, limite=100):
        """
        Obtiene los logs más recientes

        Args:
            limite: Número máximo de logs

        Returns:
            Lista de objetos LogRouter
        """
        query = """
            SELECT * FROM Log_Router 
            ORDER BY fecha_hora DESC 
            LIMIT %s
        """
        results = self.db.fetch_all(query, (limite,))
        return [LogRouter.from_tuple(row) for row in results]

    def obtener_por_evento(self, evento, limite=50):
        """
        Obtiene logs de un tipo de evento específico

        Args:
            evento: Tipo de evento a buscar
            limite: Número máximo de logs

        Returns:
            Lista de objetos LogRouter
        """
        query = """
            SELECT * FROM Log_Router 
            WHERE evento LIKE %s
            ORDER BY fecha_hora DESC 
            LIMIT %s
        """
        results = self.db.fetch_all(query, (f"%{evento}%", limite))
        return [LogRouter.from_tuple(row) for row in results]

    def obtener_por_fecha(self, fecha_inicio, fecha_fin):
        """
        Obtiene logs en un rango de fechas

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin

        Returns:
            Lista de objetos LogRouter
        """
        query = """
            SELECT * FROM Log_Router 
            WHERE fecha_hora BETWEEN %s AND %s
            ORDER BY fecha_hora DESC
        """
        results = self.db.fetch_all(query, (fecha_inicio, fecha_fin))
        return [LogRouter.from_tuple(row) for row in results]

    def obtener_recientes(self, minutos=60):
        """
        Obtiene logs recientes de los últimos X minutos

        Args:
            minutos: Número de minutos hacia atrás

        Returns:
            Lista de objetos LogRouter
        """
        query = """
            SELECT * FROM Log_Router 
            WHERE fecha_hora >= DATE_SUB(NOW(), INTERVAL %s MINUTE)
            ORDER BY fecha_hora DESC
        """
        results = self.db.fetch_all(query, (minutos,))
        return [LogRouter.from_tuple(row) for row in results]

    def eliminar(self, id_log):
        """
        Elimina un log

        Args:
            id_log: ID del log a eliminar

        Returns:
            True si la eliminación fue exitosa
        """
        query = "DELETE FROM Log_Router WHERE id_log = %s"
        return self.db.execute_query(query, (id_log,))

    def limpiar_logs_antiguos(self, dias=30):
        """
        Elimina logs más antiguos que X días

        Args:
            dias: Número de días

        Returns:
            Número de logs eliminados
        """
        query = """
            DELETE FROM Log_Router 
            WHERE fecha_hora < DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, (dias,))
            connection.commit()
            filas_eliminadas = cursor.rowcount
            cursor.close()
            print(f"✓ {filas_eliminadas} logs antiguos eliminados")
            return filas_eliminadas
        except Exception as e:
            print(f"Error al limpiar logs antiguos: {e}")
            return 0

    def contar_logs(self):
        """
        Cuenta el total de logs

        Returns:
            Número de logs
        """
        query = "SELECT COUNT(*) FROM Log_Router"
        result = self.db.fetch_one(query)
        return result[0] if result else 0

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas de eventos registrados

        Returns:
            Diccionario con estadísticas
        """
        query = """
            SELECT 
                evento,
                COUNT(*) as cantidad,
                MAX(fecha_hora) as ultimo_evento
            FROM Log_Router
            GROUP BY evento
            ORDER BY cantidad DESC
        """
        results = self.db.fetch_all(query)

        estadisticas = {}
        for row in results:
            estadisticas[row[0]] = {
                'cantidad': row[1],
                'ultimo_evento': row[2]
            }
        return estadisticas