from router.config.database import Database
from router.model.mensaje import Mensaje

class MensajeDAO:
    """Clase para acceso a datos de Mensajes"""

    def __init__(self):
        self.db = Database()

    def crear(self, mensaje):
        """
        Crea un nuevo mensaje en la base de datos

        Args:
            mensaje: Objeto Mensaje

        Returns:
            ID del mensaje creado o None si falla
        """
        query = """
            INSERT INTO Mensajes (tipo, emisor, receptor, contenido, fecha_hora)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (mensaje.tipo, mensaje.emisor, mensaje.receptor,
                  mensaje.contenido, mensaje.fecha_hora)

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            mensaje_id = cursor.lastrowid
            cursor.close()
            return mensaje_id
        except Exception as e:
            print(f" Error al crear mensaje: {e}")
            return None

    def registrar_mensaje(self, tipo, emisor, receptor, contenido):
        """
        Método simplificado para registrar un mensaje

        Args:
            tipo: Tipo de mensaje
            emisor: Emisor del mensaje
            receptor: Receptor del mensaje
            contenido: Contenido del mensaje

        Returns:
            ID del mensaje creado
        """
        mensaje = Mensaje(tipo=tipo, emisor=emisor, receptor=receptor, contenido=contenido)
        return self.crear(mensaje)

    def obtener_por_id(self, id_mensaje):
        """
        Obtiene un mensaje por su ID

        Args:
            id_mensaje: ID del mensaje

        Returns:
            Objeto Mensaje o None
        """
        query = "SELECT * FROM Mensajes WHERE id_mensaje = %s"
        result = self.db.fetch_one(query, (id_mensaje,))
        return Mensaje.from_tuple(result)

    def obtener_todos(self, limite=100):
        """
        Obtiene los mensajes más recientes

        Args:
            limite: Número máximo de mensajes

        Returns:
            Lista de objetos Mensaje
        """
        query = """
            SELECT * FROM Mensajes 
            ORDER BY fecha_hora DESC 
            LIMIT %s
        """
        results = self.db.fetch_all(query, (limite,))
        return [Mensaje.from_tuple(row) for row in results]

    def obtener_por_tipo(self, tipo, limite=50):
        """
        Obtiene mensajes de un tipo específico

        Args:
            tipo: Tipo de mensaje
            limite: Número máximo de mensajes

        Returns:
            Lista de objetos Mensaje
        """
        query = """
            SELECT * FROM Mensajes 
            WHERE tipo = %s
            ORDER BY fecha_hora DESC 
            LIMIT %s
        """
        results = self.db.fetch_all(query, (tipo, limite))
        return [Mensaje.from_tuple(row) for row in results]

    def obtener_por_emisor(self, emisor, limite=50):
        """
        Obtiene mensajes de un emisor específico

        Args:
            emisor: Emisor a buscar
            limite: Número máximo de mensajes

        Returns:
            Lista de objetos Mensaje
        """
        query = """
            SELECT * FROM Mensajes 
            WHERE emisor = %s
            ORDER BY fecha_hora DESC 
            LIMIT %s
        """
        results = self.db.fetch_all(query, (emisor, limite))
        return [Mensaje.from_tuple(row) for row in results]

    def obtener_por_receptor(self, receptor, limite=50):
        """
        Obtiene mensajes para un receptor específico

        Args:
            receptor: Receptor a buscar
            limite: Número máximo de mensajes

        Returns:
            Lista de objetos Mensaje
        """
        query = """
            SELECT * FROM Mensajes 
            WHERE receptor = %s
            ORDER BY fecha_hora DESC 
            LIMIT %s
        """
        results = self.db.fetch_all(query, (receptor, limite))
        return [Mensaje.from_tuple(row) for row in results]

    def obtener_conversacion(self, router1, router2, limite=50):
        """
        Obtiene la conversación entre dos routers

        Args:
            router1: Primer router
            router2: Segundo router
            limite: Número máximo de mensajes

        Returns:
            Lista de objetos Mensaje
        """
        query = """
            SELECT * FROM Mensajes 
            WHERE (emisor = %s AND receptor = %s)
               OR (emisor = %s AND receptor = %s)
            ORDER BY fecha_hora DESC 
            LIMIT %s
        """
        results = self.db.fetch_all(query, (router1, router2, router2, router1, limite))
        return [Mensaje.from_tuple(row) for row in results]

    def obtener_recientes(self, minutos=60):
        """
        Obtiene mensajes recientes de los últimos X minutos

        Args:
            minutos: Número de minutos hacia atrás

        Returns:
            Lista de objetos Mensaje
        """
        query = """
            SELECT * FROM Mensajes 
            WHERE fecha_hora >= DATE_SUB(NOW(), INTERVAL %s MINUTE)
            ORDER BY fecha_hora DESC
        """
        results = self.db.fetch_all(query, (minutos,))
        return [Mensaje.from_tuple(row) for row in results]

    def eliminar(self, id_mensaje):
        """
        Elimina un mensaje

        Args:
            id_mensaje: ID del mensaje a eliminar

        Returns:
            True si la eliminación fue exitosa
        """
        query = "DELETE FROM Mensajes WHERE id_mensaje = %s"
        return self.db.execute_query(query, (id_mensaje,))

    def limpiar_mensajes_antiguos(self, dias=30):
        """
        Elimina mensajes más antiguos que X días

        Args:
            dias: Número de días

        Returns:
            Número de mensajes eliminados
        """
        query = """
            DELETE FROM Mensajes 
            WHERE fecha_hora < DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, (dias,))
            connection.commit()
            filas_eliminadas = cursor.rowcount
            cursor.close()
            print(f"✓ {filas_eliminadas} mensajes antiguos eliminados")
            return filas_eliminadas
        except Exception as e:
            print(f"✗ Error al limpiar mensajes antiguos: {e}")
            return 0

    def contar_mensajes(self):
        """
        Cuenta el total de mensajes

        Returns:
            Número de mensajes
        """
        query = "SELECT COUNT(*) FROM Mensajes"
        result = self.db.fetch_one(query)
        return result[0] if result else 0

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas de mensajes

        Returns:
            Diccionario con estadísticas
        """
        query = """
            SELECT 
                tipo,
                COUNT(*) as cantidad,
                MAX(fecha_hora) as ultimo_mensaje
            FROM Mensajes
            GROUP BY tipo
            ORDER BY cantidad DESC
        """
        results = self.db.fetch_all(query)

        estadisticas = {}
        for row in results:
            estadisticas[row[0]] = {
                'cantidad': row[1],
                'ultimo_mensaje': row[2]
            }
        return estadisticas