from router.config.database import Database
from router.model.tb_enrutamiento import TbEnrutamiento

class TbEnrutamientoDAO:
    def __init__(self):
        self.db = Database()

    def crear(self, ruta):
        """
        Crea una nueva entrada en la tabla de enrutamiento

        Args:
            ruta: Objeto TbEnrutamiento

        Returns:
            ID de la ruta creada o None si falla
        """
        query = """
            INSERT INTO tb_Enrutamiento (destino, next_hop, interfaz_salida,
                                        costo_total, origen_info)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (ruta.destino, ruta.next_hop, ruta.interfaz_salida,
                  ruta.costo_total, ruta.origen_info)

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            ruta_id = cursor.lastrowid
            cursor.close()
            print(f"✓ Ruta a {ruta.destino} agregada con ID: {ruta_id}")
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
            Objeto TbEnrutamiento o None
        """
        query = "SELECT * FROM tb_Enrutamiento WHERE id_ruta = %s"
        result = self.db.fetch_one(query, (id_ruta,))
        return TbEnrutamiento.from_tuple(result)

    def obtener_por_destino(self, destino):
        """
        Obtiene una ruta por destino

        Args:
            destino: Dirección de destino

        Returns:
            Objeto TbEnrutamiento o None
        """
        query = "SELECT * FROM tb_Enrutamiento WHERE destino = %s"
        result = self.db.fetch_one(query, (destino,))
        return TbEnrutamiento.from_tuple(result)

    def obtener_todas(self):
        """
        Obtiene todas las rutas de la tabla de enrutamiento

        Returns:
            Lista de objetos TbEnrutamiento
        """
        query = "SELECT * FROM tb_Enrutamiento ORDER BY costo_total"
        results = self.db.fetch_all(query)
        return [TbEnrutamiento.from_tuple(row) for row in results]

    def obtener_por_origen(self, origen_info):
        """
        Obtiene rutas por origen de información

        Args:
            origen_info: Origen ('Interna', 'Controlador', 'Externa')

        Returns:
            Lista de objetos TbEnrutamiento
        """
        query = "SELECT * FROM tb_Enrutamiento WHERE origen_info = %s ORDER BY destino"
        results = self.db.fetch_all(query, (origen_info,))
        return [TbEnrutamiento.from_tuple(row) for row in results]

    def obtener_por_next_hop(self, next_hop):
        """
        Obtiene rutas que usan un next_hop específico

        Args:
            next_hop: Next hop a buscar

        Returns:
            Lista de objetos TbEnrutamiento
        """
        query = "SELECT * FROM tb_Enrutamiento WHERE next_hop = %s ORDER BY destino"
        results = self.db.fetch_all(query, (next_hop,))
        return [TbEnrutamiento.from_tuple(row) for row in results]

    def actualizar(self, ruta):
        """
        Actualiza una entrada de la tabla de enrutamiento

        Args:
            ruta: Objeto TbEnrutamiento con datos actualizados

        Returns:
            True si la actualización fue exitosa
        """
        query = """
            UPDATE tb_Enrutamiento 
            SET destino = %s, next_hop = %s, interfaz_salida = %s,
                costo_total = %s, origen_info = %s
            WHERE id_ruta = %s
        """
        params = (ruta.destino, ruta.next_hop, ruta.interfaz_salida,
                  ruta.costo_total, ruta.origen_info, ruta.id_ruta)

        if self.db.execute_query(query, params):
            print(f"✓ Ruta ID {ruta.id_ruta} actualizada")
            return True
        return False

    def actualizar_costo(self, id_ruta, nuevo_costo):
        """
        Actualiza el costo de una ruta

        Args:
            id_ruta: ID de la ruta
            nuevo_costo: Nuevo costo

        Returns:
            True si la actualización fue exitosa
        """
        query = "UPDATE tb_Enrutamiento SET costo_total = %s WHERE id_ruta = %s"
        return self.db.execute_query(query, (nuevo_costo, id_ruta))

    def eliminar(self, id_ruta):
        """
        Elimina una ruta de la tabla de enrutamiento

        Args:
            id_ruta: ID de la ruta a eliminar

        Returns:
            True si la eliminación fue exitosa
        """
        query = "DELETE FROM tb_Enrutamiento WHERE id_ruta = %s"
        if self.db.execute_query(query, (id_ruta,)):
            print(f"✓ Ruta ID {id_ruta} eliminada")
            return True
        return False

    def eliminar_por_origen(self, origen_info):
        """
        Elimina todas las rutas de un origen específico

        Args:
            origen_info: Origen de las rutas a eliminar

        Returns:
            Número de rutas eliminadas
        """
        query = "DELETE FROM tb_Enrutamiento WHERE origen_info = %s"
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, (origen_info,))
            connection.commit()
            filas_eliminadas = cursor.rowcount
            cursor.close()
            print(f"✓ {filas_eliminadas} rutas de origen '{origen_info}' eliminadas")
            return filas_eliminadas
        except Exception as e:
            print(f"✗ Error al eliminar rutas: {e}")
            return 0

    def limpiar_tabla(self):
        """
        Elimina todas las rutas de la tabla

        Returns:
            True si la operación fue exitosa
        """
        query = "DELETE FROM tb_Enrutamiento"
        if self.db.execute_query(query):
            print("✓ Tabla de enrutamiento limpiada")
            return True
        return False

    def contar_rutas(self):
        """
        Cuenta el total de rutas

        Returns:
            Número de rutas
        """
        query = "SELECT COUNT(*) FROM tb_Enrutamiento"
        result = self.db.fetch_one(query)
        return result[0] if result else 0

    def existe_destino(self, destino):
        """
        Verifica si ya existe una ruta a un destino

        Args:
            destino: Destino a verificar

        Returns:
            True si existe
        """
        query = "SELECT COUNT(*) FROM tb_Enrutamiento WHERE destino = %s"
        result = self.db.fetch_one(query, (destino,))
        return result[0] > 0 if result else False