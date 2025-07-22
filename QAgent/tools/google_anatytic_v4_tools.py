#pip install google-analytics-data google-auth google-api-core

import json
from typing import List, Dict
from google.analytics.data_v1beta import BetaAnalyticsDataClient # type: ignore
from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest # type: ignore
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError
from google.analytics.data_v1beta.types import RunReportResponse # type: ignore
import math

import faiss # type: ignore
import numpy as np
import openai
import pickle
from pathlib import Path
import os
import logging
from typing import Dict, Any
import chainlit as cl
from QAgent.tools.base_tool import BaseTool
from QAgent.config.config_manager import config
from QAgent.utils.logging_utils import notify_error


logger = logging.getLogger(__name__)


# Ruta base: sube 1 nivel para llegar a /tools (desde /tools/google_anatytic_v4_tools.py)
BASE_DIR = Path(__file__).resolve().parent  # Ahora apunta a QAgent/tools/

# Credenciales (ahora dentro de tools/credentials/)
GA4_KEY_PATH = BASE_DIR / "credentials" / "google_anatytic_v4_tools.json"

# Storage (en la raíz del proyecto: QAgent/storage/)
STORAGE_DIR = BASE_DIR.parent / "storage" / "google_anatytic_v4_tools"  # Usamos .parent para subir a QAgent/

# Archivos FAISS
FAISS_INDEX_PATH = STORAGE_DIR / "dimensiones_metricas.index"
METADATA_PATH = STORAGE_DIR / "dimensiones_metricas.pkl"

# Configuración
GA4_PROPERTY_ID = config.get('GA4_PROPERTY_ID')  # Asegúrate de definir 'config'
MODEL = "text-embedding-3-small"

openai.api_key =config.get('AZURE_OPENAI_API_KEY')
openai.api_type = 'azure' #'azure' en caso que sea azure'


'''
API que permite consultar eventos, usuarios, sesiones y conversiones aplicando dimensiones, métricas, filtros, segmentos, ordenamientos y rangos de fechas.

1. Dimensiones (Dimension)
Son atributos por los cuales se pueden agrupar o segmentar los datos, como:

country, city
deviceCategory, browser
date, hour
eventName
source, medium, campaignId, campaignName
pagePath, pageTitle
newVsReturning
platform (web, app, etc.)

2. Métricas (Metric)
Son valores numéricos agregados, como:

- activeUsers
- sessions
- engagementRate
- bounceRate
- eventCount
- conversions
- newUsers
- averageSessionDuration
- totalRevenue
- screenPageViews

Tipos: Enteros, flotantes, porcentajes, duración, dinero.

Cada consulta define un rango de fechas:

'''

def response_to_json_dynamic(response):
    """
    Función utilizada por la tools principal para formatear la respuesta en json
    """
    data = []
    metric_names = [m.name for m in response.metric_headers]
    dimension_names = [d.name for d in response.dimension_headers]

    for row in response.rows:
        row_data = {}

        # Dimensiones
        for i, dim_value in enumerate(row.dimension_values):
            row_data[dimension_names[i]] = dim_value.value

        # Métricas
        for j, met_value in enumerate(row.metric_values):
            met_name = metric_names[j]
            value = met_value.value
            try:
                value = int(value)
            except ValueError:
                value = float(value)

            # Verifica si hay transformación personalizada
            if met_name in transform_map:
                row_data[f"{met_name}_raw"] = value
                row_data[met_name] = transform_map[met_name](value)
            else:
                row_data[met_name] = value

        data.append(row_data)

    return data

# en construcción
def response_to_csv(response):
      lines = ["country,activeUsers"]
      for row in response.rows:
            country = row.dimension_values[0].value
            users = row.metric_values[0].value
            lines.append(f"{country},{users}")
      return "\n".join(lines)


# Diccionario para legibilizar la respuesta del reporte
transform_map = {
    "engagementRate": lambda v: f"{round(v * 100, 2)}%",
    "bounceRate": lambda v: f"{round(v * 100, 2)}%",
    "userConversionRate": lambda v: f"{round(v * 100, 2)}%",
    "sessionConversionRate": lambda v: f"{round(v * 100, 2)}%",
    "cartToViewRate": lambda v: f"{round(v * 100, 2)}%",
    "purchaseToViewRate": lambda v: f"{round(v * 100, 2)}%",    
    "averageSessionDuration": lambda v: seconds2minutes(v),
    "userEngagementDuration": lambda v: seconds2minutes(v),    
    "totalRevenue": lambda v: f"${round(v, 2)}",
    "purchaseRevenue": lambda v: f"${round(v, 2)}",
    "averagePurchaseRevenue": lambda v: f"${round(v, 2)}"
}

# Función utilizada por transform_map en los casos
# donde hay que transformar segundos a minutos 60.0000 -> 1m 0s 
def seconds2minutes(seconds):
    if not isinstance(seconds, (int, float)):
        return "N/A"
    minutes = math.floor(seconds / 60)
    remainder = round(seconds % 60)
    return f"{minutes}m {remainder}s"



class GoogleAnalyticReportTool(BaseTool):
     
    async def execute(self, dimensions: List[str], metrics: List[str],start_date: str, end_date: str)  -> RunReportResponse:
        try:      
            credentials = service_account.Credentials.from_service_account_file(GA4_KEY_PATH)

            client = BetaAnalyticsDataClient(credentials=credentials)
            request = RunReportRequest(
                  property=f"properties/{GA4_PROPERTY_ID}",
                  dimensions=[Dimension(name=d) for d in dimensions],
                  metrics=[Metric(name=m) for m in metrics],
                  date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
            )
            
            report = client.run_report(request)
            return json.dumps(response_to_json_dynamic(report), indent=2)

        except GoogleAPIError as e:
                    logger.error(f"GoogleAnalyticTool: {e}")
                    return f"Se cometió el siguiente error al intentar acceder al reporte de Google Analytic {e}"



def get_embedding(text: str, model: str) -> list:
    response = openai.embeddings.create(input=[text], model=model)
    return response.data[0].embedding


class GoogleAnalyticConceptTool(BaseTool):
    
    async def execute(self, query: str, top_k: int = 5) -> str:
        try:
            if not FAISS_INDEX_PATH.is_file():
                raise FileNotFoundError(f"Índice FAISS no encontrado en: {FAISS_INDEX_PATH}")
            
            index = faiss.read_index(str(FAISS_INDEX_PATH))

            with open(METADATA_PATH, "rb") as f:
                meta = pickle.load(f)
                texts = meta["texts"]
                df = meta["df"]

            query_vector = np.array(
                get_embedding(query, model=MODEL)
            ).astype("float32").reshape(1, -1)

            distancias, indices = index.search(query_vector, top_k)

            resultados = []
            mapping = {}  # ← nuevo

            for idx in indices[0]:
                meta_row = df[idx]
                resultados.append({
                    "match": texts[idx],
                    "metadata": meta_row
                })
                # construir el mapeo identificador → descripción
                mapping[meta_row["identificador"]] = meta_row["descripcion"]

            payload = {
                "results": resultados,
                "identificadores": mapping
            }

            # Devolver un string JSON listo para consumir
            return json.dumps(payload, ensure_ascii=False, indent=2)
  
        except Exception as err:
            return (
                "Se cometió el siguiente error al intentar obtener los datos en la "
                f"base vectorial de Google Analytics: {err}. Por favor intenta de otra forma."
            )

            

@cl.step(type="tool")
async def google_analytic_report(
      dimensions: List[str],
      metrics: List[str],
      start_date: str,
      end_date: str
      ) -> RunReportResponse:
    """
      Ejecuta una consulta a la API de Google Analytics 4 (GA4) para obtener reporte basado en métricas y dimensiones específicas

      Args:
            dimensions (List[str]): Lista de nombres de dimensiones a extraer (máximo 9).
            metrics (List[str]): Lista de nombres de métricas a extraer (máximo 10).
            start_date (str): Fecha de inicio del rango (formato 'YYYY-MM-DD').
            end_date (str): Fecha de fin del rango (formato 'YYYY-MM-DD').

      Returns:
            RunReportResponse: Objeto de respuesta con los datos solicitados.

      Raises:
            ValueError: Si se excede el número permitido de métricas o dimensiones.
            GoogleAPIError: Si ocurre un error en la consulta a la API.
      """
    if len(dimensions) > 9:
            logger.error(f"No se pueden usar más de 9 dimensiones por consulta")
            return  "No se pueden usar más de 9 dimensiones por consulta, informa al usuario para que elimine alguna dimensión"
    if len(metrics) > 10:
            logger.error(f"No se pueden usar más de 10 métricas por consulta")
            return "No se pueden usar más de 10 métricas por consulta, informa al usuario para que elimine alguna métricas"
    
    tool = GoogleAnalyticReportTool()
    return await tool.execute(dimensions=dimensions, metrics=metrics,start_date=start_date, end_date=end_date)



@cl.step(type="tool")
async def google_analytic_concept(query: str) -> str:
    """
      Ejecuta una consulta a la base de conocimiento vectorial donde se encuentran las métricas y dimensiones de Google Analytics 4 (GA4)

      Args:
            query (str): consulta semántica en lenguaje natural.            

      Returns:
           texto con los datos solicitados.

      Raises:            
           
      """   
    
    tool = GoogleAnalyticConceptTool()
    return await tool.execute(query=query)


