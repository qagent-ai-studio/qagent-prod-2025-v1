"""
Herramientas para visualización y gráficos.
"""

import logging
import json
from typing import Any, Dict

import plotly
import chainlit as cl

from QAgent.tools.base_tool import BaseTool
from QAgent.utils.logging_utils import notify_error, get_random_response

logger = logging.getLogger(__name__)

class PlotlyChartTool(BaseTool):
    """
    Herramienta para generar gráficos con Plotly.
    """
    
    async def execute(self, message: str, plotly_json_fig: str) -> str:
        """
        Genera un gráfico Plotly y lo muestra en el chat
        
        Args:
            message: Mensaje a mostrar junto con el gráfico
            plotly_json_fig: JSON con la configuración del gráfico
            
        Returns:
            Mensaje de éxito o error
        """
        try:
            fig = plotly.io.from_json(plotly_json_fig)
            elements = [cl.Plotly(name="chart", figure=fig, display="inline")]
            
        
            plot_element = elements[0]
            thread_id = plot_element.thread_id
            element_id = plot_element.id

            await cl.Message(
                content=message, 
                elements=elements,
                actions=[
                    cl.Action(
                        name="fijar_grafico", 
                        label="🖈 Fijar gráfico",
                        tooltip="Fijar gráfico", 
                        payload={
                            "thread_id": cl.user_session.get('chainlit_thread_id'),
                            "element_id": element_id
                        }
                    )
                ]
            ).send()
            
            return 'Ok'
        
        except Exception as err:
            # Gestión de errores
            modulo = "plotting_tools"
            funcion = "draw_plotly_chart"
            await notify_error(str(err), modulo, funcion)
            
            # Respuesta al usuario
            response = get_random_response("error")
            await cl.Message(response).send()
            error_message = str(err)
            
            return f"Se cometió el siguiente error al intentar crear el gráfico: {error_message}. Por favor intenta de otra forma"


# Función compatible con la implementación original para mantener CUSTOM_TOOLS
@cl.step(type="tool")
async def draw_plotly_chart(message: str, plotly_json_fig: str) -> str:
    """
    Herramienta de Assistant
    Genera un gráfico Plotly.

    Args:
        message: Mensaje a mostrar junto con el gráfico
        plotly_json_fig: JSON con la configuración del gráfico
            
    Returns: 
        Mensaje de éxito o error
    """
    tool = PlotlyChartTool()
    return await tool.execute(message=message, plotly_json_fig=plotly_json_fig)
