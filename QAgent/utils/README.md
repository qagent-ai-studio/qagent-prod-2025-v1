# Módulo de Utilidades

El módulo `utils` proporciona funciones y clases de utilidad general que son utilizadas en toda la aplicación. Contiene herramientas comunes para logging, manejo de errores, formateo de datos y otras funcionalidades transversales que no pertenecen específicamente a ningún otro módulo.

## Estructura del Módulo

```
utils/
├── __init__.py           # Exportación de utilidades
└── logging_utils.py      # Utilidades para logging
```

## Archivos Principales

### logging_utils.py

Proporciona funciones y configuraciones para el sistema de logging de la aplicación. Características principales:

- **Configuración Centralizada**: Establece una configuración uniforme para todos los loggers.
- **Niveles de Log**: Gestión de diferentes niveles de log (DEBUG, INFO, WARNING, ERROR).
- **Formateo de Mensajes**: Define formatos estándar para los mensajes de log.
- **Rotación de Archivos**: Configura la rotación de archivos de log para evitar archivos demasiado grandes.
- **Notificación de Errores**: Proporciona utilidades para notificar errores graves.
- **Respuestas Aleatorias**: Genera respuestas aleatorias para situaciones específicas.

## Funciones Principales

### configure_logging()

Configura el sistema de logging con los parámetros especificados:

```python
def configure_logging(level=logging.INFO, log_file=None):
    """
    Configura el sistema de logging.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        log_file: Ruta al archivo de log (opcional)
    """
    # Configuración del sistema de logging
```

### notify_error()

Notifica errores graves a través de diferentes canales (logs, correos, etc.):

```python
async def notify_error(error_message, context=None):
    """
    Notifica un error grave.
    
    Args:
        error_message: Mensaje de error
        context: Contexto adicional del error
    """
    # Notificación del error
```

### get_random_response()

Genera respuestas aleatorias para diferentes situaciones:

```python
def get_random_response(tipo):
    """
    Obtiene una respuesta aleatoria del tipo especificado.
    
    Args:
        tipo: Tipo de respuesta ('tiempo', 'error', etc.)
        
    Returns:
        Una respuesta aleatoria del tipo especificado
    """
    # Selección y retorno de una respuesta aleatoria
```

## Ventajas

- **Reutilización**: Centraliza funcionalidades comunes para evitar duplicación de código.
- **Consistencia**: Garantiza un comportamiento uniforme en toda la aplicación.
- **Mantenibilidad**: Facilita los cambios en funcionalidades transversales.
- **Separación de Preocupaciones**: Aísla funcionalidades utilitarias de la lógica de negocio.

## Patrones y Principios

1. **DRY (Don't Repeat Yourself)**: Evita la duplicación de código centralizando funcionalidades comunes.
2. **Principio de Responsabilidad Única**: Cada utilidad tiene una responsabilidad bien definida.
3. **Composición sobre Herencia**: Las utilidades se diseñan para ser utilizadas por composición.

## Uso del Módulo

El módulo de utilidades se utiliza en toda la aplicación:

```python
from QAgent.utils.logging_utils import configure_logging, notify_error

# Configurar el sistema de logging
configure_logging(level=logging.DEBUG)

# Notificar un error
try:
    # Alguna operación
except Exception as e:
    await notify_error(f"Error en la operación: {e}") 