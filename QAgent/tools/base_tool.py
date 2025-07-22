"""
Clase base para las herramientas del asistente.
"""

import logging
import json
from abc import ABC, abstractmethod
from typing import Any, Dict

import chainlit as cl

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """
    Clase base abstracta para las herramientas del asistente.
    Define la interfaz común para todas las herramientas.
    """
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Ejecuta la funcionalidad principal de la herramienta
        
        Args:
            kwargs: Argumentos para la ejecución
            
        Returns:
            Resultado de la ejecución
        """
        pass
    
    @cl.step(type="tool")
    async def __call__(self, **kwargs) -> Any:
        """
        Permite que la herramienta sea llamada como una función
        Integra con Chainlit mediante el decorador @cl.step
        
        Args:
            kwargs: Argumentos para la ejecución
            
        Returns:
            Resultado de la ejecución
        """
        try:
            logger.info(f"Ejecutando herramienta {self.__class__.__name__} con args: {kwargs}")
            result = await self.execute(**kwargs)
            
            # Si el resultado es un diccionario o una lista, lo convertimos a JSON
            if isinstance(result, (dict, list)):
                return json.dumps(result, default=str)
            
            return result
        except Exception as e:
            logger.error(f"Error en herramienta {self.__class__.__name__}: {e}")
            raise
