import os
from router.config.settings import TIPOS_MENSAJE

class MenuMensajes:
    def __init__(self, router_controller):
        self.router_controller = router_controller

    def limpiar_pantalla(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def mostrar_menu(self):
        """Muestra el menú de mensajes"""
        print("\n GESTIÓN DE MENSAJES")
        print("─" * 60)
        print("  1. Enviar mensaje")
        print("  2. Ver mensajes recibidos")
        print("  3. Ver mensajes enviados")
        print("  4. Ver conversación con un router")
        print("  5. Ver estadísticas de mensajes")
        print("  0. Volver al menú principal")
        print("─" * 60)

    def enviar_mensaje(self):
        """Envía un mensaje a otro router"""
        print("\n" + "=" * 60)
        print("ENVIAR MENSAJE")
        print("=" * 60)

        print(f"\nTipos de mensaje disponibles: {', '.join(TIPOS_MENSAJE)}")
        tipo = input("Tipo de mensaje: ").strip()

        if tipo not in TIPOS_MENSAJE:
            print(f" Tipo inválido. Debe ser uno de: {TIPOS_MENSAJE}")
            return

        receptor = input("Router receptor: ").strip()
        if not receptor:
            print("El receptor no puede estar vacío")
            return

        contenido = input("Contenido del mensaje: ").strip()
        if not contenido:
            print(" El contenido no puede estar vacío")
            return

        mensaje_id = self.router_controller.enviar_mensaje(tipo, receptor, contenido)

        if mensaje_id:
            print(f"\n Mensaje enviado exitosamente con ID: {mensaje_id}")
        else:
            print("\n No se pudo enviar el mensaje")

    def ver_mensajes_recibidos(self):
        """Muestra los mensajes recibidos"""
        print("\n" + "=" * 60)
        print("MENSAJES RECIBIDOS")
        print("=" * 60)

        try:
            limite = int(input("Número de mensajes a mostrar (presione Enter para 20): ").strip() or "20")
        except ValueError:
            limite = 20

        mensajes = self.router_controller.obtener_mensajes_recibidos(limite)

        if not mensajes:
            print("\nNo hay mensajes recibidos")
            return

        print(f"\n{'ID':<6} {'Tipo':<10} {'Emisor':<15} {'Fecha/Hora':<20}")
        print("─" * 80)

        for mensaje in mensajes:
            print(f"{mensaje.id_mensaje:<6} {mensaje.tipo:<10} {mensaje.emisor:<15} "
                  f"{str(mensaje.fecha_hora):<20}")

        # Mostrar detalles de un mensaje
        ver_detalle = input("\n¿Ver detalles de un mensaje? (ID o Enter para omitir): ").strip()
        if ver_detalle:
            try:
                id_msg = int(ver_detalle)
                mensaje = next((m for m in mensajes if m.id_mensaje == id_msg), None)
                if mensaje:
                    print("\n" + "=" * 60)
                    print(f"Tipo:      {mensaje.tipo}")
                    print(f"Emisor:    {mensaje.emisor}")
                    print(f"Receptor:  {mensaje.receptor}")
                    print(f"Fecha:     {mensaje.fecha_hora}")
                    print(f"Contenido: {mensaje.contenido}")
                else:
                    print(" Mensaje no encontrado")
            except ValueError:
                print(" ID inválido")

    def ver_mensajes_enviados(self):
        """Muestra los mensajes enviados"""
        print("\n" + "=" * 60)
        print("MENSAJES ENVIADOS")
        print("=" * 60)

        try:
            limite = int(input("Número de mensajes a mostrar (presione Enter para 20): ").strip() or "20")
        except ValueError:
            limite = 20

        mensajes = self.router_controller.obtener_mensajes_enviados(limite)

        if not mensajes:
            print("\nNo hay mensajes enviados")
            return

        print(f"\n{'ID':<6} {'Tipo':<10} {'Receptor':<15} {'Fecha/Hora':<20}")
        print("─" * 80)

        for mensaje in mensajes:
            print(f"{mensaje.id_mensaje:<6} {mensaje.tipo:<10} {mensaje.receptor:<15} "
                  f"{str(mensaje.fecha_hora):<20}")

        # Mostrar detalles de un mensaje
        ver_detalle = input("\n¿Ver detalles de un mensaje? (ID o Enter para omitir): ").strip()
        if ver_detalle:
            try:
                id_msg = int(ver_detalle)
                mensaje = next((m for m in mensajes if m.id_mensaje == id_msg), None)
                if mensaje:
                    print("\n" + "=" * 60)
                    print(f"Tipo:      {mensaje.tipo}")
                    print(f"Emisor:    {mensaje.emisor}")
                    print(f"Receptor:  {mensaje.receptor}")
                    print(f"Fecha:     {mensaje.fecha_hora}")
                    print(f"Contenido: {mensaje.contenido}")
                else:
                    print(" Mensaje no encontrado")
            except ValueError:
                print(" ID inválido")

    def ver_conversacion(self):
        """Muestra la conversación con otro router"""
        print("\n" + "=" * 60)
        print("VER CONVERSACIÓN")
        print("=" * 60)

        otro_router = input("Nombre del otro router: ").strip()
        if not otro_router:
            print(" El nombre del router no puede estar vacío")
            return

        try:
            limite = int(input("Número de mensajes a mostrar (presione Enter para 30): ").strip() or "30")
        except ValueError:
            limite = 30

        mensajes = self.router_controller.obtener_conversacion(otro_router, limite)

        if not mensajes:
            print(f"\nNo hay conversación con {otro_router}")
            return

        print(f"\nConversación con {otro_router}:")
        print("=" * 80)

        for mensaje in reversed(mensajes):  # Mostrar del más antiguo al más reciente
            direccion = "→" if mensaje.emisor == self.router_controller.router_nombre else "←"
            print(f"\n[{mensaje.fecha_hora}] {direccion} {mensaje.tipo}")
            print(f"  {mensaje.contenido[:100]}{'...' if len(mensaje.contenido) > 100 else ''}")

    def ver_estadisticas_mensajes(self):
        """Muestra estadísticas de mensajes"""
        print("\n" + "=" * 60)
        print("ESTADÍSTICAS DE MENSAJES")
        print("=" * 60)

        from router.dao.mensaje_dao import MensajeDAO
        mensaje_dao = MensajeDAO()

        total = mensaje_dao.contar_mensajes()
        stats = mensaje_dao.obtener_estadisticas()

        print(f"\nTotal de mensajes: {total}")

        if stats:
            print("\nPor tipo de mensaje:")
            print("─" * 60)
            for tipo, info in stats.items():
                print(f"  • {tipo:<10} {info['cantidad']:<6} mensajes  (Último: {info['ultimo_mensaje']})")
        else:
            print("\nNo hay estadísticas disponibles")

    def ejecutar(self):
        """Ejecuta el menú de mensajes"""
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(" " * 25 + "ROUTER")
            print("=" * 60)
            self.mostrar_menu()

            opcion = input("\n➤ Seleccione una opción: ").strip()

            if opcion == '1':
                self.enviar_mensaje()
                input("\nPresione Enter para continuar...")

            elif opcion == '2':
                self.ver_mensajes_recibidos()
                input("\nPresione Enter para continuar...")

            elif opcion == '3':
                self.ver_mensajes_enviados()
                input("\nPresione Enter para continuar...")

            elif opcion == '4':
                self.ver_conversacion()
                input("\nPresione Enter para continuar...")

            elif opcion == '5':
                self.ver_estadisticas_mensajes()
                input("\nPresione Enter para continuar...")

            elif opcion == '0':
                break

            else:
                input("\n Opción inválida. Presione Enter para continuar...")