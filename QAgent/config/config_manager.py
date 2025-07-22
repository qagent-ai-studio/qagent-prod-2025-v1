"""
Módulo de configuración centralizada siguiendo el patrón Singleton.
Gestiona todas las variables de entorno y configuraciones del proyecto.
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()  # Carga variables de .env si existe

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Singleton para gestionar la configuración de la aplicación.
    Centraliza el acceso a variables de entorno y configuraciones.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa la configuración con valores por defecto y desde variables de entorno"""
        self._config = {}

        
        self._config['PROVEEDOR'] = os.environ.get("PROVEEDOR")
        
        # Configuración de OpenAI
        self._config['OPENAI_API_KEY'] = os.environ.get("OPENAI_API_KEY")
        self._config['OPENAI_ASSISTANT_ID'] = os.environ.get("OPENAI_ASSISTANT_ID")
        
         # Configuración de Azure OpenAI         
        self._config['AZURE_OPENAI_API_KEY'] = os.environ.get("AZURE_OPENAI_API_KEY")
        self._config['AZURE_OPENAI_ASSISTANT_ID'] = os.environ.get("AZURE_OPENAI_ASSISTANT_ID")
        self._config['AZURE_OPENAI_ENDPOINT'] = os.environ.get("AZURE_OPENAI_ENDPOINT")  
        self._config['AZURE_EMBEDDING_DEPLOYMENT'] = os.environ.get("AZURE_EMBEDDING_DEPLOYMENT") 
        self._config['AZURE_OPENAI_API_VERSION'] = os.environ.get("AZURE_OPENAI_API_VERSION")
        
        # Configuración de autenticación de superadmin
        self._config['SUPER_ADMIN_USER'] = os.environ.get("SUPER_ADMIN_USER")
        self._config['SUPER_ADMIN_PASS'] = os.environ.get("SUPER_ADMIN_PASS")
        
        # Configuración de bases de datos MYSQL
        self._config['DB_HOST'] = os.environ.get("DB_HOST", "localhost")
        self._config['DB_USER'] = os.environ.get("DB_USER")
        self._config['DB_PASSWORD'] = os.environ.get("DB_PASSWORD")
        self._config['DB_NAME'] = os.environ.get("DB_NAME")
        
        # Configuración de bases de datos ASQLS
        self._config['DB_ASQLS_SERVER'] = os.environ.get("DB_ASQLS_SERVER")
        self._config['DB_ASQLS_DATABASE'] = os.environ.get("DB_ASQLS_DATABASE")
        self._config['DB_ASQLS_USERNAME'] = os.environ.get("DB_ASQLS_USERNAME")
        self._config['DB_ASQLS_PASSWORD'] = os.environ.get("DB_ASQLS_PASSWORD")
        self._config['DB_ASQLS_DRIVER'] = os.environ.get("DB_ASQLS_DRIVER")        
        
        # Configuración de bases de datos GSQLS
        self._config['DB_GCP_SQLS_SERVER'] = os.environ.get("DB_GCP_SQLS_SERVER")
        self._config['DB_CP_SQLS_DATABASE'] = os.environ.get("DB_CP_SQLS_DATABASE")
        self._config['DB_DB_GCP_SQLS_USERNAME'] = os.environ.get("DB_DB_GCP_SQLS_USERNAME")
        self._config['DB_GCP_SQLS_PASSWORD'] = os.environ.get("DB_GCP_SQLS_PASSWORD")
        self._config['DB_GCP_SQLS_DRIVER'] = os.environ.get("DB_GCP_SQLS_DRIVER")

        # Configuración de Chainlit - PostgreSQL
        self._config['CHAINLIT_DB_URI'] = os.environ.get("CHAINLIT_DB_URI")
        
        # Configuración SQLAlchemy (conexión síncrona)
        self._config['DB_URL'] = os.environ.get("DB_URL")

        # Credenciales API de MAIL JET
        self._config['MAIL_JET_KEY'] = os.environ.get("MAIL_JET_KEY")
        self._config['MAIL_JET_SECRET'] = os.environ.get("MAIL_JET_SECRET")
        
        # clima_tools: Credenciales Api de clima weatherapi.com
        self._config['WHEATHER_API'] = os.environ.get("WHEATHER_API")
        
        # google_analytics_v4: Credenciales Api de Google Analytics 4
        self._config['GA4_KEY'] = os.environ.get("GA4_KEY")
        self._config['GA4_PROPERTY_ID'] = os.environ.get("GA4_PROPERTY_ID")
        
        # Multimedia tools: Configuración de almacenamiento de archivos multimedia
        self._config['MEDIA_VIDEO_PATH'] = os.environ.get("MEDIA_VIDEO_PATH")    
        self._config['MEDIA_PDF_PATH'] = os.environ.get("MEDIA_PDF_PATH")    
        
        # Para descarga de archivos excel
        self._config['URL_ARCHIVO'] = os.environ.get("URL_ARCHIVO")
        
        # BASE DE DATOS VECTORIALES
        self._config['INDEX_FILE'] = os.environ.get("INDEX_FILE")    
        self._config['METADATA_FILE'] = os.environ.get("METADATA_FILE")    
        self._config['URL_BASE'] = os.environ.get("URL_BASE")
        
        # Verificar configuraciones críticas
        self._validate_critical_config()

    def _validate_critical_config(self):
        """Valida que las configuraciones críticas estén presentes"""
        critical_keys = ['OPENAI_API_KEY', 'OPENAI_ASSISTANT_ID']
        
        for key in critical_keys:
            if not self._config.get(key):
                logger.warning(f"Configuración crítica faltante: {key}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración

        Args:
            key: Clave de configuración
            default: Valor por defecto si la clave no existe

        Returns:
            Valor de configuración o default si no existe
        """
        return self._config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """
        Obtiene todas las configuraciones
        
        Returns:
            Diccionario con todas las configuraciones
        """
        return self._config.copy()

    def set(self, key: str, value: Any) -> None:
        """
        Establece un valor de configuración
        
        Args:
            key: Clave de configuración
            value: Valor a establecer
        """
        self._config[key] = value
        
# Para uso directo como import
config = ConfigManager()
