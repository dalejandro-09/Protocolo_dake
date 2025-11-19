from controlador.config.database import Database
from controlador.model.enlace import Enlace

class EnlaceDAO:
    def __init__(self):
        self.db = Database()

    def crear(self, enlace):
        query = """
            INSERT INTO Enlace (router_origen, router_destino, costo, 
                               ancho_banda, estado, retardo_ms)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (enlace.router_origen, enlace.router_destino, enlace.costo,
                  enlace.ancho_banda, enlace.estado, enlace.retardo_ms)

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            enlace_id = cursor.lastrowid
            cursor.close()
            print(f"✓ Enlace creado: R{enlace.router_origen} -> R{enlace.router_destino} (ID: {enlace_id})")
            return enlace_id
        except Exception as e:
            print(f"✗ Error al crear enlace: {e}")
            return None

    def obtener_por_id(self, id_enlace):

        query = "SELECT * FROM Enlace WHERE id_enlace = %s"
        result = self.db.fetch_one(query, (id_enlace,))
        return Enlace.from_tuple(result)

    def obtener_todos(self):

        query = "SELECT * FROM Enlace ORDER BY id_enlace"
        results = self.db.fetch_all(query)
        return [Enlace.from_tuple(row) for row in results]

    def obtener_activos(self):

        query = "SELECT * FROM Enlace WHERE estado = 'Activo' ORDER BY id_enlace"
        results = self.db.fetch_all(query)
        return [Enlace.from_tuple(row) for row in results]

    def obtener_por_router(self, id_router):

        query = """
            SELECT * FROM Enlace 
            WHERE router_origen = %s OR router_destino = %s
            ORDER BY id_enlace
        """
        results = self.db.fetch_all(query, (id_router, id_router))
        return [Enlace.from_tuple(row) for row in results]

    def obtener_vecinos(self, id_router):
        query = """
            SELECT 
                CASE 
                    WHEN router_origen = %s THEN router_destino
                    ELSE router_origen
                END as vecino,
                costo,
                id_enlace
            FROM Enlace
            WHERE (router_origen = %s OR router_destino = %s)
            AND estado = 'Activo'
        """
        results = self.db.fetch_all(query, (id_router, id_router, id_router))
        return results

    def obtener_enlace_entre(self, router_origen, router_destino):
        query = """
            SELECT * FROM Enlace 
            WHERE (router_origen = %s AND router_destino = %s)
               OR (router_origen = %s AND router_destino = %s)
            LIMIT 1
        """
        result = self.db.fetch_one(query, (router_origen, router_destino,
                                           router_destino, router_origen))
        return Enlace.from_tuple(result)

    def actualizar(self, enlace):

        query = """
            UPDATE Enlace 
            SET router_origen = %s, router_destino = %s, costo = %s,
                ancho_banda = %s, estado = %s, retardo_ms = %s
            WHERE id_enlace = %s
        """
        params = (enlace.router_origen, enlace.router_destino, enlace.costo,
                  enlace.ancho_banda, enlace.estado, enlace.retardo_ms,
                  enlace.id_enlace)

        if self.db.execute_query(query, params):
            print(f"✓ Enlace ID {enlace.id_enlace} actualizado")
            return True
        return False

    def cambiar_estado(self, id_enlace, nuevo_estado):

        query = "UPDATE Enlace SET estado = %s WHERE id_enlace = %s"
        if self.db.execute_query(query, (nuevo_estado, id_enlace)):
            print(f"✓ Estado del enlace ID {id_enlace} cambiado a '{nuevo_estado}'")
            return True
        return False

    def eliminar(self, id_enlace):

        query = "DELETE FROM Enlace WHERE id_enlace = %s"
        if self.db.execute_query(query, (id_enlace,)):
            print(f"✓ Enlace ID {id_enlace} eliminado")
            return True
        return False

    def contar_enlaces(self):

        query = "SELECT COUNT(*) FROM Enlace"
        result = self.db.fetch_one(query)
        return result[0] if result else 0

    def existe_enlace(self, router_origen, router_destino, excluir_id=None):

        if excluir_id:
            query = """
                SELECT COUNT(*) FROM Enlace 
                WHERE ((router_origen = %s AND router_destino = %s)
                   OR (router_origen = %s AND router_destino = %s))
                AND id_enlace != %s
            """
            result = self.db.fetch_one(query, (router_origen, router_destino,
                                               router_destino, router_origen,
                                               excluir_id))
        else:
            query = """
                SELECT COUNT(*) FROM Enlace 
                WHERE (router_origen = %s AND router_destino = %s)
                   OR (router_origen = %s AND router_destino = %s)
            """
            result = self.db.fetch_one(query, (router_origen, router_destino,
                                               router_destino, router_origen))

        return result[0] > 0 if result else False