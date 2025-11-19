import mysql.connector
from mysql.connector import Error
from router.config.settings import DB_CONFIG

class Database:
    """Clase para gestionar la conexión a router_db"""

    _instance = None
    _connection = None

    def __new__(cls):
        """Patrón Singleton para una única conexión"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """Establece la conexión con la base de datos"""
        try:
            if self._connection is None or not self._connection.is_connected():
                self._connection = mysql.connector.connect(**DB_CONFIG)
                print("✓ Conexión exitosa a router_db")
            return self._connection
        except Error as e:
            print(f"✗ Error al conectar a router_db: {e}")
            return None

    def disconnect(self):
        """Cierra la conexión con la base de datos"""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            print("✓ Conexión cerrada con router_db")

    def get_connection(self):
        """Obtiene la conexión activa"""
        if self._connection is None or not self._connection.is_connected():
            return self.connect()
        return self._connection

    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta SQL (INSERT, UPDATE, DELETE)

        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros de la consulta

        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"✗ Error al ejecutar query: {e}")
            return False

    def fetch_all(self, query, params=None):
        """
        Ejecuta una consulta SELECT y retorna todos los resultados

        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros de la consulta

        Returns:
            Lista de tuplas con los resultados
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"✗ Error al ejecutar query: {e}")
            return []

    def fetch_one(self, query, params=None):
        """
        Ejecuta una consulta SELECT y retorna un solo resultado

        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros de la consulta

        Returns:
            Tupla con el resultado o None
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"✗ Error al ejecutar query: {e}")
            return None