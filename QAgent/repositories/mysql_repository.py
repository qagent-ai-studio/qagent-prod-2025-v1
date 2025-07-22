"""
Implementación del repositorio para MySQL.
Utiliza mysql-connector-python para las operaciones síncronas
y aiomysql para las operaciones asíncronas.
"""

import logging
import json
import mysql.connector
import aiomysql
from typing import List, Dict, Any, Optional, Union

from QAgent.config.config_manager import config
from QAgent.repositories.db_repository import DBRepository

logger = logging.getLogger(__name__)

class MySQLRepository(DBRepository):
    """
    Implementación del repositorio para MySQL.
    Implementa el patrón Singleton y Repository.
    """
    
    def _initialize(self) -> None:
        """Inicializa la configuración para conexiones MySQL"""
        self._db_config = {
            'host': config.get('DB_HOST', 'localhost'),
            'user': config.get('DB_USER'),
            'password': config.get('DB_PASSWORD'),
            'database': config.get('DB_NAME'),
            'charset': 'utf8',
            'use_unicode': True
        }
        
        self._pool = None
        self._async_pool = None
        
        # Configurar connection pool para operaciones síncronas
        try:
            pool_name = "ai_pool_or"
            pool_size = 4
            self._pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                **self._db_config
            )
            logger.info("Pool de conexiones MySQL inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar el pool de conexiones MySQL: {e}")
            raise
    
    async def _get_async_pool(self):
        """Obtiene o crea el pool asíncrono de conexiones"""
        if self._async_pool is None:
            try:
                self._async_pool = await aiomysql.create_pool(
                    host=self._db_config['host'],
                    user=self._db_config['user'],
                    password=self._db_config['password'],
                    db=self._db_config['database'],
                    charset=self._db_config['charset'],
                    minsize=1,
                    maxsize=10,
                    autocommit=True
                )
                logger.info("Pool de conexiones asíncronas MySQL inicializado correctamente")
            except Exception as e:
                logger.error(f"Error al inicializar el pool de conexiones asíncronas MySQL: {e}")
                raise
        return self._async_pool
    
    def get_sync_connection(self):
        """Obtiene una conexión síncrona del pool"""
        if not self._pool:
            raise RuntimeError("Pool de conexiones MySQL no inicializado")
        return self._pool.get_connection()
    
    async def execute(self, query: str, *params) -> None:
        """
        Ejecuta una consulta SQL sin retornar resultados (INSERT, UPDATE, DELETE)
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
        """
        pool = await self._get_async_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    # Si params[0] es un diccionario, convertimos a tupla de valores
                    if params and isinstance(params[0], dict):
                        # Extraer los valores del diccionario según la consulta
                        # Este es un enfoque simplificado, en una implementación real
                        # se debería analizar la consulta y extraer los parámetros correctamente
                        param_values = tuple(params[0].values())
                        await cursor.execute(query, param_values)
                    else:
                        await cursor.execute(query, params)
                    await conn.commit()
                except Exception as e:
                    await conn.rollback()
                    logger.error(f"Error en MySQLRepository.execute: {e}")
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
        pool = await self._get_async_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    # Si params[0] es un diccionario, convertimos a tupla de valores
                    if params and isinstance(params[0], dict):
                        param_values = tuple(params[0].values())
                        await cursor.execute(query, param_values)
                    else:
                        await cursor.execute(query, params)
                    
                    result = await cursor.fetchall()
                    return [dict(row) for row in result]
                except Exception as e:
                    logger.error(f"Error en MySQLRepository.fetch: {e}")
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
        pool = await self._get_async_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    # Si params[0] es un diccionario, convertimos a tupla de valores
                    if params and isinstance(params[0], dict):
                        param_values = tuple(params[0].values())
                        await cursor.execute(query, param_values)
                    else:
                        await cursor.execute(query, params)
                    
                    row = await cursor.fetchone()
                    return dict(row) if row else None
                except Exception as e:
                    logger.error(f"Error en MySQLRepository.fetchrow: {e}")
                    raise
    
    async def close(self) -> None:
        """Cierra las conexiones a MySQL"""
        if self._async_pool:
            self._async_pool.close()
            await self._async_pool.wait_closed()
            logger.info("Conexiones asíncronas a MySQL cerradas correctamente")
