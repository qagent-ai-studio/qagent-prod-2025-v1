"""
Módulo de repositorios.
"""

from QAgent.repositories.db_repository import DBRepository
from QAgent.repositories.mysql_repository import MySQLRepository
from QAgent.repositories.postgres_repository import PostgresRepository

__all__ = ['DBRepository', 'MySQLRepository', 'PostgresRepository']
