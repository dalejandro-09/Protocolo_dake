from controlador.config.database import Database
from controlador.model.router import Router

class RouterDAO:
    def __init__(self):
        self.db = Database()
    def crear(self, router):
        query = """
            INSERT INTO Router (nombre, ip, estado, ultima_actualizacion)
            VALUES (%s, %s, %s, %s)
        """
        params = (router.nombre, router.ip, router.estado, router.ultima_actualizacion)

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            router_id = cursor.lastrowid
            cursor.close()
            print(f"✓ Router '{router.nombre}' creado con ID: {router_id}")
            return router_id
        except Exception as e:
            print(f"✗ Error al crear router: {e}")
            return None

    def obtener_por_id(self, id_router):

        query = "SELECT * FROM Router WHERE id_router = %s"
        result = self.db.fetch_one(query, (id_router,))
        return Router.from_tuple(result)

    def obtener_por_nombre(self, nombre):

        query = "SELECT * FROM Router WHERE nombre = %s"
        result = self.db.fetch_one(query, (nombre,))
        return Router.from_tuple(result)

    def obtener_por_ip(self, ip):
        query = "SELECT * FROM Router WHERE ip = %s"
        result = self.db.fetch_one(query, (ip,))
        return Router.from_tuple(result)

    def obtener_todos(self):

        query = "SELECT * FROM Router ORDER BY id_router"
        results = self.db.fetch_all(query)
        return [Router.from_tuple(row) for row in results]

    def obtener_activos(self):
        """
        Obtiene todos los routers activos

        Returns:
            Lista de objetos Router activos
        """
        query = "SELECT * FROM Router WHERE estado = 'Activo' ORDER BY id_router"
        results = self.db.fetch_all(query)
        return [Router.from_tuple(row) for row in results]

    def actualizar(self, router):
        """
        Actualiza un router existente

        Args:
            router: Objeto Router con datos actualizados

        Returns:
            True si la actualización fue exitosa
        """
        query = """
            UPDATE Router 
            SET nombre = %s, ip = %s, estado = %s, ultima_actualizacion = %s
            WHERE id_router = %s
        """
        params = (router.nombre, router.ip, router.estado,
                  router.ultima_actualizacion, router.id_router)

        if self.db.execute_query(query, params):
            print(f"✓ Router ID {router.id_router} actualizado")
            return True
        return False

    def cambiar_estado(self, id_router, nuevo_estado):
        """
        Cambia el estado de un router

        Args:
            id_router: ID del router
            nuevo_estado: Nuevo estado ('Activo', 'Inactivo', 'En mantenimiento')

        Returns:
            True si el cambio fue exitoso
        """
        query = """
            UPDATE Router 
            SET estado = %s, ultima_actualizacion = NOW()
            WHERE id_router = %s
        """
        if self.db.execute_query(query, (nuevo_estado, id_router)):
            print(f"✓ Estado del router ID {id_router} cambiado a '{nuevo_estado}'")
            return True
        return False

    def eliminar(self, id_router):
        """
        Elimina un router (y sus enlaces por CASCADE)

        Args:
            id_router: ID del router a eliminar

        Returns:
            True si la eliminación fue exitosa
        """
        query = "DELETE FROM Router WHERE id_router = %s"
        if self.db.execute_query(query, (id_router,)):
            print(f"✓ Router ID {id_router} eliminado")
            return True
        return False

    def contar_routers(self):
        """
        Cuenta el total de routers

        Returns:
            Número de routers
        """
        query = "SELECT COUNT(*) FROM Router"
        result = self.db.fetch_one(query)
        return result[0] if result else 0

    def existe_ip(self, ip, excluir_id=None):
        """
        Verifica si una IP ya está en uso

        Args:
            ip: IP a verificar
            excluir_id: ID de router a excluir de la búsqueda (para updates)

        Returns:
            True si la IP existe
        """
        if excluir_id:
            query = "SELECT COUNT(*) FROM Router WHERE ip = %s AND id_router != %s"
            result = self.db.fetch_one(query, (ip, excluir_id))
        else:
            query = "SELECT COUNT(*) FROM Router WHERE ip = %s"
            result = self.db.fetch_one(query, (ip,))

        return result[0] > 0 if result else False