DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql',  # Cambiar por tu contraseña
    'database': 'router_db',
    'port': 3306
}

# Configuración del router
ROUTER_CONFIG = {
    'version': '1.0.0',
    'protocolo': 'OSPF',
    'hello_interval': 10,  # segundos
    'dead_interval': 40,   # segundos
}

# Estados válidos de vecinos
ESTADOS_VECINO = ['Full', '2-Way', 'Down']

# Tipos de mensajes OSPF
TIPOS_MENSAJE = ['START', 'ACK', 'UPDATE', 'FAIL', 'HELLO', 'LSA', 'DBD', 'LSR', 'LSU']

# Origen de información de rutas
ORIGEN_INFO = ['Interna', 'Controlador', 'Externa']

# Configuración de logging
LOG_CONFIG = {
    'nivel': 'INFO',
    'formato': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'archivo': 'logs/router.log'
}