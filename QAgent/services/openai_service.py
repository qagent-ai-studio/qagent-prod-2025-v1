"""
Servicio para interactuar con OpenAI.
Encapsula todas las llamadas a la API de OpenAI.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from chainlit.element import Element
from openai import OpenAI, AsyncOpenAI, OpenAIError
from openai import OpenAI, AsyncOpenAI, AsyncAssistantEventHandler,  OpenAIError, AzureOpenAI, AsyncAzureOpenAI
# Removemos la importación específica que causa problemas
# from openai.types.beta.threads import Run, Thread

from QAgent.config.config_manager import config

logger = logging.getLogger(__name__)

# --- imports tiktoken ---
import chainlit as cl
import uuid, json
import tiktoken
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
# ----------------------

# justo después de cargar config/DB_URL:
# from QAgent.config.config_manager import config

class TokenCounter:
    _enc = tiktoken.get_encoding("cl100k_base")
    _engine = create_engine(config.get('DB_URL'))
    _Session = sessionmaker(bind=_engine)

    @classmethod
    def count(cls, s: str) -> int:
        if not s:
            return 0
        return len(cls._enc.encode(s))

    @classmethod
    def insert(cls, thread_id: str, token_in: int = 0, token_out: int = 0):
       
        
        session = cls._Session()
        _id = str(uuid.uuid4()) 
               
        try:
            print("Antes de session")
            session.execute(
                text("INSERT INTO tokens (id, id_thread, token_in, token_out) "
                     "VALUES (:id, :thread_id, :token_in, :token_out)"),
                {
                    "id": _id,
                    "thread_id": thread_id,
                    "token_in": int(token_in or 0),
                    "token_out": int(token_out or 0),
                }
            )
            print("Despues de session")
            session.commit()
        except OpenAIError as e:
            logger.error(f"al insertar tokens: {e}")
        finally:
            session.close()



class OpenAIService:
    """
    Servicio para interactuar con OpenAI.
    Implementa el patrón Singleton.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa las conexiones a OpenAI"""
        
        self.proveedor= config.get('PROVEEDOR')
        logger.info(f"Proveedor de OpenAI: {self.proveedor}")
        
        if self.proveedor == 'OPEN_AI':
            self._api_key = config.get('OPENAI_API_KEY')
            self._assistant_id = config.get('OPENAI_ASSISTANT_ID')
        
        if self.proveedor == 'AZURE_OPEN_AI':
            self._api_key = config.get('AZURE_OPENAI_API_KEY')
            self._assistant_id = config.get('AZURE_OPENAI_ASSISTANT_ID')          
            
        
        if not self._api_key:
            logger.error("API Key de OpenAI no configurada")
            raise ValueError("API Key de OpenAI no configurada")
            
        if not self._assistant_id:
            logger.error("ID de asistente de OpenAI no configurado")
            raise ValueError("ID de asistente de OpenAI no configurado")
        
        try:
            if self.proveedor == 'OPEN_AI':
                self._sync_client = OpenAI(api_key=self._api_key)
                self._async_client = AsyncOpenAI(api_key=self._api_key)
            
            
            if self.proveedor == 'AZURE_OPEN_AI':
                self._sync_client = AzureOpenAI(
                    azure_endpoint=config.get('AZURE_OPENAI_ENDPOINT'),
                    api_key=self._api_key,
                    api_version="2024-05-01-preview"
                )
                self._async_client = AsyncAzureOpenAI(
                    azure_endpoint=config.get('AZURE_OPENAI_ENDPOINT'),
                    api_key=self._api_key,
                    api_version="2024-05-01-preview"
                )
            
            
            # Cargar el asistente
            self._assistant = self._sync_client.beta.assistants.retrieve(self._assistant_id)
            
            logger.info(f"Servicio OpenAI inicializado correctamente con proveedor {self.proveedor}")
        except OpenAIError as e:
            logger.error(f"Error al inicializar el servicio OpenAI: {e}")
            raise
    
    @property
    def sync_client(self) -> OpenAI:
        """Cliente síncrono de OpenAI"""
        return self._sync_client
    
    @property
    def async_client(self) -> AsyncOpenAI:
        """Cliente asíncrono de OpenAI"""
        return self._async_client
    
    @property
    def assistant(self) -> Any:
        """Asistente de OpenAI"""
        return self._assistant
    
    async def create_thread(self) -> str:
        """
        Crea un nuevo hilo de conversación
        
        Returns:
            ID del hilo creado
        """
        try:
            thread = await self._async_client.beta.threads.create()
            return thread.id
        except OpenAIError as e:
            logger.error(f"Error al crear hilo: {e}")
            raise
    
    async def add_message_to_thread(self, thread_id: str, role: str, content: str, attachments: Optional[List[Dict[str, Any]]] = None) -> Any:
        """
        Añade un mensaje a un hilo existente
        
        Args:
            thread_id: ID del hilo
            content: Contenido del mensaje
            
        Returns:
            Mensaje creado
        """
        
        chainlit_thread_id = cl.user_session.get('chainlit_thread_id')
        token_in=TokenCounter.count(content)
        try:
            TokenCounter.insert(thread_id=chainlit_thread_id, token_in=token_in)
            print(f"token_in 1:{token_in}")
        except Exception as _:
            logger.debug("TokenCounter add_message_to_thread: skip log")
    
        try:
            
            message = await self._async_client.beta.threads.messages.create(
                thread_id=thread_id,
                role=role,
                content=content,
                attachments=attachments or []
            )
            return message
        except OpenAIError as e:
            logger.error(f"Error al añadir mensaje a hilo: {e}")
            raise
    
    async def run_thread(self, thread_id: str, event_handler_creator) -> None:
        """
        Ejecuta un hilo con instrucciones específicas
        
        Args:
            thread_id: ID del hilo
            instructions: Instrucciones para el asistente
            event_handler_creator: Función para crear un manejador de eventos
        """
        try:
            # Creamos un nuevo event handler para cada run
            event_handler = event_handler_creator()
            
            async with self._async_client.beta.threads.runs.stream(
                thread_id=thread_id,
                assistant_id=self._assistant.id,               
                event_handler=event_handler
            ) as stream:
                await stream.until_done()
        except OpenAIError as e:
            logger.error(f"Error al ejecutar hilo: {e}")
            raise
    
    async def cancel_run(self, thread_id: str, run_id: str) -> Any:
        """
        Cancela una ejecución en curso
        
        Args:
            thread_id: ID del hilo
            run_id: ID de la ejecución
            
        Returns:
            Información sobre la ejecución cancelada
        """
        try:
            return await self._async_client.beta.threads.runs.cancel(
                thread_id=thread_id,
                run_id=run_id
            )
        except OpenAIError as e:
            logger.error(f"Error al cancelar ejecución: {e}")
            raise
    
    async def submit_tool_outputs(self, thread_id: str, run_id: str, tool_outputs: List[Dict], event_handler_creator) -> None:
        """
        Envía las salidas de herramientas al hilo en ejecución
        
        Args:
            thread_id: ID del hilo
            run_id: ID de la ejecución
            tool_outputs: Lista de salidas de herramientas
            event_handler_creator: Función para crear un manejador de eventos
        """
        
        try:
            chainlit_thread_id = cl.user_session.get('chainlit_thread_id')
            payload_str = json.dumps(tool_outputs, ensure_ascii=False)
            token_in=TokenCounter.count(payload_str)
            TokenCounter.insert(thread_id=chainlit_thread_id, token_in=token_in)
            print(f"token_in 2:{token_in}")
        except Exception as _:
            logger.debug("TokenCounter submit_tool_outputs: skip log")
    
        try:
            # Creamos un nuevo event handler para cada submit_tool_outputs
            event_handler = event_handler_creator()
            
            async with self._async_client.beta.threads.runs.submit_tool_outputs_stream(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs,
                event_handler=event_handler
            ) as stream:
                await stream.until_done()
        except OpenAIError as e:
            
            logger.error(f"Error al enviar salidas de herramientas: {e}")
            error_message = str(e).lower()           
            
            if "string too long" in error_message or "too large" in error_message:
                 return f"Este es el error {e}, intenta de nuevo. para ver si se resuelve el problema."
            elif "invalid_request_error" in error_message:
                 return f"Este es el error {e}, intenta de nuevo. para ver si se resuelve el problema."
            else:
                return f"Este es el error {e}, intenta de nuevo. para ver si se resuelve el problema."
                
    
    async def get_file_content(self, file_id: str) -> bytes:
        """
        Obtiene el contenido de un archivo
        
        Args:
            file_id: ID del archivo
            
        Returns:
            Contenido del archivo en bytes
        """
        try:
            response = await self._async_client.files.with_raw_response.content(file_id)
            return response.content
        except OpenAIError as e:
            logger.error(f"Error al obtener contenido del archivo: {e}")
            raise

    async def upload_files(self, files: List[Element]):
        file_ids = []
        try:
            for file in files:
                uploaded_file_id = await self._async_client.files.create(
                    file=Path(file.path), purpose="assistants"
                )
                file_ids.append(uploaded_file_id.id)
            return file_ids    
        except OpenAIError as e:
            logger.error(f"Error al cargar el archivo: {e}")
            raise   