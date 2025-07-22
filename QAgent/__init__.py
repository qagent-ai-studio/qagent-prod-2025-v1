"""
Paquete principal QAgent.
Mantiene compatibilidad con las importaciones existentes.
"""

# Importamos las entidades principales para mantener compatibilidad
from QAgent.conexion import DB
from QAgent.prompt import instrucciones

# Para mantener compatibilidad completa, importamos tanto desde los nuevos módulos
# como desde el módulo de compatibilidad Qtools
from QAgent.Qtools import CUSTOM_TOOLS
from QAgent.Qtools import almacenar_interaccion, qtokens

# También exponemos las nuevas importaciones para código futuro
from QAgent.tools import ToolFactory
from QAgent.repositories import PostgresRepository, MySQLRepository
from QAgent.services import OpenAIService
from QAgent.config.config_manager import config as app_config
