"""
Implementación del repositorio para PostgreSQL.
Utiliza SQLAlchemy para las operaciones de base de datos.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker

from QAgent.config.config_manager import config
from QAgent.repositories.db_repository import DBRepository

logger = logging.getLogger(__name__)

class PostgresRepository(DBRepository):
    """
    Implementación del repositorio para PostgreSQL usando SQLAlchemy.
    Implementa el patrón Singleton y Repository.
    """
    
    def _initialize(self) -> None:
        """Inicializa la conexión a PostgreSQL"""
        self._engine = None
        self._session_maker = None
        self._connection_string = config.get('CHAINLIT_DB_URI')
        
        try:
            self._engine = create_async_engine(self._connection_string)
            self._session_maker = sessionmaker(
                self._engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            logger.info("Repositorio PostgreSQL inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar el repositorio PostgreSQL: {e}")
            raise
    
    async def execute(self, query: str, *params) -> None:
        """
        Ejecuta una consulta SQL sin retornar resultados (INSERT, UPDATE, DELETE)
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
        """
        if not self._session_maker:
            raise RuntimeError("Repositorio PostgreSQL no inicializado")
            
        async with self._session_maker() as session:
            try:
                # Si params[0] es un diccionario, lo usamos directamente
                params_dict = params[0] if params and isinstance(params[0], dict) else {}
                await session.execute(text(query), params_dict)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Error en PostgresRepository.execute: {e}")
                raise
    
    async def fetch(self, query: str, *params) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL y retorna múltiples filas
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Lista de diccionarios con los resultados
        """
        if not self._session_maker:
            raise RuntimeError("Repositorio PostgreSQL no inicializado")
            
        async with self._session_maker() as session:
            try:
                # Si params[0] es un diccionario, lo usamos directamente
                params_dict = params[0] if params and isinstance(params[0], dict) else {}
                result = await session.execute(text(query), params_dict)
                return [dict(row._mapping) for row in result.fetchall()]
            except Exception as e:
                logger.error(f"Error en PostgresRepository.fetch: {e}")
                raise
    
    async def fetchrow(self, query: str, *params) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL y retorna una sola fila
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Diccionario con el resultado o None si no hay resultados
        """
        if not self._session_maker:
            raise RuntimeError("Repositorio PostgreSQL no inicializado")
            
        async with self._session_maker() as session:
            try:
                # Si params[0] es un diccionario, lo usamos directamente
                params_dict = params[0] if params and isinstance(params[0], dict) else {}
                result = await session.execute(text(query), params_dict)
                row = result.fetchone()
                return dict(row._mapping) if row else None
            except Exception as e:
                logger.error(f"Error en PostgresRepository.fetchrow: {e}")
                raise
    
    async def close(self) -> None:
        """Cierra la conexión a PostgreSQL"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Conexión a PostgreSQL cerrada correctamente")
