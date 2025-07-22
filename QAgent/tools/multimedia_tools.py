"""
Herramientas para visualización y gráficos.
"""

import logging
import json
from typing import Any, Dict

import chainlit as cl

from QAgent.tools.base_tool import BaseTool
from QAgent.config.config_manager import config
from QAgent.utils.logging_utils import notify_error, get_random_response

logger = logging.getLogger(__name__)

class VideoTool(BaseTool):
    """
    Herramienta para generar gráficos con Plotly.
    """
    
    async def execute(self, message: str, name: str , url: str) -> str:
        """
        Muestra un video 
        
        Args:
            message: Mensaje a mostrar junto con Video
            name: Nombre del video
            url: url del video
            
        Returns:
            Mensaje de éxito o error
        """
        try:
           
            elements = [
                cl.Video(name=name, path=url, display="inline"),
            ]
            await cl.Message(
                content=message,
                elements=elements,
            ).send()
            
            return 'Video enviado'
                
        except Exception as err:
            # Gestión de errores
            modulo = "multimedia_tools"
            funcion = "video_tool"
            await notify_error(str(err), modulo, funcion)
            
            # Respuesta al usuario
            response = get_random_response("error")
            await cl.Message(response).send()
            error_message = str(err)
            
            return f"Se cometió el siguiente error al intentar mostrar el video: {error_message}. Por favor intenta de otra forma"


class PdfTool(BaseTool):
    """
    Herramienta para generar gráficos con Plotly.
    """
    
    async def execute(self, message: str, name: str , pdf: str) -> str:
        """
        Muestra un PDF 
        
        Args:
            message: Mensaje a mostrar junto con PDF
            name: Nombre del PDF
            pdf: documento pdf con extensión .pdf
            
        Returns:
            Mensaje de éxito o error
        """
        try:
           
            path = config.get('MEDIA_PDF_PATH') 
            path = path + pdf
            
            name = name+ ".pdf"
            elements = [
                cl.Pdf(name=name, display="inline", path=path, page=1)
            ]

            await cl.Message(content=message, elements=elements).send()            
            return 'PDF enviado'
                
        except Exception as err:
            # Gestión de errores
            modulo = "multimedia_tools"
            funcion = "video_tool"
            await notify_error(str(err), modulo, funcion)
            
            # Respuesta al usuario
            response = get_random_response("error")
            await cl.Message(response).send()
            error_message = str(err)
            
            return f"Se cometió el siguiente error al intentar desplegar el pdf: {error_message}. Recuerda que debes "


async def video_tool(message: str, name: str, url:str) -> str:
   
    tool = VideoTool()
    return await tool.execute(message=message,name=name,url=url )


async def pdf_tool(message: str, name: str, pdf:str) -> str:
   
    tool = PdfTool()
    return await tool.execute(message=message,name=name,pdf=pdf )



#02_ETI_HDS_KANDA.pdf

