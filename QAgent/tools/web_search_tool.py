"""
Herramientas parabúsquedas en internet.
"""

from openai import OpenAI
import os
import logging
from typing import Dict, Any
import chainlit as cl
from QAgent.tools.base_tool import BaseTool
from QAgent.config.config_manager import config
from QAgent.utils.logging_utils import notify_error

logger = logging.getLogger(__name__)


client = OpenAI( api_key= config.get('AZURE_OPENAI_API_KEY'))

class WebSearchTool(BaseTool):
  
      async def execute(self, user_query: str) -> str:
          
            try:         
                       
                  main_instructions=f'''
                  Eres un asistente útil que hace búsquedas web que ayudan a resolver dudas a los usuarios.
                  No puedes acceder a la web directamente, pero puedes hacer búsquedas en Google y resumir los resultados.
                  Responde en español y proporciona un resumen de los resultados de búsqueda.   
                  Incluye los enlaces relevantes y la información más importante.
                  No incluyas información innecesaria o irrelevante.
                  No incluyas información de la búsqueda en sí, solo el resumen.
                  No puedes buscar en redes sociales, blogs o foros.
                  No puedes buscar en sitios web que no sean de confianza.
                  No puedes buscar en sitios web de pornografía o violencia
                  '''

                  completion = client.chat.completions.create(
                  model="gpt-4o-search-preview",   
                  messages=[
                        {
                              "role": "system", 
                              "content": main_instructions
                        },
                        {
                              "role": "user",
                              "content": user_query,
                        }
                  ],
                  )
                  
                  return completion.choices[0].message.content
            
            except Exception as err:
                  await notify_error(str(err), "utility_tools", "getCurrentDate")
                  return f"Error al obtener la fecha: {str(err)}"




@cl.step(type="tool")
async def web_search(user_query:str)->str:
      """
      Herramienta de Assistant
      Agente que busca en la web según la consulta del usuario

      Args:       
            user_query (str): Consulta de usuario        

      Returns: 
            Retorna un resumen con el resultado de la búsqueda

      Raises:
            Exception: Describe las condiciones bajo las cuales la función podría lanzar una excepción, si es aplicable.

      Nota: 
      Etos datos son almacenados por el asistente [No implementado]
      La busqueda en url especificas debe ser parametrizado en el dashboard 
      el prompt (main_instructions) debe ser parametrizado en el dashboard 
            
      """     
      
      tool = WebSearchTool()
      return await tool.execute(user_query=user_query)

