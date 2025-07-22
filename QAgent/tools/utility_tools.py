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



class GetMysqlSchema(BaseTool):
    """
    Herramienta para enviar correos electrónicos.
    """
    
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
                AND TABLE_NAME  = :tabla
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


# Funciones compatibles con la implementación original para mantener CUSTOM_TOOLS

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



@cl.step(type="tool")
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