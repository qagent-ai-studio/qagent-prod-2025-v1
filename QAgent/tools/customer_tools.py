"""
Herramientas específica de clientes 
"""

import logging
import json
from typing import Any, Dict

import plotly
import chainlit as cl

from QAgent.tools.base_tool import BaseTool
from QAgent.config.config_manager import config
from QAgent.utils.logging_utils import notify_error, get_random_response

logger = logging.getLogger(__name__)

class BuscaRutCliente(BaseTool):
    """
    CLIENTE COAGRA
    Herramienta para consulta un rut de cliente.
    """
    
    async def execute(self, razon_social: str) -> str:
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
            logger.info(f"Solicitando RUT de cliente: {razon_social}")

            # 1. Buscar en maestro_cliente
            consulta = """
                SELECT rut_cliente 
                FROM maestro_cliente 
                WHERE razon_social LIKE %s 
                LIMIT 1
            """
            cursor.execute(consulta, (f"%{razon_social}%",))
            resultado = cursor.fetchone()

            if resultado:
                return json.dumps(resultado, default=str)
            
            # 2. Buscar en ventas si no está en maestro_cliente
            consulta = """
                SELECT rut_cliente 
                FROM ventas 
                WHERE razon_social LIKE %s 
                LIMIT 1
            """
            cursor.execute(consulta, (f"%{razon_social}%",))
            resultado = cursor.fetchone()

            if resultado:
                return json.dumps({
                    "rut_cliente": resultado["rut_cliente"],
                    "mensaje": "El cliente no está en maestro_cliente, pero sí en ventas. Intentaré hacer un análisis de todas formas."
                }, default=str)
            else:
                return json.dumps({
                    "mensaje": "Cliente no encontrado en maestro_cliente ni en ventas."
                })

        except Exception as err:
            # Gestión de errores
            modulo = "customer_tools"
            funcion = "BuscaRutCliente"
            await notify_error(str(err), modulo, funcion)
            
            # Respuesta al usuario
            response = get_random_response("error")
            await cl.Message(response).send()
            error_message = str(err)
            
            return f"Se cometió el siguiente error al intentar buscar rut de cleinte: {error_message}. Por favor intenta de otra forma"


class SegmentaCliente(BaseTool):
    """
    CLIENTE COAGRA
    Herramienta para segmentar al cliente. Retorna tipo_de_cliente, segmento, subsegmento, comuna_despacho.
    """
    
    async def execute(self, rut: str) -> str:
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
            logger.info(f"Solicitando segmentación de cliente: {rut}")

            # 1. Buscar en maestro_cliente
            consulta = """
              SELECT tipo_de_cliente, segmento, subsegmento, comuna_despacho FROM maestro_cliente WHERE rut_cliente = %s LIMIT 1;
            """
            cursor.execute(consulta, (rut,))
            resultado = cursor.fetchone()

            if resultado:
                return json.dumps(resultado, default=str)            
            else:
                return json.dumps({
                    "mensaje": "Cliente no encontrado en maestro cliente ni en ventas no se puede segmentar."
                })

        except Exception as err:
            # Gestión de errores
            modulo = "customer_tools"
            funcion = "SegmentaCliente"
            await notify_error(str(err), modulo, funcion)
            
            # Respuesta al usuario
            response = get_random_response("error")
            await cl.Message(response).send()
            error_message = str(err)
            
            return f"Se cometió el siguiente error al intentar buscar rut de cleinte: {error_message}. Por favor intenta de otra forma"


class BuscaSku(BaseTool):
    """
    CLIENTE COAGRA
    Herramienta para consulta los sku comprados por el cliente.
    """
    
    async def execute(self, rut: str) -> str:
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
            logger.info(f"Solicitando SKUs del cliente: {rut}")

            consulta = """
                SELECT sku FROM ventas WHERE rut_cliente = %s
            """
            cursor.execute(consulta, (rut,))
            resultado = cursor.fetchall()

            if resultado:
                return json.dumps(resultado, default=str)
            else:
                return json.dumps({
                    "mensaje": "Cliente no encontrado en tabla de ventas."
                })

        except Exception as err:
                # Gestión de errores
                modulo = "customer_tools"
                funcion = "BuscaSku"
                await notify_error(str(err), modulo, funcion)
                
                # Respuesta al usuario
                response = get_random_response("error")
                await cl.Message(response).send()
                error_message = str(err)
                
                return f"Se cometió el siguiente error al intentar buscar rut de cleinte: {error_message}. Por favor intenta de otra forma"


class BuscaRecursosConaf(BaseTool):
    """
    CLIENTE CONAF
    Herramienta para bucar recurso más cercano al foco del siniestro. 
    """
    
    async def execute(self,latitud: str, longitud: str) -> str:
        import requests
        import mysql.connector
        import json
        import urllib.parse
        
        API_KEY = "AIzaSyDak1Rwnebczes1NSlHNv1iHN7fxUKLl7U"
        
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
            logger.info(f"Solicitando recursos más cercanos para : {latitud}, {longitud}")
            destination = f"{latitud},{longitud}"

            # 1. Buscar en maestro_cliente
            consulta = """
              SELECT unidad, comuna, latitud, longitud, clase, tipo, dotacion FROM poa  WHERE id <=8 ;
            """
            cursor.execute(consulta)
            recursos  = cursor.fetchall()

            resultado = []
            for recurso in recursos:
                origen = f"{recurso['latitud']},{recurso['longitud']}"
                url = (
                    f"https://maps.googleapis.com/maps/api/directions/json?"
                    f"origin={origen}&destination={destination}&mode=driving&departure_time=now&key={API_KEY}"
                )
                resp = requests.get(url)
                data = resp.json()
                if not data.get("routes"):
                    # Si no hay ruta, marca nulls
                    recurso.update({
                        "distancia": None,
                        "duracion": None,
                        "polyline": None,
                        "summary": None
                    })
                else:
                    ruta = data["routes"][0]["legs"][0]
                    recurso.update({
                        "distancia": ruta["distance"]["text"],
                        "duracion": ruta.get("duration_in_traffic", ruta["duration"])["text"],
                        "polyline": data["routes"][0]["overview_polyline"]["points"],
                        "summary": data["routes"][0]["summary"],
                        "link_mapa": f"http://127.0.0.1:8000/mapa?origen={urllib.parse.quote_plus(origen)}&destino={urllib.parse.quote_plus(destination)}"

                    })
                resultado.append(recurso)
            
            return json.dumps(resultado, default=str)
        
       
        except Exception as err:
            # Gestión de errores
            modulo = "customer_tools"
            funcion = "SegmentaCliente"
            logger.error(f"Error al solcitar recursos más cercanos en móduoo{modulo}, funcion{funcion} : {str(err)}")
            
            # Respuesta al usuario
            response = get_random_response("error")
            await cl.Message(response).send()
            error_message = str(err)
            
            return f"Se cometió el siguiente error al intentar los recursos de Conaf: {error_message}. Por favor intenta de otra forma"



# Función compatible con la implementación original para mantener CUSTOM_TOOLS
@cl.step(type="tool")
async def busca_rut_cliente(razon_social: str) -> str:
    
    # CLIENTE COAGRA
    tool = BuscaRutCliente()
    return await tool.execute(razon_social=razon_social)


@cl.step(type="tool")
async def segmenta_cliente(rut: str) -> str:
    
    # CLIENTE COAGRA
    tool = SegmentaCliente()
    return await tool.execute(rut=rut)


@cl.step(type="tool")
async def busca_sku(rut: str) -> str:
    
    # CLIENTE COAGRA
    tool = BuscaSku()
    return await tool.execute(rut=rut)


@cl.step(type="tool")
async def recursos_conaf(latitud: str, longitud: str) -> str:
    
    # CLIENTE CONAF
    tool = BuscaRecursosConaf()

    return await tool.execute(latitud=latitud,longitud=longitud )



