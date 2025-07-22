"""
Herramientas para obtener pronóstios de clima.
"""
import requests
import logging
from datetime import datetime
from typing import Dict, Any
import chainlit as cl
from QAgent.tools.base_tool import BaseTool
from QAgent.config.config_manager import config
from QAgent.utils.logging_utils import notify_error

logger = logging.getLogger(__name__)

class ClimaActualTool(BaseTool):
  
    async def execute(self, ciudad: str) -> str:
       
        try:
            
            API_KEY =config.get("WHEATHER_API") 
            url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={ciudad}&lang=es"    
            
            response = requests.get(url)
            response.raise_for_status()
            datos = response.json()

            ubicacion = datos["location"]["name"]
            region = datos["location"]["region"]
            pais = datos["location"]["country"]
            temp = datos["current"]["temp_c"]
            condicion = datos["current"]["condition"]["text"]
            humedad = datos["current"]["humidity"]
            viento = datos["current"]["wind_kph"]

            resumen = (f"En {ubicacion}, {region}, {pais} ahora está {condicion.lower()} "
                    f"con {temp}°C, humedad del {humedad}% y vientos de {viento} km/h.")

            return resumen
           
            
        except Exception as err:
            await notify_error(str(err), "clima_tools", "clima_actual")
            return f"Error intentar acceder al api del clima: {str(err)}, intenta buscando en la web"


class PronosticoClimalTool(BaseTool):
    async def execute(self, ciudad:str, dias:int) -> str:
    
        try:
            API_KEY =config.get("WHEATHER_API")
            url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={ciudad}&days={dias}&lang=es"
            response = requests.get(url)
            response.raise_for_status()
            datos = response.json()

            ubicacion = datos["location"]["name"]
            pais = datos["location"]["country"]
            pronosticos = datos["forecast"]["forecastday"]

            resumen = f"Pronóstico para {ubicacion}, {pais}:\n"
            for dia in pronosticos:
                fecha = dia["date"]
                condicion = dia["day"]["condition"]["text"]
                temp_max = dia["day"]["maxtemp_c"]
                temp_min = dia["day"]["mintemp_c"]
                lluvia = dia["day"]["daily_chance_of_rain"]

                resumen += (f"- {fecha}: {condicion.lower()}, "
                            f"máx {temp_max}°C / mín {temp_min}°C, "
                            f"{lluvia}% de probabilidad de lluvia\n")

            return resumen.strip()
            
        except Exception as err:
            await notify_error(str(err), "clima_tools", "pronostico clima")
            return f"Error intentar acceder al api del clima: {str(err)} intenta buscando en la web"

@cl.step(type="tool")
async def clima_actual(ciudad:str)-> str:
    
    """
    Herramienta de Assistant
    Proporciona el clima actual por medio de la api www.weatherapi.com

    Args:       
        ciudad (str): Ciudad que se desea saber el clima        

    Returns: 
        Retorna un resumen con el clima actual de la ciudad consultada

    Raises:
        Exception: Describe las condiciones bajo las cuales la función podría lanzar una excepción, si es aplicable.

    Nota: Etos datos son almacenados por el asistente [No implementado]        
    """
    tool = ClimaActualTool()
    return await tool.execute(ciudad=ciudad)
    

@cl.step(type="tool")
async def pronostico(ciudad:str,dias=3)-> str:
    
    """
    Herramienta de Assistant
    Proporciona el pronóstico del clima por medio de la api www.weatherapi.com

    Args:       
        ciudad (str): Ciudad que se desea saber el clima        
        dias (int): Cantidad de días a pronosticar (default=3)
    Returns: 
        Retorna un resumen con el clima actual de la ciudad consultada

    Raises:
        Exception: Describe las condiciones bajo las cuales la función podría lanzar una excepción, si es aplicable.

    Nota: Etos datos son almacenados por el asistente [No implementado]        
    """
    
    tool = PronosticoClimalTool()
    return await tool.execute(ciudad=ciudad, dias=dias)