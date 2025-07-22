"""
Estrategia para el manejo de eventos de OpenAI.
Implementa la lógica específica para los eventos del asistente de OpenAI.
"""

import logging
import json
from typing import Dict, Any, List, Callable

import chainlit as cl
import plotly

from QAgent.events.event_handler import EventStrategy
from QAgent.services.openai_service import OpenAIService
from QAgent.tools import almacenar_interaccion, qtokens
from QAgent.utils.logging_utils import get_random_response

logger = logging.getLogger(__name__)

class OpenAIEventStrategy(EventStrategy):
    """
    Estrategia para manejar eventos del asistente de OpenAI.
    """
    
    def __init__(self):
        """Inicializa la estrategia"""
        self.tool_call_data = {}
    
    async def handle_requires_action(self, handler, data, run_id):
        """
        Maneja los eventos que requieren acción
        
        Args:
            handler: Manejador de eventos
            data: Datos del evento
            run_id: ID de la ejecución
        """
        tool_outputs = []
        
        for tool in data.required_action.submit_tool_outputs.tool_calls:
            func_name = tool.function.name
            func_args = tool.function.arguments

            func_to_call = handler.function_map.get(func_name)  # Obtiene la función del mapa
            logger.info(f"Llamando a la función '{func_name}' con argumentos: {func_args}")
            response = get_random_response("consultando")
            await cl.Message(response).send()
            
            if func_to_call:
                try:
                    func_args_dict = json.loads(func_args)  # Convierte los argumentos a un diccionario
                    tool_call_output = await func_to_call(**func_args_dict)
                    tool_outputs.append({"tool_call_id": tool.id, "output": tool_call_output})
                    
                    # Guardar la información para usar en submit_tool_outputs
                    self.tool_call_data = {
                        "thread_id": handler.current_run.thread_id,
                        "run_id": run_id,
                        "tool_outputs": tool_outputs
                    }
                    
                    #TODO: eliminar la funcionalidad de almacenado de consulta. 
                    # Si es una consulta SQL, guardarla
                    if func_name == "getdata" and "consulta" in func_args_dict:
                        assistant_sql_query = func_args_dict["consulta"]
                        
                        # Obtener thread ID de Chainlit
                        chainlit_thread_id = cl.user_session.get('chainlit_thread_id')
                        if chainlit_thread_id:
                            thread_id = chainlit_thread_id
                            logger.debug(f"Usando thread ID de Chainlit para SQL: {thread_id}")
                        else:
                            thread_id = handler.current_run.thread_id
                            logger.warning(f"Usando thread ID de OpenAI como fallback para SQL: {thread_id}")
                        
                        total_tokens = qtokens(str(assistant_sql_query))
                        agente = cl.user_session.get("agente")
                        await almacenar_interaccion("", "", assistant_sql_query, thread_id, 0, agente)
                    
                except TypeError as te:
                    logger.error(f"TypeError al llamar a la función {func_name}: {te}")
                except Exception as ex:
                    logger.error(f"Error al llamar a la función {func_name}: {str(ex)}")
            else:
                logger.error(f"Función {func_name} no encontrada")
        
        # Enviar todas las salidas de herramientas al mismo tiempo
        openai_service = OpenAIService()
        
        # Crear una función para generar manejadores de eventos
        # Esta función será pasada a OpenAIService para crear un manejador nuevo cada vez
        from QAgent.events.event_handler import EventHandlerFactory
        event_factory = EventHandlerFactory()
        
        def create_event_handler():
            return event_factory.create_handler("openai", handler.assistant_name)
        
        try:
            await openai_service.submit_tool_outputs(
                thread_id=handler.current_run.thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs,
                event_handler_creator=create_event_handler
            )
        except ValueError as ve:
            error_message = str(ve)
            logger.error(f"Error en submit_tool_outputs: {error_message}")
            await cl.Message(error_message).send()
        except Exception as e:
            logger.error(f"Error en submit_tool_outputs: {e}")
            
            error_message = str(e).lower()
            if "string too long" in error_message or "too large" in error_message:
                respuesta = "La respuesta contiene demasiados datos, lo untentaré nuevamente con menos datos."
                await cl.Message(respuesta).send()
                return("La respuesta contiene demasiados datos, por favor, replantea e intenta nuevamente")
                
            elif "invalid_request_error" in error_message:
                respuesta = "No pude encontrar la respuesta, es posible que algún dato no esté actualizado. Por favor intenta con otra consulta."
                await cl.Message(respuesta).send()
                return "No se pude encontrar la respuesta, es posible que algún dato no esté actualizado. hay que intentarlo nuevamente de otra forma"
                
            else:
                # Mensaje de error genérico cuando no podemos identificar el problema específico
                await cl.Message("Lo siento, estoy teniendo problemas para procesar los datos. Puedes intentar con una consulta diferente por favor.").send()
    
    async def handle_text_created(self, handler, text):
        """
        Maneja los eventos de creación de texto
        
        Args:
            handler: Manejador de eventos
            text: Texto creado
        """
        handler.current_message = await cl.Message(author=handler.assistant_name, content="").send()
    
    async def handle_text_delta(self, handler, delta, snapshot):
        """
        Maneja los eventos de delta de texto
        
        Args:
            handler: Manejador de eventos
            delta: Delta del texto
            snapshot: Snapshot del texto
        """
        if delta.value:
            await handler.current_message.stream_token(delta.value)
    
    async def handle_text_done(self, handler, text):
        """
        Maneja los eventos de finalización de texto
        
        Args:
            handler: Manejador de eventos
            text: Texto finalizado
        """
        await handler.current_message.update()
        assistant_response = text.value
        assistant_sql_query = ""
        
        # Obtener thread ID de Chainlit
        chainlit_thread_id = cl.user_session.get('chainlit_thread_id')
        if chainlit_thread_id:
            thread_id = chainlit_thread_id
            logger.debug(f"Usando thread ID de Chainlit para respuesta: {thread_id}")
        else:
            thread_id = handler.current_run.thread_id
            logger.warning(f"Usando thread ID de OpenAI como fallback para respuesta: {thread_id}")
            
        total_tokens = qtokens(assistant_response)
        
        agente = cl.user_session.get("agente")
        await almacenar_interaccion("", assistant_response, assistant_sql_query, thread_id, total_tokens, agente)
        
        if text.annotations:
            await self._process_annotations(handler, text.annotations)
    
    async def _process_annotations(self, handler, annotations):
        """
        Procesa las anotaciones en el texto
        
        Args:
            handler: Manejador de eventos
            annotations: Lista de anotaciones
        """
        openai_service = OpenAIService()
        
        for annotation in annotations:
            if annotation.type == "file_path":
                response = await openai_service.get_file_content(annotation.file_path.file_id)
                file_name = annotation.text.split("/")[-1]
                
                try:
                    fig = plotly.io.from_json(response)
                    element = cl.Plotly(name=file_name, figure=fig)
                    await cl.Message(content="", elements=[element]).send()
                except Exception:
                    element = cl.File(content=response, name=file_name)
                    await cl.Message(content="", elements=[element]).send()
                
                # Hack para arreglar links
                if annotation.text in handler.current_message.content and element.chainlit_key:
                    handler.current_message.content = handler.current_message.content.replace(
                        annotation.text, 
                        f"/project/file/{element.chainlit_key}?session_id={cl.context.session.id}"
                    )
                    await handler.current_message.update()
    
    async def handle_tool_call_delta(self, handler, delta, snapshot):
        """
        Maneja los eventos de delta de llamada a herramienta
        
        Args:
            handler: Manejador de eventos
            delta: Delta de la llamada
            snapshot: Snapshot de la llamada
        """
        if snapshot.id != handler.current_tool_call:
            handler.current_tool_call = snapshot
    
    async def handle_image_file_done(self, handler, image_file):
        """
        Maneja los eventos de finalización de archivo de imagen
        
        Args:
            handler: Manejador de eventos
            image_file: Archivo de imagen
        """
        openai_service = OpenAIService()
        image_id = image_file.file_id
        response = await openai_service.get_file_content(image_id)
        
        image_element = cl.Image(
            name=image_id,
            content=response,
            display="inline",
            size="large"
        )
        
        if not handler.current_message.elements:
            handler.current_message.elements = []
        
        handler.current_message.elements.append(image_element)
        await handler.current_message.update()
