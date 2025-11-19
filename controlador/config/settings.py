DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql',
    'database': 'controlador_db',
    'port': 3306
}

# Configuración del controlador
CONTROLADOR_CONFIG = {
    'nombre': 'SDN_Controller',
    'version': '1.0.0',
    'puerto': 6633,
}

# Estados válidos
ESTADOS_ROUTER = ['Activo', 'Inactivo', 'En mantenimiento']
ESTADOS_ENLACE = ['Activo', 'Inactivo']

# Configuración de logging
LOG_CONFIG = {
    'nivel': 'INFO',
    'formato': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'archivo': 'logs/controlador.log'
}