"""
Herramientas para visualización y gráficos.
"""

import logging
import json
from typing import List
import plotly 
import plotly.graph_objects as go
import chainlit as cl
from chainlit.element import Plotly
import requests
from QAgent.tools.base_tool import BaseTool
from QAgent.utils.logging_utils import notify_error, get_random_response

logger = logging.getLogger(__name__)



class BlueRaptorTool(BaseTool):
    """
    Herramienta para generar gráficos forecast usando la API de Blue Raptor y Plotly.
    """

    async def execute(self, serie: List[float]) -> str:
        """
        Genera un gráfico Plotly con los datos de forecast.

        Args:
            serie: Lista de valores numéricos (serie temporal original)

        Returns:
            Mensaje de éxito o error
        """
        try:
            # Formatear serie para URL
            serie_str = ",".join(str(x) for x in serie)
            url = f"https://app.blueraptor.cl/api/v2/?d=QAGENT_2QZU0GJW8NX1F,{serie_str}"
            
            # Llamar API
            headers = {"User-Agent": "QAgent/1.0", "Accept": "application/json"}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise Exception(f"HTTP error: {response.status_code}")

            data = response.json() 

            if data.get("ERR") != "Ninguno.":
                raise Exception(f"API error: {data.get('ERR')}")

            # === Construir gráfico Plotly ===
            ORI, EST, PRO = data["ORI"], data["EST"], data["PRO"]
            I50, S50 = data["I50"], data["S50"]
            I75, S75 = data["I75"], data["S75"]
            I95, S95 = data["I95"], data["S95"]

            x = list(range(len(ORI)))
            x_proj = list(range(len(ORI), len(ORI) + len(PRO)))

            fig = go.Figure()

            fig.add_trace(go.Scatter(x=x, y=ORI, mode="lines+markers", name="Datos originales", line=dict(color="blue")))
            fig.add_trace(go.Scatter(x=x, y=EST, mode="lines", name="Estimación", line=dict(color="green", dash="dot")))
            fig.add_trace(go.Scatter(x=x_proj, y=PRO, mode="lines+markers", name="Proyección", line=dict(color="orange")))

            # Intervalos de confianza
            fig.add_trace(go.Scatter(x=x_proj + x_proj[::-1], y=S95 + I95[::-1], fill='toself',
                                     fillcolor='rgba(255,0,0,0.1)', line=dict(color='rgba(255,0,0,0)'), name='Confianza 95%'))
            fig.add_trace(go.Scatter(x=x_proj + x_proj[::-1], y=S75 + I75[::-1], fill='toself',
                                     fillcolor='rgba(255,165,0,0.2)', line=dict(color='rgba(255,165,0,0)'), name='Confianza 75%'))
            fig.add_trace(go.Scatter(x=x_proj + x_proj[::-1], y=S50 + I50[::-1], fill='toself',
                                     fillcolor='rgba(0,255,0,0.3)', line=dict(color='rgba(0,255,0,0)'), name='Confianza 50%'))

            fig.update_layout(
                title="Forecast con Intervalos de Confianza (Blue Raptor)",
                xaxis_title="Índice Temporal",
                yaxis_title="Valor",
                legend_title="Leyenda",
                template="plotly_white"
            )

            elements = [Plotly(name="chart", figure=fig, display="inline")]
            plot_element = elements[0]

            await cl.Message(
                content="📈 Aquí está el forecast generado:",
                elements=elements,
                actions=[
                    cl.Action(
                        name="fijar_grafico",
                        label="🖈 Fijar gráfico",
                        tooltip="Fijar gráfico",
                        payload={
                            "thread_id": cl.user_session.get('chainlit_thread_id'),
                            "element_id": plot_element.id
                        }
                    )
                ]
            ).send()
            
            insight_prompt = f"""
            Gráfico generado exitosamente.

            📊 Por favor analiza los siguientes datos retornados por la API de forecasting y entrega tu insight.

            Estos son los datos numéricos utilizados:

            - ORI (Original): {data['ORI']}
            - EST (Estimación): {data['EST']}
            - PRO (Proyección): {data['PRO']}
            - Intervalos de confianza:
            - 50%: inferior={data['I50']}, superior={data['S50']}
            - 75%: inferior={data['I75']}, superior={data['S75']}
            - 95%: inferior={data['I95']}, superior={data['S95']}

            📘 Definiciones para ayudarte:

            - **Estimación**: Modelo ajustado a los datos históricos, representado en verde. Debe asemejarse a los datos reales sin sobreajuste.
            - **Proyección**: Forecast hacia el futuro, representado en amarillo.
            - **Intervalos de confianza (al N%)**: Rango dentro del cual se espera que caiga el valor real con probabilidad N%. Representado como bandas de color.

            🧠 Por favor, entrega un resumen de:
            - Qué patrón observas entre ORI y EST.
            - Cómo se comporta la proyección (PRO).
            - Qué tan amplios o estrechos son los intervalos de confianza.
            """

            return insight_prompt

        except Exception as err:
            await notify_error(str(err), "plotting_tools", "BlueRaptorTool.execute")
            response = get_random_response("error")
            await cl.Message(response).send()
            return f"❌ Error al generar el gráfico: {err}"



@cl.step(type="tool")
async def blueRaptor(serie: List[float]) -> str:
    """
    Genera un gráfico Plotly con un forecast a partir de una serie temporal.

    Args:
        serie: Lista de valores numéricos (float)

    Returns:
        Mensaje de éxito o error
    """
    tool = BlueRaptorTool()
    return await tool.execute(serie=serie)

"""
{
  "name": "blueRaptor",
  "description": "Genera un gráfico de forecast a partir de una serie temporal utilizando la API de Blue Raptor.",
  "parameters": {
    "type": "object",
    "required": [
      "serie"
    ],
    "properties": {
      "serie": {
        "type": "array",
        "items": {
          "type": "number"
        },
        "description": "Serie temporal original como una lista de números (por ejemplo: [400, 523.1, 755, ...])"
      }
    }
  }
}

"""