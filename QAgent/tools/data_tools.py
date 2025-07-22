"""
Herramientas para acceso a datos.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any
import pyodbc
import mysql.connector
import chainlit as cl

from QAgent.tools.base_tool import BaseTool
from QAgent.config.config_manager import config
from QAgent.utils.logging_utils import notify_error, get_random_response

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool
import pandas as pd
import json

logger = logging.getLogger(__name__)


async def generar_excel_desde_mysql(resultados):
    
    import openpyxl
    from openpyxl.utils import get_column_letter
    import os
    from datetime import datetime

    try:
        # Crear libro de Excel
        libro = openpyxl.Workbook()
        hoja = libro.active
        
        logger.info(f"Generar_excel_desde_mysql:   {resultados}")

        # Obtener nombres de columnas (claves del primer diccionario)
        columnas = list(resultados[0].keys())
        # Escribir encabezados
        for col_num, columna in enumerate(columnas, 1):
            hoja.cell(row=1, column=col_num, value=columna)
        
        # Escribir datos
        for row_num, fila in enumerate(resultados, 2):
            for col_num, columna in enumerate(columnas, 1):
                valor = fila[columna]
                
                # Manejar tipos de datos especiales (como datetime)
                if hasattr(valor, 'isoformat'):
                    valor = valor.isoformat()
                
                hoja.cell(row=row_num, column=col_num, value=valor)
        
        # Ajustar ancho de columnas automáticamente
        for col_num, columna in enumerate(columnas, 1):
            # Longitud del encabezado
            longitudes = [len(str(columna))]

            # Longitud de los valores no nulos
            for fila in resultados:
                valor = fila.get(columna)
                if valor is not None:
                    longitudes.append(len(str(valor)))

            hoja.column_dimensions[get_column_letter(col_num)].width = min(max(longitudes) + 2, 50)
        
        # Generar nombre de archivo si no se proporcionó
       
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"public/storage/excel/reporte_{fecha_actual}.xlsx"
        libro.save(nombre_archivo)
        URL_ARCHIVO = config.get("URL_ARCHIVO")
        url_archivo = f"{URL_ARCHIVO}{nombre_archivo}"
        logger.info(f"url_archivo:   {url_archivo}")
        
        
        return url_archivo
    except Exception as err:
         logger.error(f"Error al crear un excel: {err}")

class GetDataLocalMySQLTool(BaseTool):
    """
    Herramienta para ejecutar consultas SQL y obtener datos.
    """
    
    async def execute(self, consulta: str) -> str:
        """
        Ejecuta una consulta SQL y devuelve los resultados como JSON
        
        Args:
            consulta: Consulta SQL a ejecutar
            
        Returns:
            Resultados de la consulta en formato JSON
        """
        db_connection = None
        cursor = None
        
        try:
            db_connection = mysql.connector.connect(
                host=config.get("DB_HOST"),
                user=config.get("DB_USER"),
                password=config.get("DB_PASSWORD"),
                database=config.get("DB_NAME"),
            )
            cursor = db_connection.cursor(dictionary=True) 
            logger.info(f"Ejecutando consulta: {consulta}")
            
            # Ejecutar la consulta
            cursor.execute(consulta)
            resultados = cursor.fetchall()            
            filas = len(resultados)
            
            if filas > 100:                
                url_archo_excel = await generar_excel_desde_mysql(resultados)    
                resultados.insert(0, {"Instrucción adicional": f" # Atención, esto es muy importante para el usuario: - El resultado tiene {filas} filas. **Despliega solo las primeras 15 filas e informa al usuario que puede descargar el archivo excel con todos los datos en el siguiente link [Descargar Excel]({url_archo_excel}) renderiza el link en formato md.**"})        
            elif filas > 50:
                url_archo_excel = await generar_excel_desde_mysql(resultados)    
                resultados.insert(0, {"Instrucción adicional": f" # Atención, esto es muy importante para el usuario: - El resultado tiene {filas} filas. **Despliega solo las primeras 15 filas e informa al usuario que puede descargar el archivo excel con todos los datos en el siguiente link [Descargar Excel]({url_archo_excel}) renderiza el link en formato md.**"})        
            elif filas > 20:
                resultados.insert(0, {"Instrucción adicional": f"El resultado tiene {filas} filas. Debes utilizar la herramienta createDataFrame() para paginar los resultados, no formato markdown. **debe estar en formato dict serializado en JSON. Nunca lo envíes como un string anidado ni como tabla Markdown y limpia los campos null.** "})
            else:
                resultados.insert(0, {"Instrucción adicional": f"El resultado tiene {filas} filas. Recuerda que para entregar listas de menos de 20 registros debes utilizar formato markdown"})
            
            
            json_resultados = json.dumps(resultados, default=str)
            
            logger.info(f"Q caracteres respuesta: {len(json_resultados)}")
            return json_resultados
            
        except mysql.connector.Error as err:
            error_message = str(err)
            
            # Gestión de errores
            modulo = "data_tools"
            funcion = "getdata"
            #await notify_error(error_message, modulo, funcion)
            
            response = get_random_response("error")
            await cl.Message(response).send()
            
            if "Unknown column" in error_message:
                return f"Cometiste el siguiente error en tu consulta:{err}. Por favor revisa el nombre de las columnas en tu base de conocimiento y otorga la respuesta correcta"
            else:
                return f"Cometiste el siguiente error en tu consulta:{err}. Por favor replantea la consulta y otorga la respuesta correcta"
        
        finally:
            # Asegura que el cursor y la conexión se cierran
            if cursor:
                cursor.close()
            if db_connection and db_connection.is_connected():
                db_connection.close()

class GetDataAzureSQLServer_deprecador(BaseTool):
    """
    Herramienta para ejecutar consultas SQL SERVER y obtener datos.
    """
    
    async def execute(self, consulta: str) -> str:
        """
        Ejecuta una consulta SQL Server y devuelve los resultados como JSON

        Args:
            consulta: Consulta SQL a ejecutar

        Returns:
            Resultados de la consulta en formato JSON
        """
       
        import pandas as pd
        from sqlalchemy import create_engine
        from sqlalchemy.exc import SQLAlchemyError
        from sqlalchemy.pool import QueuePool

        try:
            
            SERVER   = config.get("DB_ASQLS_SERVER")
            DATABASE = config.get("DB_ASQLS_DATABASE")
            USERNAME = config.get("DB_ASQLS_USERNAME")
            PASSWORD = config.get("DB_ASQLS_PASSWORD")
            DRIVER   = config.get("DB_ASQLS_DRIVER")

            def crear_engine():
                url = (
                    f"mssql+pyodbc://{USERNAME}:{PASSWORD}"
                    f"@{SERVER}:1433/{DATABASE}"
                    f"?driver={DRIVER.replace(' ', '+')}"
                    "&encrypt=yes&trustServerCertificate=no"
                )
               
                return create_engine(
                    url,
                    poolclass=QueuePool,
                    pool_size=10,           # Conexiones mantenidas abiertas
                    max_overflow=20,        # Conexiones adicionales bajo demanda
                    pool_timeout=30,        # Segundos para obtener conexión del pool
                    pool_recycle=3600,      # Reciclar conexiones cada 1 hora
                    pool_pre_ping=True,     # Verificar conexión antes de usarla
                    fast_executemany=True,  # Optimización para inserts masivos
                    echo=False,             # Cambiar a True para debug
                    connect_args={
                        'application_name': 'Chainlit_App',  # Identificador en SQL Server
                        'timeout': 30       # Timeout de conexión inicial
                    }
                )
            
            engine = crear_engine()

            # Ejecutar consulta
            logger.info(f"Ejecutando consulta: {consulta}")
            
            with engine.connect() as conn:
                df_resultado = pd.read_sql(consulta, conn)

            # Convertir a JSON y medir tamaño
            resultados = df_resultado.to_dict(orient="records")
            filas = len(resultados)

            if filas > 100:                
                url_archo_excel = await generar_excel_desde_mysql(resultados)    
                resultados.insert(0, {"Instrucción adicional": f" # Atención, esto es muy importante para el usuario: - El resultado tiene {filas} filas. **Despliega solo las primeras 15 filas e informa al usuario que puede descargar el archivo excel con todos los datos en el siguiente link [Descargar Excel]({url_archo_excel}) renderiza el link en formato md.**"})        
            elif filas > 50:
                url_archo_excel = await generar_excel_desde_mysql(resultados)    
                resultados.insert(0, {"Instrucción adicional": f" # Atención, esto es muy importante para el usuario: - El resultado tiene {filas} filas. **Despliega solo las primeras 15 filas e informa al usuario que puede descargar el archivo excel con todos los datos en el siguiente link [Descargar Excel]({url_archo_excel}) renderiza el link en formato md.**"})        
            elif filas > 20:
                resultados.insert(0, {"Instrucción adicional": f"El resultado tiene {filas} filas. Recuerda que para entregar listas de más de 20 registros debes utilizar la herramienta createDataFrame() para paginar los resultados, no formato markdown"})
            else:
                resultados.insert(0, {"Instrucción adicional": f"El resultado tiene {filas} filas. Recuerda que para entregar listas de menos de 20 registros debes utilizar formato markdown"})
                        
            
            json_resultado = json.dumps(resultados, default=str)
            tamano_bytes = len(json_resultado.encode("utf-8"))
            logger.info(f"Q Tamaño de respuesta: {tamano_bytes}")

            if tamano_bytes > 500000:
                logger.warning("Respuesta supera los 500KB")
                return "Respuesta demasiado grande. Debes paginar, resumir o limitar con LIMIT. Por favor intenta nuevamente"
            else:
                return json_resultado

        except SQLAlchemyError as err:
            error_message = str(err)

            # Gestión de errores
            response = get_random_response("error")
            await cl.Message(response).send()

            if "Invalid column name" in error_message:
                return f"Cometiste el siguiente error en tu consulta: {err}. Por favor revisa el nombre de las columnas en tu base de conocimiento y otorga la respuesta correcta"
            else:
                return f"Cometiste el siguiente error en tu consulta: {err}. Por favor replantea la consulta y otorga la respuesta correcta"

class GetDataAzureSQLServer(BaseTool):
    """
    Herramienta para ejecutar consultas SQL SERVER y obtener datos.
    Usa un engine global para aprovechar el pool de conexiones.
    """
    # --- Engine global para la clase ---
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

    async def execute(self, consulta: str) -> str:
        try:
            engine = self.get_engine()   # Reusa el mismo engine/pool
            logger.info(f"Ejecutando consulta: {consulta}")

            with engine.connect() as conn:
                df_resultado = pd.read_sql(consulta, conn)
            resultados = df_resultado.to_dict(orient="records")
            filas = len(resultados)

            # El resto de tu lógica...
            # ...
            json_resultado = json.dumps(resultados, default=str)
            tamano_bytes = len(json_resultado.encode("utf-8"))
            logger.info(f"Q Tamaño de respuesta: {tamano_bytes}")

            if tamano_bytes > 500000:
                logger.warning("Respuesta supera los 500KB")
                return "Respuesta demasiado grande. Debes paginar, resumir o limitar con LIMIT. Por favor intenta nuevamente"
            else:
                return json_resultado

        except SQLAlchemyError as err:
            error_message = str(err)
            response = get_random_response("error")
            await cl.Message(response).send()

            if "Invalid column name" in error_message:
                return f"Cometiste el siguiente error en tu consulta: {err}. Por favor revisa el nombre de las columnas en tu base de conocimiento y otorga la respuesta correcta"
            else:
                return f"Cometiste el siguiente error en tu consulta: {err}. Por favor replantea la consulta y otorga la respuesta correcta"

class GetDataGCPSQLServer(BaseTool):
    """
    Herramienta para ejecutar consultas SQL SERVER en GCP y obtener datos.
    Usa un engine global para aprovechar el pool de conexiones.
    """
    _engine = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            SERVER   = config.get("DB_GCP_SQLS_SERVER")
            DATABASE = config.get("DB_CP_SQLS_DATABASE")
            USERNAME = config.get("DB_DB_GCP_SQLS_USERNAME")
            PASSWORD = config.get("DB_GCP_SQLS_PASSWORD")
            DRIVER   = config.get("DB_GCP_SQLS_DRIVER")  # "ODBC Driver 18 for SQL Server"

            url = (
                f"mssql+pyodbc://{USERNAME}:{PASSWORD}"
                f"@{SERVER}:1433/{DATABASE}"
                f"?driver={DRIVER.replace(' ', '+')}"
                f"&TrustServerCertificate=yes"
                f"&encrypt=yes"
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
                    'application_name': 'Qagent_GCP_App',
                    'timeout': 30
                }
            )
        return cls._engine

    async def execute(self, consulta: str) -> str:
        try:
            engine = self.get_engine()
            logger.info(f"Ejecutando consulta: {consulta}")

            with engine.connect() as conn:
                df_resultado = pd.read_sql(consulta, conn)
            resultados = df_resultado.to_dict(orient="records")
            filas = len(resultados)

            json_resultado = json.dumps(resultados, default=str)
            tamano_bytes = len(json_resultado.encode("utf-8"))
            logger.info(f"Q Tamaño de respuesta: {tamano_bytes}")

            if tamano_bytes > 500000:
                logger.warning("Respuesta supera los 500KB")
                return "Respuesta demasiado grande. Debes paginar, resumir o limitar con LIMIT. Por favor intenta nuevamente"
            else:
                return json_resultado

        except SQLAlchemyError as err:
            error_message = str(err)
            response = get_random_response("error")
            await cl.Message(response).send()

            if "Invalid column name" in error_message:
                return f"Cometiste el siguiente error en tu consulta: {err}. Por favor revisa el nombre de las columnas en tu base de conocimiento y otorga la respuesta correcta"
            else:
                return f"Cometiste el siguiente error en tu consulta: {err}. Por favor replantea la consulta y otorga la respuesta correcta"

class CreateDataFrameTool(BaseTool):
  
    async def execute(self, message: str, dataframe: str) -> str:
        try:
            import pandas as pd
            import json
            
            logger.info("==== Asi llego el dataframe ====")
            logger.info(dataframe)
            logger.info("===============================")

            # Parseo robusto
            if isinstance(dataframe, str):
                logger.info("Se intentó parsear 1 vez")
                parsed = json.loads(dataframe)
                if isinstance(parsed, str):
                    logger.info("Se intentó parsear 2 vez")
                    parsed = json.loads(parsed)
            else:
                logger.info("Se intentó parsear")
                parsed = dataframe
                
                
            logger.info("==== Asi termino el dataframe ====")
            logger.info(parsed)
            logger.info("===============================")     

            df = pd.DataFrame(parsed)
            elements = [cl.Dataframe(data=df, display="inline", name="Dataframe")]
            await cl.Message(content=message, elements=elements).send()
            return "Dataframe creado exitosamente y enviado al usuario."                     
           
            
        except Exception as err:
            logger.warning("No pudo generar el reporte de forma paginada")
            return f"""
            Error intentar crear al crear el  dataframe: {err}, recuerda el formato de la data debe ser un diccionario con el siguiente formato:
            Los valores deben estar en listas del mismo largo, por ejemplo:
            - "Nombre_columna_1": lista de strings
            - "Nombre_columna_2": lista de números
            Evita los null o reemplazalos por un valor por defecto, por ejemplo: "", "N/A", None, etc.
            Si continua generando error despliega en formato markdown
            """            

class GetDataSQLSLocal(BaseTool):
    """
    Herramienta para ejecutar consultas SQL SERVER en GCP y obtener datos.
    Usa un engine global para aprovechar el pool de conexiones.
    """
    _engine = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            SERVER   = "localhost"
            DATABASE = "qagent"
            DRIVER   = "ODBC Driver 18 for SQL Server"
                        
            url = (
                    f"mssql+pyodbc://@{SERVER}/{DATABASE}"
                    f"?driver={DRIVER.replace(' ', '+')}"
                    f"&Trusted_Connection=yes"
                    f"&TrustServerCertificate=yes"
                    f"&encrypt=no"
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
                    'application_name': 'Qagent_Local_App',
                    'timeout': 30
                }
            )
        return cls._engine

    async def execute(self, consulta: str) -> str:
        try:
            engine = self.get_engine()
            logger.info(f"Ejecutando consulta: {consulta}")

            with engine.connect() as conn:
                df_resultado = pd.read_sql(consulta, conn)
            resultados = df_resultado.to_dict(orient="records")
            filas = len(resultados)           
            
            
            if filas > 100:                
                url_archo_excel = await generar_excel_desde_mysql(resultados)    
                resultados.insert(0, {"Instrucción adicional": f" # Atención, esto es muy importante para el usuario: - El resultado tiene {filas} filas. **Despliega solo las primeras 20 filas e informa al usuario que puede descargar el archivo excel con todos los datos en el siguiente link [Descargar Excel]({url_archo_excel}) renderiza el link en formato md.**"})        
            elif filas >= 50:
                url_archo_excel = await generar_excel_desde_mysql(resultados)    
                resultados.insert(0, {"Instrucción adicional": f" # Atención, esto es muy importante para el usuario: - El resultado tiene {filas} filas. **Despliega solo las primeras 20 filas e informa al usuario que puede descargar el archivo excel con todos los datos en el siguiente link [Descargar Excel]({url_archo_excel}) renderiza el link en formato md.**"})        
            elif filas >= 15:               
                resultados.insert(0, {"Instrucción adicional": f"El resultado tiene {filas} filas. Debes utilizar la herramienta createDataFrame() para paginar los resultados, no formato markdown. **debe estar en formato dict serializado en JSON. Nunca lo envíes como un string anidado ni como tabla Markdown y limpia los campos null.** "})
            else:
                resultados.insert(0, {"Instrucción adicional": f"El resultado tiene {filas} filas. Recuerda que para entregar listas de menos de 20 registros debes utilizar formato markdown"})
            

            json_resultado = json.dumps(resultados, default=str)
            tamano_bytes = len(json_resultado.encode("utf-8"))
            logger.info(f"Q Tamaño de respuesta: {tamano_bytes}")

            if tamano_bytes > 500000:
                logger.warning("Respuesta supera los 500KB")
                return "Respuesta demasiado grande. Debes paginar, resumir o limitar con LIMIT. Por favor intenta nuevamente"
            else:
                return json_resultado

        except SQLAlchemyError as err:
            error_message = str(err)
            response = get_random_response("error")
            await cl.Message(response).send()

            if "Invalid column name" in error_message:
                return f"Cometiste el siguiente error en tu consulta: {err}. Por favor revisa el nombre de las columnas en tu base de conocimiento y otorga la respuesta correcta"
            else:
                return f"Cometiste el siguiente error en tu consulta: {err}. Por favor replantea la consulta y otorga la respuesta correcta"

class GetExplainSQL(BaseTool):
    """
    Herramienta para explicar  consultas SQL SERVER 
    """
    _engine = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            SERVER   = "localhost"
            DATABASE = "qagent"
            DRIVER   = "ODBC Driver 18 for SQL Server"
                        
            url = (
                    f"mssql+pyodbc://@{SERVER}/{DATABASE}"
                    f"?driver={DRIVER.replace(' ', '+')}"
                    f"&Trusted_Connection=yes"
                    f"&TrustServerCertificate=yes"
                    f"&encrypt=no"
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
                    'application_name': 'Qagent_Local_App',
                    'timeout': 30
                }
            )
        return cls._engine

    async def execute(self, consulta: str) -> str:
        try:
            engine = self.get_engine()
            logger.info(f"Explicando consulta: {consulta}")

            conn = engine.raw_connection()
            try:
                cursor = conn.cursor()

                # Activar análisis del plan
                cursor.execute("SET SHOWPLAN_ALL ON;")
                conn.commit()

                # Ejecutar la consulta generada por IA (solo plan, no ejecuta)
                cursor.execute(consulta)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                plan = [dict(zip(columns, row)) for row in rows]

                # Desactivar plan
                cursor.execute("SET SHOWPLAN_ALL OFF;")
                conn.commit()

            finally:
                conn.close()

            # Agregar instrucción al inicio
            plan.insert(0, {
                "Instrucción adicional": (
                    "⚠️ Esta respuesta contiene un plan de ejecución. "
                    "Razona muy bien si la consulta SQL es la adecuada y replantéala si lo estimas conveniente, "
                    "Si no son muchos registros **informa al usuario** cuantos registros contiene y que es posible que se demore un poco en obtener los resultado ya que replantearás la consulta."
                )
            })
            
            logger.info(f"Explicando consulta: {plan}")        
            return json.dumps(plan, indent=2, default=str)

        
        
        except (SQLAlchemyError, pyodbc.Error) as err:
            error_message = str(err)
            logger.warning(f"1 Este es el error: {error_message}")
            
            response = get_random_response("error")
            await cl.Message(response).send()
            
            if "Invalid column name" in error_message:
                return f"> Este error corresponde al plan de ejecución de la consulta: {error_message}. -  Por favor revisa el nombre de las columnas en tu base de conocimiento y otorga la respuesta correcta"
            else:
                return f">  Este error corresponde al plan de ejecución de la consulta: {error_message}. -  Por favor replantea la consulta y otorga la respuesta correcta"
        except Exception as e:
            error_message = str(e)
            logger.warning(f"2 Este es el error: {error_message}")
            return f">  Este error corresponde al plan de ejecución de la consulta: {error_message}. -  Por favor replantea la consulta y otorga la respuesta correcta"

@cl.step(type="tool")
async def getdataMSQL(consulta: str) -> str:
    """
    Herramienta de Assistant
    Genera la respuesta por medio de una consulta SQL a la base de datos.

    Args:
        consulta (str): consulta del usuario para crear la consulta sql 
            
    Returns: 
        Retorna una instrucción de tipo dict al asistente
    """
    tool = GetDataLocalMySQLTool()
    return await tool.execute(consulta=consulta)

@cl.step(type="tool")
async def getdataASQLS(consulta: str) -> str:
    """
    Herramienta de Assistant
    Genera la respuesta por medio de una consulta SQL a la base de datos Azure SQL Server.

    Args:
        consulta (str): consulta del usuario para crear la consulta sql 
            
    Returns: 
        Retorna una instrucción de tipo dict al asistente
    """
    tool = GetDataAzureSQLServer()
    return await tool.execute(consulta=consulta)

@cl.step(type="tool")
async def getdataGSQLS(consulta: str) -> str:
    """
    Herramienta de Assistant
    Genera la respuesta por medio de una consulta SQL a la base de datos Azure SQL Server.

    Args:
        consulta (str): consulta del usuario para crear la consulta sql 
            
    Returns: 
        Retorna una instrucción de tipo dict al asistente
    
    Comentario:    
    Puerto 1433 debe estar abierto y permitido para IP o red.    
    """
    tool = GetDataGCPSQLServer()
    return await tool.execute(consulta=consulta)

async def createDataFrame(message, dataframe: str) -> str:
    """
    Herramienta de Assistant
    Genera la respuesta por medio de una consulta SQL a la base de datos Azure SQL Server.

    Args:
        consulta (str): consulta del usuario para crear la consulta sql 
            
    Returns: 
        Retorna una instrucción de tipo dict al asistente
    """
    tool = CreateDataFrameTool()
    return await tool.execute(message=message, dataframe=dataframe)

@cl.step(type="tool")
async def getdataSQLSLocal(consulta: str) -> str:
    """
    Herramienta de Assistant
    Genera la respuesta por medio de una consulta SQL a la base de datos Azure SQL Server.

    Args:
        consulta (str): consulta del usuario para crear la consulta sql 
            
    Returns: 
        Retorna una instrucción de tipo dict al asistente
    
    Comentario:    
    Puerto 1433 debe estar abierto y permitido para IP o red.    
    """
    tool = GetDataSQLSLocal()
    return await tool.execute(consulta=consulta)

async def explainSQL(consulta: str) -> str:
    """
    Herramienta de Assistant
   Explica la consulta sql para mejorar la respuesta del modelo 

    Args:
        consulta (str): consulta del usuario para crear la consulta sql 
            
    Returns: 
        Retorna la explicación de la consulta
    
    Example:
    
        {
            "StmtText": "SELECT * FROM tabla;",
            "StmtId": 1,
            "NodeId": 0,
            "Parent": NULL,
            "PhysicalOp": "Clustered Index Scan",
            "LogicalOp": "Clustered Index Scan",
            "EstimateRows": 34118.0,
            ...
        }
    
    """
    tool = GetExplainSQL()
    return await tool.execute(consulta=consulta)