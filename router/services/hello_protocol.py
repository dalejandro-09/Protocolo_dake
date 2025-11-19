import time
import threading
from datetime import datetime
from router.dao.vecino_dao import VecinoDAO
from router.dao.mensaje_dao import MensajeDAO
from router.dao.log_router_dao import LogRouterDAO
from router.config.settings import ROUTER_CONFIG

class HelloProtocol:
    def __init__(self, router_nombre, router_ip=None):
        """
        Inicializa el protocolo HELLO

        Args:
            router_nombre: Nombre del router
            router_ip: IP del router (opcional)
        """
        self.router_nombre = router_nombre
        self.router_ip = router_ip  # ← GUARDAR router_ip
        self.vecino_dao = VecinoDAO()
        self.mensaje_dao = MensajeDAO()
        self.log_dao = LogRouterDAO()

        self.hello_interval = ROUTER_CONFIG['hello_interval']
        self.activo = False
        self.hilo_hello = None

    def enviar_hello_periodico(self):
        """Envía mensajes HELLO periódicamente a todos los vecinos"""
        while self.activo:
            vecinos = self.vecino_dao.obtener_activos()

            for vecino in vecinos:
                contenido = f"HELLO from {self.router_nombre}"
                if self.router_ip:  # ← INCLUIR IP si está disponible
                    contenido += f" ({self.router_ip})"
                contenido += f" at {datetime.now()}"

                self.mensaje_dao.registrar_mensaje(
                    tipo='HELLO',
                    emisor=self.router_nombre,
                    receptor=vecino.router_vecino,
                    contenido=contenido
                )

            if vecinos:
                print(f"📡 HELLO enviado a {len(vecinos)} vecinos")

            time.sleep(self.hello_interval)

    def iniciar(self):
        """Inicia el envío periódico de HELLOs"""
        if not self.activo:
            self.activo = True
            self.hilo_hello = threading.Thread(target=self.enviar_hello_periodico, daemon=True)
            self.hilo_hello.start()

            self.log_dao.registrar_evento(
                "Protocolo HELLO iniciado",
                f"Intervalo: {self.hello_interval} segundos"
            )
            print(f"✓ Protocolo HELLO iniciado (intervalo: {self.hello_interval}s)")

    def detener(self):
        """Detiene el envío periódico de HELLOs"""
        if self.activo:
            self.activo = False
            if self.hilo_hello:
                self.hilo_hello.join(timeout=2)

            self.log_dao.registrar_evento(
                "Protocolo HELLO detenido",
                "Servicio de HELLOs desactivado"
            )
            print("✓ Protocolo HELLO detenido")

    def esta_activo(self):
        """Verifica si el protocolo está activo"""
        return self.activo