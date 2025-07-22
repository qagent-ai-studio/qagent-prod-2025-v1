"""
Factory para la creación de herramientas del asistente.
"""

import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

class ToolFactory:
    """
    Factory para crear y gestionar herramientas del asistente.
    Implementa el patrón Singleton y Factory.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolFactory, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa el registro de herramientas"""
        self._tools = {}
    
    def register_tool(self, name: str, tool_function: Callable) -> None:
        """
        Registra una herramienta
        
        Args:
            name: Nombre de la herramienta
            tool_function: Función que implementa la herramienta
        """
        self._tools[name] = tool_function
        logger.info(f"Herramienta '{name}' registrada correctamente")
    
    def get_tool(self, name: str) -> Callable:
        """
        Obtiene una herramienta por su nombre
        
        Args:
            name: Nombre de la herramienta
            
        Returns:
            Función que implementa la herramienta
            
        Raises:
            ValueError: Si la herramienta no está registrada
        """
        if name not in self._tools:
            logger.error(f"Herramienta '{name}' no encontrada")
            raise ValueError(f"Herramienta '{name}' no encontrada")
        return self._tools[name]
    
    def get_all_tools(self) -> Dict[str, Callable]:
        """
        Obtiene todas las herramientas registradas
        
        Returns:
            Diccionario con todas las herramientas
        """
        return self._tools.copy()
    
    def unregister_tool(self, name: str) -> None:
        """
        Elimina una herramienta del registro
        
        Args:
            name: Nombre de la herramienta
            
        Raises:
            ValueError: Si la herramienta no está registrada
        """
        if name not in self._tools:
            logger.error(f"Herramienta '{name}' no encontrada")
            raise ValueError(f"Herramienta '{name}' no encontrada")
        del self._tools[name]
        logger.info(f"Herramienta '{name}' eliminada correctamente")
