"""
Herramientas utilitarias para el asistente.
"""

import logging
from datetime import datetime
from typing import Dict, Any
import tiktoken

import chainlit as cl

from QAgent.tools.base_tool import BaseTool
from QAgent.config.config_manager import config
from QAgent.utils.logging_utils import notify_error

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool


logger = logging.getLogger(__name__)

# Función para contar tokens
def qtokens(string: str) -> int:
    """
    Retorna el número de tokens en un texto
    
    Args:
        string: Texto a analizar
        
    Returns:
        Número de tokens
    """
    encoding = tiktoken.encoding_for_model("gpt-4o-mini") # <- TODO: DEBE SER COHERENTE CON EL MODELO 
    num_tokens = len(encoding.encode(string))
    return num_tokens


# Función para almacenar interacciones en la base de datos
# ! Deprecated: Favor eliminar 
async def almacenar_interaccion(
    user_input: str,
    assistant_response: str,
    assistant_sql_query: str,
    new_thread_id: str,
    tokens_nuevos: int,
    agente: str
) -> None:
    """
    Almacena las interacciones entre el usuario y el asistente en la base de datos
    
    Args:
        user_input: Mensaje del usuario
        assistant_response: Respuesta del asistente
        assistant_sql_query: Consulta SQL ejecutada por el asistente
        new_thread_id: ID del hilo de conversación
        tokens_nuevos: Número de tokens utilizados
        agente: Tipo de agente utilizado
    """
    try:
        pass
        
        
    except Exception as err:
        logger.error(f"Error en almacenar_interaccion: {err}")


class DateTimeTool(BaseTool):
    """
    Herramienta para obtener la fecha y hora actual.
    """
    
    async def execute(self) -> str:
        """
        Obtiene la fecha y hora actual
        
        Returns:
            Fecha y hora actual en formato legible
        """
        try:
            now = datetime.now() 
            hoy = now.strftime("%d-%m-%Y %H:%M:%S")
            respuesta = f"Esta es la fecha de hoy: {hoy} esta en formato Dia-Mes-Año Hora:Minuto:Segundo"
            return respuesta
        except Exception as err:
            await notify_error(str(err), "utility_tools", "getCurrentDate")
            return f"Error al obtener la fecha: {str(err)}"


class SendMailTool(BaseTool):
    """
    Herramienta para enviar correos electrónicos.
    """
    
    async def execute(self, email: str, nombre: str, texto: str) -> str:
        """
        Envía un correo electrónico
        
        Args:
            email: Dirección de correo del destinatario
            nombre: Nombre del destinatario
            texto: Contenido del correo
            
        Returns:
            Mensaje de confirmación
        """
        try:
            # Importar el módulo de envío de correos
            from QAgent.send_mail.send_mailjet import enviar_mail
            
            # Enviar el correo
            enviar_mail(nombre, email, texto)
            
            logger.info(f"Correo enviado a {email}")
            return f"El mail fue enviado a {nombre} con el siguiente texto: {texto}"
        except Exception as err:
            await notify_error(str(err), "utility_tools", "send_mail")
            logger.error(f"Error al enviar correo: {err}")
            return f"Error al enviar correo: {str(err)}"


# mysql
class GetMysqlSchema(BaseTool):
        
    async def execute(self, table: str) -> Dict:
       
        db_connection = None
        cursor = None
        
        try:
            import mysql.connector
            import json
            
            db_connection = mysql.connector.connect(
                host=config.get("DB_HOST"),
                user=config.get("DB_USER"),
                password=config.get("DB_PASSWORD"),
                database=config.get("DB_NAME"),
            )
            cursor = db_connection.cursor(dictionary=True) 
            logger.info(f"Solicitando esquema de la tabla : {table}")
            
            # Ejecutar la consulta
            consulta = """
            SELECT 
                COLUMN_NAME   AS FIELD,
                COLUMN_COMMENT AS COMMENT
            FROM
                information_schema.COLUMNS
            WHERE
                TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME  = :table
            ORDER BY 
                ORDINAL_POSITION
            """
                
            cursor.execute(consulta, {'nombre_tabla': table})
            resultados = cursor.fetchall()
            
            json_resultados = json.dumps(resultados, default=str)             
            return json_resultados
        
        except Exception as err:
            #await notify_error(str(err), "utility_tools", "send_mail")
            logger.error(f"Error al obtener esquema de la tabla {table}: {err}")
            return f"Error al obtener esquema de la tabla {table} : {str(err)}"

# mysql
class GetMySQLTablesAndColumns(BaseTool):
       
    async def execute(self) -> Dict:
       
        db_connection = None
        cursor = None
        
        try:
            import mysql.connector
            import json
            
            db_connection = mysql.connector.connect(
                host=config.get("DB_HOST"),
                user=config.get("DB_USER"),
                password=config.get("DB_PASSWORD"),
                database=config.get("DB_NAME"),
            )
            cursor = db_connection.cursor(dictionary=True)           
            
            database = config.get("DB_NAME")
            logger.info(f"Solicitando esquema de la base : {database}")
            
            # Ejecutar la consulta
            consulta = """
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                COLUMN_NAME,
                COLUMN_TYPE,
                IS_NULLABLE,
                COLUMN_KEY,
                EXTRA
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME, ORDINAL_POSITION
            """

            cursor.execute(consulta, (database,))
            resultados = cursor.fetchall()
            
            json_resultados = json.dumps(resultados, default=str)             
            return json_resultados
        
        except Exception as err:
            #await notify_error(str(err), "utility_tools", "send_mail")
            logger.error(f"Error al obtener esquema de la tabla {database}: {err}")
            return f"Error al obtener esquema de la tabla {database} : {str(err)}"

# mysql
class GetMySQLRelationships(BaseTool):   
    
    async def execute(self) -> Dict:
       
        db_connection = None
        cursor = None
        
        try:
            import mysql.connector
            import json
            
            db_connection = mysql.connector.connect(
                host=config.get("DB_HOST"),
                user=config.get("DB_USER"),
                password=config.get("DB_PASSWORD"),
                database=config.get("DB_NAME"),
            )
            cursor = db_connection.cursor(dictionary=True) 
            database = config.get("DB_NAME")
            logger.info(f"Solicitando esquema de la base : {database}")
            
            # Ejecutar la consulta
            consulta = """
            SELECT 
                c.TABLE_NAME,
                c.COLUMN_NAME,
                c.COLUMN_TYPE,
                c.COLUMN_KEY,
                k.REFERENCED_TABLE_NAME AS tabla_relacionada,
                k.REFERENCED_COLUMN_NAME AS columna_relacionada
            FROM information_schema.COLUMNS c
            LEFT JOIN information_schema.KEY_COLUMN_USAGE k
                ON c.TABLE_SCHEMA = k.TABLE_SCHEMA
                AND c.TABLE_NAME = k.TABLE_NAME
                AND c.COLUMN_NAME = k.COLUMN_NAME
                AND k.REFERENCED_TABLE_NAME IS NOT NULL
            WHERE c.TABLE_SCHEMA = %s
            ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION
            """
                
            cursor.execute(consulta, (database,))
            resultados = cursor.fetchall()
            
            json_resultados = json.dumps(resultados, default=str)             
            return json_resultados
        
        except Exception as err:
            #await notify_error(str(err), "utility_tools", "send_mail")
            logger.error(f"Error al obtener esquema de la tabla {database}: {err}")
            return f"Error al obtener esquema de la tabla {database} : {str(err)}"
        
# Azure
class GetASQLSTablesAndColumns(BaseTool):
    _engine = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            SERVER   = config.get("DB_ASQLS_SERVER")
            DATABASE = config.get("DB_ASQLS_DATABASE")
            USERNAME = config.get("DB_ASQLS_USERNAME")
            PASSWORD = config.get("DB_ASQLS_PASSWORD")
            DRIVER   = config.get("DB_ASQLS_DRIVER")

            url = (
                f"mssql+pyodbc://{USERNAME}:{PASSWORD}"
                f"@{SERVER}:1433/{DATABASE}"
                f"?driver={DRIVER.replace(' ', '+')}&TrustServerCertificate=yes&encrypt=yes"
            )

            cls._engine = create_engine(
                url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True,
                fast_executemany=True,
                echo=False,
                connect_args={
                    'application_name': 'Qagent_App',
                    'timeout': 30
                }
            )
        return cls._engine

    async def execute(self) -> str:
        try:
            import json
            engine = self.get_engine()
            query = """
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION;
            """

            with engine.connect() as conn:
                result = conn.execute(text(query))
                columns = result.keys()
                rows = result.fetchall()
                data = [dict(zip(columns, row)) for row in rows]

            return json.dumps(data, indent=2, default=str)

        except Exception as err:
            logger.error(f"Error al obtener esquema de la base: {err}")
            return f"❌ Error al obtener esquema de la base: {str(err)}"

# Azure
class GetASQLSRelationships(BaseTool):
    _engine = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            SERVER   = config.get("DB_ASQLS_SERVER")
            DATABASE = config.get("DB_ASQLS_DATABASE")
            USERNAME = config.get("DB_ASQLS_USERNAME")
            PASSWORD = config.get("DB_ASQLS_PASSWORD")
            DRIVER   = config.get("DB_ASQLS_DRIVER")

            url = (
                f"mssql+pyodbc://{USERNAME}:{PASSWORD}"
                f"@{SERVER}:1433/{DATABASE}"
                f"?driver={DRIVER.replace(' ', '+')}&TrustServerCertificate=yes&encrypt=yes"
            )

            cls._engine = create_engine(
                url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True,
                fast_executemany=True,
                echo=False,
                connect_args={
                    'application_name': 'Qagent_App',
                    'timeout': 30
                }
            )
        return cls._engine

    async def execute(self) -> str:
        try:
            import json
            engine = self.get_engine()
            
            query = """
            SELECT 
                fk.name AS foreign_key_name,
                s.name AS parent_schema,
                tp.name AS parent_table,
                cp.name AS parent_column,
                rs.name AS referenced_schema,
                tr.name AS referenced_table,
                cr.name AS referenced_column
            FROM sys.foreign_keys fk
            INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
            INNER JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
            INNER JOIN sys.schemas s ON tp.schema_id = s.schema_id
            INNER JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
            INNER JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
            INNER JOIN sys.schemas rs ON tr.schema_id = rs.schema_id
            INNER JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
            ORDER BY s.name, tp.name, fk.name;
            """

            with engine.connect() as conn:
                result = conn.execute(text(query))
                columns = result.keys()
                rows = result.fetchall()
                data = [dict(zip(columns, row)) for row in rows]

            return json.dumps(data, indent=2, default=str)

        except Exception as err:
            logger.error(f"❌ Error al obtener relaciones de la base: {err}")
            return f"❌ Error al obtener relaciones de la base: {str(err)}"

# GCP 
class GetGCPSQLSTablesAndColumns(BaseTool):
    _engine = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            SERVER   = config.get("DB_GCP_SQLS_SERVER")
            DATABASE = config.get("DB_CP_SQLS_DATABASE")
            USERNAME = config.get("DB_DB_GCP_SQLS_USERNAME")
            PASSWORD = config.get("DB_GCP_SQLS_PASSWORD")
            DRIVER   = config.get("DB_GCP_SQLS_DRIVER") 

            url = (
                f"mssql+pyodbc://{USERNAME}:{PASSWORD}"
                f"@{SERVER}:1433/{DATABASE}"
                f"?driver={DRIVER.replace(' ', '+')}&TrustServerCertificate=yes&encrypt=yes"
            )

            cls._engine = create_engine(
                url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True,
                fast_executemany=True,
                echo=False,
                connect_args={
                    'application_name': 'Qagent_App',
                    'timeout': 30
                }
            )
        return cls._engine

    async def execute(self) -> str:
        try:
            import json
            engine = self.get_engine()
            query = """
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION;
            """

            with engine.connect() as conn:
                result = conn.execute(text(query))
                columns = result.keys()
                rows = result.fetchall()
                data = [dict(zip(columns, row)) for row in rows]

            return json.dumps(data, indent=2, default=str)

        except Exception as err:
            logger.error(f"Error al obtener esquema de la base: {err}")
            return f"❌ Error al obtener esquema de la base: {str(err)}"

# GCP 
class GetGCPSQLSRelationships(BaseTool):
    _engine = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            SERVER   = config.get("DB_GCP_SQLS_SERVER")
            DATABASE = config.get("DB_CP_SQLS_DATABASE")
            USERNAME = config.get("DB_DB_GCP_SQLS_USERNAME")
            PASSWORD = config.get("DB_GCP_SQLS_PASSWORD")
            DRIVER   = config.get("DB_GCP_SQLS_DRIVER") 

            url = (
                f"mssql+pyodbc://{USERNAME}:{PASSWORD}"
                f"@{SERVER}:1433/{DATABASE}"
                f"?driver={DRIVER.replace(' ', '+')}&TrustServerCertificate=yes&encrypt=yes"
            )

            cls._engine = create_engine(
                url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True,
                fast_executemany=True,
                echo=False,
                connect_args={
                    'application_name': 'Qagent_App',
                    'timeout': 30
                }
            )
        return cls._engine

    async def execute(self) -> str:
        try:
            import json
            engine = self.get_engine()
            
            query = """
            SELECT 
                fk.name AS foreign_key_name,
                s.name AS parent_schema,
                tp.name AS parent_table,
                cp.name AS parent_column,
                rs.name AS referenced_schema,
                tr.name AS referenced_table,
                cr.name AS referenced_column
            FROM sys.foreign_keys fk
            INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
            INNER JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
            INNER JOIN sys.schemas s ON tp.schema_id = s.schema_id
            INNER JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
            INNER JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
            INNER JOIN sys.schemas rs ON tr.schema_id = rs.schema_id
            INNER JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
            ORDER BY s.name, tp.name, fk.name;
            """

            with engine.connect() as conn:
                result = conn.execute(text(query))
                columns = result.keys()
                rows = result.fetchall()
                data = [dict(zip(columns, row)) for row in rows]

            return json.dumps(data, indent=2, default=str)

        except Exception as err:
            logger.error(f"❌ Error al obtener relaciones de la base: {err}")
            return f"❌ Error al obtener relaciones de la base: {str(err)}"

        

@cl.step(type="tool")
async def getCurrentDate() -> str:
    """
    Herramienta de Assistant
    Obtiene la fecha actual.

    Returns: 
        Fecha y hora actual en formato legible
    """
    tool = DateTimeTool()
    return await tool.execute()


@cl.step(type="tool")
async def send_mail(email: str, nombre: str, texto: str) -> str:
    """
    Herramienta de Assistant
    Envía un email por medio del asistente.

    Args:
        email: Dirección de correo del destinatario
        nombre: Nombre del destinatario
        texto: Contenido del correo
        
    Returns: 
        Mensaje de confirmación
    """
    tool = SendMailTool()
    return await tool.execute(email=email, nombre=nombre, texto=texto)

async def get_mysql_schema(table: str) -> str:
    """
    Herramienta de Assistant
    Consulta el esquema de la tabla a consultar.

    Args:
        table: Nombre de la tabla a consultar        
        
    Returns: 
        Diccionario nombre_tabla -> Comentario 
    """
    tool = GetMysqlSchema()
    return await tool.execute(table=table)

async def getMySQLTablesAndColumns() -> str:
    """
    Devuelve todas las tablas y sus columnas, junto con su tipo de dato, 
    si permiten nulos, si son claves primarias y otras propiedades.

    Returns: 
        str: Un JSON o texto estructurado que describe todas las tablas y sus columnas 
             (nombre de tabla, nombre de columna, tipo de dato, si es nullable, etc.).
    """
    tool = GetMySQLTablesAndColumns()
    return await tool.execute()

async def getMySQLRelationships() -> str:
    """
    Devuelve todas las relaciones (claves foráneas) entre tablas, 
    incluyendo la columna de origen y la tabla/columna de destino.

    Returns: 
         str: Un JSON o texto estructurado con las relaciones entre tablas, especificando 
             claves foráneas, tablas origen/destino y columnas relacionadas.
    """
    tool = GetMySQLRelationships()
    return await tool.execute()

async def getASQLSTablesAndColumns() -> str:
    """
    Devuelve todas las tablas y sus columnas, junto con su tipo de dato, 
    si permiten nulos, si son claves primarias y otras propiedades.
    Base de datos Azure

    Returns: 
    str: Un JSON o texto estructurado que describe todas las tablas y sus columnas 
        (nombre de tabla, nombre de columna, tipo de dato, si es nullable, etc.).
    """
    tool = GetASQLSTablesAndColumns()
    return await tool.execute()

async def getASQLSRelationships() -> str:
    """
    Devuelve todas las relaciones (claves foráneas) entre tablas, 
    incluyendo la columna de origen y la tabla/columna de destino.
    Base de datos Azure

    Returns: 
    str: Un JSON o texto estructurado con las relaciones entre tablas, especificando 
        claves foráneas, tablas origen/destino y columnas relacionadas.
    """
    tool = GetASQLSRelationships()
    return await tool.execute()

async def getGCPSQLSTablesAndColumns() -> str:
    """
    Devuelve todas las tablas y sus columnas, junto con su tipo de dato, 
    si permiten nulos, si son claves primarias y otras propiedades.
    Base de datos GCP

    Returns: 
    str: Un JSON o texto estructurado que describe todas las tablas y sus columnas 
        (nombre de tabla, nombre de columna, tipo de dato, si es nullable, etc.).
    """
    tool = GetGCPSQLSTablesAndColumns()
    return await tool.execute()

async def getGCPSQLSRelationships() -> str:
    """
    Devuelve todas las relaciones (claves foráneas) entre tablas, 
    incluyendo la columna de origen y la tabla/columna de destino.
    Base de datos GCP

    Returns: 
    str: Un JSON o texto estructurado con las relaciones entre tablas, especificando 
        claves foráneas, tablas origen/destino y columnas relacionadas.
    """
    tool = GetGCPSQLSRelationships()
    return await tool.execute()