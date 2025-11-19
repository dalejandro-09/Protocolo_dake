from router.config.database import Database
from router.model.vecino import Vecino

class VecinoDAO:
    def __init__(self):
        self.db = Database()

    def crear(self, vecino):
        """
        Crea un nuevo vecino en la base de datos

        Args:
            vecino: Objeto Vecino

        Returns:
            ID del vecino creado o None si falla
        """
        query = """
            INSERT INTO Vecino (router_vecino, ip_vecino, estado_vecino, 
                               costo_enlace, tiempo_ultimo_hello)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (vecino.router_vecino, vecino.ip_vecino, vecino.estado_vecino,
                  vecino.costo_enlace, vecino.tiempo_ultimo_hello)

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            vecino_id = cursor.lastrowid
            cursor.close()
            print(f"✓ Vecino '{vecino.router_vecino}' agregado con ID: {vecino_id}")
            return vecino_id
        except Exception as e:
            print(f"✗ Error al crear vecino: {e}")
            return None

    def obtener_por_id(self, id_vecino):
        """
        Obtiene un vecino por su ID

        Args:
            id_vecino: ID del vecino

        Returns:
            Objeto Vecino o None
        """
        query = "SELECT * FROM Vecino WHERE id_vecino = %s"
        result = self.db.fetch_one(query, (id_vecino,))
        return Vecino.from_tuple(result)

    def obtener_por_nombre(self, router_vecino):
        """
        Obtiene un vecino por su nombre

        Args:
            router_vecino: Nombre del router vecino

        Returns:
            Objeto Vecino o None
        """
        query = "SELECT * FROM Vecino WHERE router_vecino = %s"
        result = self.db.fetch_one(query, (router_vecino,))
        return Vecino.from_tuple(result)

    def obtener_por_ip(self, ip_vecino):
        """
        Obtiene un vecino por su IP

        Args:
            ip_vecino: IP del vecino

        Returns:
            Objeto Vecino o None
        """
        query = "SELECT * FROM Vecino WHERE ip_vecino = %s"
        result = self.db.fetch_one(query, (ip_vecino,))
        return Vecino.from_tuple(result)

    def obtener_todos(self):
        """
        Obtiene todos los vecinos

        Returns:
            Lista de objetos Vecino
        """
        query = "SELECT * FROM Vecino ORDER BY id_vecino"
        results = self.db.fetch_all(query)
        return [Vecino.from_tuple(row) for row in results]

    def obtener_activos(self):
        """
        Obtiene todos los vecinos en estado Full o 2-Way

        Returns:
            Lista de objetos Vecino activos
        """
        query = "SELECT * FROM Vecino WHERE estado_vecino IN ('Full', '2-Way') ORDER BY id_vecino"
        results = self.db.fetch_all(query)
        return [Vecino.from_tuple(row) for row in results]

    def obtener_por_estado(self, estado):
        """
        Obtiene vecinos por estado

        Args:
            estado: Estado del vecino

        Returns:
            Lista de objetos Vecino
        """
        query = "SELECT * FROM Vecino WHERE estado_vecino = %s ORDER BY id_vecino"
        results = self.db.fetch_all(query, (estado,))
        return [Vecino.from_tuple(row) for row in results]

    def actualizar(self, vecino):
        """
        Actualiza un vecino existente

        Args:
            vecino: Objeto Vecino con datos actualizados

        Returns:
            True si la actualización fue exitosa
        """
        query = """
            UPDATE Vecino 
            SET router_vecino = %s, ip_vecino = %s, estado_vecino = %s,
                costo_enlace = %s, tiempo_ultimo_hello = %s
            WHERE id_vecino = %s
        """
        params = (vecino.router_vecino, vecino.ip_vecino, vecino.estado_vecino,
                  vecino.costo_enlace, vecino.tiempo_ultimo_hello, vecino.id_vecino)

        if self.db.execute_query(query, params):
            print(f"✓ Vecino ID {vecino.id_vecino} actualizado")
            return True
        return False

    def actualizar_tiempo_hello(self, id_vecino):
        """
        Actualiza el tiempo del último HELLO recibido

        Args:
            id_vecino: ID del vecino

        Returns:
            True si la actualización fue exitosa
        """
        query = """
            UPDATE Vecino 
            SET tiempo_ultimo_hello = NOW()
            WHERE id_vecino = %s
        """
        return self.db.execute_query(query, (id_vecino,))

    def cambiar_estado(self, id_vecino, nuevo_estado):
        """
        Cambia el estado de un vecino

        Args:
            id_vecino: ID del vecino
            nuevo_estado: Nuevo estado

        Returns:
            True si el cambio fue exitoso
        """
        query = """
            UPDATE Vecino 
            SET estado_vecino = %s, tiempo_ultimo_hello = NOW()
            WHERE id_vecino = %s
        """
        if self.db.execute_query(query, (nuevo_estado, id_vecino)):
            print(f"✓ Estado del vecino ID {id_vecino} cambiado a '{nuevo_estado}'")
            return True
        return False

    def eliminar(self, id_vecino):
        """
        Elimina un vecino

        Args:
            id_vecino: ID del vecino a eliminar

        Returns:
            True si la eliminación fue exitosa
        """
        query = "DELETE FROM Vecino WHERE id_vecino = %s"
        if self.db.execute_query(query, (id_vecino,)):
            print(f"✓ Vecino ID {id_vecino} eliminado")
            return True
        return False

    def contar_vecinos(self):
        """
        Cuenta el total de vecinos

        Returns:
            Número de vecinos
        """
        query = "SELECT COUNT(*) FROM Vecino"
        result = self.db.fetch_one(query)
        return result[0] if result else 0

    def existe_vecino(self, router_vecino=None, ip_vecino=None):
        """
        Verifica si ya existe un vecino con ese nombre o IP

        Args:
            router_vecino: Nombre del router vecino
            ip_vecino: IP del vecino

        Returns:
            True si el vecino existe
        """
        if router_vecino:
            query = "SELECT COUNT(*) FROM Vecino WHERE router_vecino = %s"
            result = self.db.fetch_one(query, (router_vecino,))
        elif ip_vecino:
            query = "SELECT COUNT(*) FROM Vecino WHERE ip_vecino = %s"
            result = self.db.fetch_one(query, (ip_vecino,))
        else:
            return False

        return result[0] > 0 if result else False

    def obtener_vecinos_caidos(self, timeout_segundos=40):
        """
        Obtiene vecinos que no han enviado HELLO en un tiempo determinado

        Args:
            timeout_segundos: Tiempo sin HELLO para considerar caído

        Returns:
            Lista de vecinos caídos
        """
        query = """
            SELECT * FROM Vecino 
            WHERE TIMESTAMPDIFF(SECOND, tiempo_ultimo_hello, NOW()) > %s
            AND estado_vecino != 'Down'
        """
        results = self.db.fetch_all(query, (timeout_segundos,))
        return [Vecino.from_tuple(row) for row in results]