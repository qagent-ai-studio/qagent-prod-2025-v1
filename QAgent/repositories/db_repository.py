"""
Módulo base para el acceso a datos siguiendo el patrón Repository.
Define la interfaz abstracta para diferentes implementaciones de acceso a datos.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class DBRepository(ABC):
    """
    Clase base abstracta para repositorios de acceso a datos.
    Define la interfaz común para diferentes implementaciones de bases de datos.
    """
    
    _instance = None
    
    def __new__(cls):
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(DBRepository, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    @abstractmethod
    def _initialize(self) -> None:
        """Inicializa la conexión y configuración del repositorio"""
        pass
    
    @abstractmethod
    async def execute(self, query: str, *params) -> None:
        """
        Ejecuta una consulta SQL sin retornar resultados (INSERT, UPDATE, DELETE)
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
        """
        pass
    
    @abstractmethod
    async def fetch(self, query: str, *params) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL y retorna múltiples filas
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Lista de diccionarios con los resultados
        """
        pass
    
    @abstractmethod
    async def fetchrow(self, query: str, *params) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL y retorna una sola fila
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Diccionario con el resultado o None si no hay resultados
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Cierra las conexiones y recursos del repositorio"""
        pass
