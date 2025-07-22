"""
Módulo de conexión a bases de datos.
Mantiene compatibilidad con el código existente.
"""

import logging
from typing import Dict, Any, Optional, List, Union

from QAgent.repositories.postgres_repository import PostgresRepository

logger = logging.getLogger(__name__)

class DB:
    """
    Clase para acceso a base de datos.
    Mantiene la compatibilidad con el código existente.
    Esta clase actúa como un adaptador al nuevo sistema de repositorios.
    """
    
    @classmethod
    async def execute(cls, query: str, *params):
        """
        Ejecuta consultas que no retornan resultados (INSERT, UPDATE, DELETE)
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
        """
        try:
            repo = PostgresRepository()
            await repo.execute(query, *params)
        except Exception as e:
            logger.error(f"DB.execute error: {e}")
            raise

    @classmethod
    async def fetch(cls, query: str, *params) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT y retorna múltiples filas como lista de diccionarios
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Lista de diccionarios con los resultados
        """
        try:
            repo = PostgresRepository()
            return await repo.fetch(query, *params)
        except Exception as e:
            logger.error(f"DB.fetch error: {e}")
            raise

    @classmethod
    async def fetchrow(cls, query: str, *params) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT y retorna una sola fila como diccionario
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Diccionario con el resultado o None si no hay resultados
        """
        try:
            repo = PostgresRepository()
            return await repo.fetchrow(query, *params)
        except Exception as e:
            logger.error(f"DB.fetchrow error: {e}")
            raise
