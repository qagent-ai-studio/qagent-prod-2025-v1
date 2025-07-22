"""
Factory y clase base para el manejo de eventos.
Implementa el patrón Strategy para manejar diferentes tipos de eventos.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Type

import chainlit as cl
from openai import AsyncAssistantEventHandler

from QAgent.config.config_manager import config

logger = logging.getLogger(__name__)

class EventStrategy(ABC):
    """
    Clase base abstracta para estrategias de manejo de eventos.
    Define la interfaz común para diferentes tipos de estrategias.
    """
    
    @abstractmethod
    async def handle_requires_action(self, handler, data, run_id):
        """
        Maneja los eventos que requieren acción
        
        Args:
            handler: Manejador de eventos
            data: Datos del evento
            run_id: ID de la ejecución
        """
        pass
    
    @abstractmethod
    async def handle_text_created(self, handler, text):
        """
        Maneja los eventos de creación de texto
        
        Args:
            handler: Manejador de eventos
            text: Texto creado
        """
        pass
    
    @abstractmethod
    async def handle_text_delta(self, handler, delta, snapshot):
        """
        Maneja los eventos de delta de texto
        
        Args:
            handler: Manejador de eventos
            delta: Delta del texto
            snapshot: Snapshot del texto
        """
        pass
    
    @abstractmethod
    async def handle_text_done(self, handler, text):
        """
        Maneja los eventos de finalización de texto
        
        Args:
            handler: Manejador de eventos
            text: Texto finalizado
        """
        pass
    
    @abstractmethod
    async def handle_tool_call_delta(self, handler, delta, snapshot):
        """
        Maneja los eventos de delta de llamada a herramienta
        
        Args:
            handler: Manejador de eventos
            delta: Delta de la llamada
            snapshot: Snapshot de la llamada
        """
        pass
    
    @abstractmethod
    async def handle_image_file_done(self, handler, image_file):
        """
        Maneja los eventos de finalización de archivo de imagen
        
        Args:
            handler: Manejador de eventos
            image_file: Archivo de imagen
        """
        pass


class BaseEventHandler(AsyncAssistantEventHandler):
    """
    Manejador base de eventos que utiliza el patrón Strategy.
    """
    
    def __init__(self, assistant_name: str, strategy: EventStrategy) -> None:
        super().__init__()
        self.assistant_name = assistant_name
        self.strategy = strategy
        self.current_message = None
        self.current_step = None
        self.current_tool_call = None
        
        # Cargar las herramientas
        from QAgent.tools import CUSTOM_TOOLS
        self.function_map = CUSTOM_TOOLS
    
    async def on_event(self, event):
        """
        Maneja eventos generales
        
        Args:
            event: Evento a manejar
        """
        try:
            # Recuperar eventos que se indican con 'requires_action', 
            # ya que estos tendrán nuestras llamadas a herramientas
            if event.event == 'thread.run.requires_action':
                run_id = event.data.id  # Obtener el ID de la ejecución de los datos del evento
                self.current_run.id = run_id
                await self.strategy.handle_requires_action(self, event.data, run_id)
        except Exception as e:
            logger.error(f"Error en on_event: {e}")
    
    async def on_text_created(self, text):
        """
        Maneja la creación de texto
        
        Args:
            text: Texto creado
        """
        try:
            await self.strategy.handle_text_created(self, text)
        except Exception as e:
            logger.error(f"Error en on_text_created: {e}")
    
    async def on_text_delta(self, delta, snapshot):
        """
        Maneja deltas de texto
        
        Args:
            delta: Delta del texto
            snapshot: Snapshot del texto
        """
        try:
            await self.strategy.handle_text_delta(self, delta, snapshot)
        except Exception as e:
            logger.error(f"Error en on_text_delta: {e}")
    
    async def on_text_done(self, text):
        """
        Maneja la finalización de texto
        
        Args:
            text: Texto finalizado
        """
        try:
            await self.strategy.handle_text_done(self, text)
        except Exception as e:
            logger.error(f"Error en on_text_done: {e}")
    
    async def on_tool_call_delta(self, delta, snapshot):
        """
        Maneja deltas de llamada a herramienta
        
        Args:
            delta: Delta de la llamada
            snapshot: Snapshot de la llamada
        """
        try:
            await self.strategy.handle_tool_call_delta(self, delta, snapshot)
        except Exception as e:
            logger.error(f"Error en on_tool_call_delta: {e}")
    
    async def on_image_file_done(self, image_file):
        """
        Maneja la finalización de archivo de imagen
        
        Args:
            image_file: Archivo de imagen
        """
        try:
            await self.strategy.handle_image_file_done(self, image_file)
        except Exception as e:
            logger.error(f"Error en on_image_file_done: {e}")


class EventHandlerFactory:
    """
    Factory para crear manejadores de eventos con diferentes estrategias.
    Implementa el patrón Singleton y Factory.
    """
    
    _instance = None
    _strategies = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventHandlerFactory, cls).__new__(cls)
        return cls._instance
    
    def register_strategy(self, name: str, strategy_class: Type[EventStrategy]) -> None:
        """
        Registra una estrategia
        
        Args:
            name: Nombre de la estrategia
            strategy_class: Clase que implementa la estrategia
        """
        self._strategies[name] = strategy_class
        logger.info(f"Estrategia '{name}' registrada correctamente")
    
    def create_handler(self, strategy_name: str, assistant_name: str) -> BaseEventHandler:
        """
        Crea un manejador con la estrategia especificada
        
        Args:
            strategy_name: Nombre de la estrategia
            assistant_name: Nombre del asistente
            
        Returns:
            Manejador con la estrategia especificada
            
        Raises:
            ValueError: Si la estrategia no está registrada
        """
        if strategy_name not in self._strategies:
            logger.error(f"Estrategia '{strategy_name}' no encontrada")
            raise ValueError(f"Estrategia '{strategy_name}' no encontrada")
        
        strategy = self._strategies[strategy_name]()
        return BaseEventHandler(assistant_name, strategy)
