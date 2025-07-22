"""
Herramientas parabúsquedas en internet.
"""
import faiss
import pickle
import numpy as np
import time
from pathlib import Path

from openai import OpenAI, AsyncOpenAI, OpenAIError
from openai import OpenAI, AsyncOpenAI, AsyncAssistantEventHandler,  OpenAIError, AzureOpenAI, AsyncAzureOpenAI
import os
import logging
from typing import Dict, Any
import chainlit as cl
from QAgent.tools.base_tool import BaseTool
from QAgent.config.config_manager import config
from QAgent.utils.logging_utils import notify_error

logger = logging.getLogger(__name__)

# ───── Configuración ─────
client = AzureOpenAI(
    api_key=config.get("AZURE_OPENAI_API_KEY"),
    api_version=config.get("AZURE_OPENAI_API_VERSION"),  
    azure_endpoint=config.get("AZURE_OPENAI_ENDPOINT")
)


# Obtiene el path del directorio actual (tools)
CURRENT_DIR = Path(__file__).resolve().parent
# Sube dos niveles hasta llegar al root del proyecto (qagent-dev-2.2.0)
ROOT_DIR = CURRENT_DIR.parent.parent

# Define la ruta base de la base de vectores
VECTOR_DB_PATH = ROOT_DIR
INDEX_FILE = VECTOR_DB_PATH / config.get("INDEX_FILE") 
METADATA_FILE = VECTOR_DB_PATH / config.get("METADATA_FILE") 
URL_BASE = config.get("URL_BASE")
EMBED_MODEL = config.get("AZURE_EMBEDDING_DEPLOYMENT") 

# ───── Función para obtener el embedding de la pregunta ─────
def embed_query(query: str) -> np.ndarray:
      response = client.embeddings.create(input=[query], model=EMBED_MODEL)
      vector = response.data[0].embedding
      logger.info(f"Embedding generado con {len(vector)} dimensiones.")
      return np.array(response.data[0].embedding, dtype="float32").reshape(1, -1)

# ───── Función para buscar contexto en índice combinado ─────
def buscar_contexto(query: str, top_k: int = 3) -> str:
      vector = embed_query(query)

      # Cargar índice y metadatos
      index = faiss.read_index(str(INDEX_FILE))
      with open(METADATA_FILE, "rb") as f:
            metadata = pickle.load(f)["metadata"]

      D, I = index.search(vector, top_k)
      resultados = []
      for score, idx in zip(D[0], I[0]):
        if idx < len(metadata):
            meta = metadata[idx]
            url = f"{URL_BASE}{meta['source_pdf']}"
            resultados.append(
                f"[{meta['source_pdf']} - página {meta['page']}]\n📎 {url}\n{meta['text']}"
            )

      return "\n\n---\n\n".join(resultados)

class FaissAiSearchTool(BaseTool):
      
      async def execute(self, consulta: str) -> str:
          
            try:         
                  return buscar_contexto(consulta)
            
            except Exception as err:
                  await notify_error(str(err), "faiss_ai_search_tool", "faiss_ai_search")
                  return f"Error al obtener la fecha: {str(err)}"

@cl.step(type="tool")
async def faiss_ai_search(consulta:str)->str:
      """
      Herramienta de Assistant
      Agente que busca en una base vectorial FAISS Local

      Args:       
            consulta (str): Consulta de usuario        

      Returns: 
            Retorna un resumen con el resultado de la búsqueda

      Raises:
            Exception: Describe las condiciones bajo las cuales la función podría lanzar una excepción, si es aplicable.

      Nota: 
      Etos datos son almacenados por el asistente [No implementado]
      La busqueda en url especificas debe ser parametrizado en el dashboard 
      el prompt (main_instructions) debe ser parametrizado en el dashboard 
            
      """     
      
      tool = FaissAiSearchTool()
      return await tool.execute(consulta=consulta)

