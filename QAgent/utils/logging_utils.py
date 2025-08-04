"""
Utilidades para logging y notificación de errores.
"""

import logging
from datetime import datetime
from typing import Optional

from QAgent.repositories.postgres_repository import PostgresRepository

logger = logging.getLogger(__name__)

def configure_logging(level=logging.INFO):
    """
    Configura el sistema de logging para la aplicación
    
    Args:
        level: Nivel de logging (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger.info("Sistema de logging configurado")

async def notify_error(mensaje: str, modulo: str, funcion: str):
    """
    # Registra un error en la base de datos
    
    # Args:
    #     mensaje: Mensaje de error
    #     modulo: Módulo donde ocurrió el error
    #     funcion: Función donde ocurrió el error
    # """
    pass
    # hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # try:
    #     repo = PostgresRepository()
    #     await repo.execute(
    #         """
    #         INSERT INTO qa_log (mensaje, modulo, funcion, fecha)
    #         VALUES ($1, $2, $3, $4)
    #         """,
    #         {
    #             "$1": mensaje,
    #             "$2": modulo,
    #             "$3": funcion,
    #             "$4": hora_actual
    #         }
    #     )
    #     logger.info(f"Error registrado: {mensaje}")
    # except Exception as db_err:
    #     logger.error(f"Error al registrar en la base de datos: {db_err}")

def get_random_response(response_type: str = "error") -> str:
    """
    Obtiene una respuesta aleatoria para mostrar al usuario
    
    Args:
        response_type: Tipo de respuesta ("error" o "tiempo")
    
    Returns:
        Mensaje aleatorio
    """
    if response_type == "error":
        responses = [
            "Estoy replanteando la consulta, por favor dame un momento.",
            "Permíteme unos instantes para revisar la información.",
            "Estoy trabajando en tu solicitud, un momento por favor.",
            "Déjame verificar los detalles, esto tomará solo un momento.",
            "Por favor, espera un instante mientras reviso la información.",
            "Estoy buscando la mejor solución para ti, dame un momento.",
            "Gracias por tu paciencia, ya casi lo tengo.",
            "Solo un momento más, estoy revisando los datos.",
            "Déjame asegurarme de que todo esté correcto, un momento por favor.",
            "Estoy en ello, gracias por tu paciencia.",
            "Un momento mientras confirmo la información.",
            "Estoy analizando tu solicitud, esto tomará solo un instante.",
            "Por favor, espera un momento mientras termino de revisar.",
            "Estoy ajustando algunos detalles, dame unos segundos.",
            "Gracias por tu paciencia, ya estoy trabajando en ello."
        ]
        
    elif response_type == "consultando":
        responses = [
            "Estoy pensando la consulta que debo ejecutar...",
            "Dame un momento para comprender la consulta.",
            "Estoy trabajando en tu solicitud, un momento por favor.",
            "De inmediato voy a consultar en la base de datos, puede tomar un momento",
            "Estoy procesando tu solicitud, esto puede tardar unos segundos.",
            "Voy a generar la consulta en mis datos, gracias por tu paciencia.",
            "Un momento, estoy formulando la mejor consulta posible.",
            "Voy a construir la consulta para obtener los datos correctos.",
            "Voy a diseñar la instrucción SQL adecuada, aguarda un momento.",
            "Traduciendo la solicitud a lenguaje de base de datos...",
            "Dame unos segundos para definir correctamente los filtros y condiciones."
           
        ]            
        
    elif response_type == "analisis":
        responses = [
            "Analizando la información disponible, ya te respondo.",
            "Revisando los datos para darte una respuesta precisa.",
            "Revisando la respuesta.",
            "Estoy preparando la respuesta, aguarda un instante.",
            "Interpretando los resultados obtenidos...",
            "Procesando los datos para ofrecerte una conclusión clara.",
            "Estoy validando que los datos coincidan con lo que solicitaste.",
            "Realizando el análisis final antes de entregarte la respuesta.",
            "Tengo la información, ahora la estoy interpretando para ti."
        ]            
    else:  # tiempo
        responses = [
            "Estoy teniendo problemas para procesar los datos, dame unos segundos para intentar solucionarlo ",
            "Estoy presentando problemas con la respuesta, permíteme unos instantes para revisar la información.",
            "Estoy trabajando en tu solicitud, un momento por favor.",
            "Estoy buscando la mejor solución para ti, dame unos segundos.",
            "Algo paso con los datos, pero voy a tratar de resolverlo",
            "Hubo un problema técnico pero voy a intentar solucionarlo, gracias por tu paciencia.",
        ]
    
    import random
    return random.choice(responses)
