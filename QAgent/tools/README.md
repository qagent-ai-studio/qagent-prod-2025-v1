# Módulo de Herramientas (Tools)

El módulo `tools` implementa las diversas herramientas que el asistente puede utilizar para realizar acciones específicas. Estas herramientas extienden las capacidades del asistente permitiéndole interactuar con bases de datos, crear visualizaciones, y realizar otras operaciones especializadas.

## Estructura del Módulo

```
tools/
├── __init__.py           # Exporta herramientas disponibles
├── base_tool.py          # Clase base abstracta para todas las herramientas
├── data_tools.py         # Herramientas relacionadas con datos
├── plotting_tools.py     # Herramientas para visualización
├── tool_factory.py       # Factory para crear herramientas
└── utility_tools.py      # Herramientas utilitarias generales
```

## Archivos Principales

### base_tool.py

Define `BaseTool`, una clase abstracta que sirve como base para todas las herramientas. Características:

- **Interfaz Común**: Define una interfaz estándar para todas las herramientas.
- **Integración con Chainlit**: Utiliza decoradores de Chainlit para rastrear la ejecución.
- **Manejo de Errores**: Implementa un manejo de errores consistente.
- **Formateo de Respuestas**: Formatea las respuestas de manera uniforme.

### data_tools.py

Implementa herramientas para acceder y manipular datos, especialmente desde bases de datos. Incluye:

- **Herramientas de Consulta SQL**: Para ejecutar consultas en bases de datos.
- **Transformación de Datos**: Para procesar y dar formato a los resultados.
- **Manejo de Errores de Base de Datos**: Para gestionar errores de conexión y consulta.

### plotting_tools.py

Proporciona herramientas para la visualización de datos:

- **Generación de Gráficos**: Crea diferentes tipos de visualizaciones.
- **Personalización de Visualizaciones**: Configura aspectos visuales de los gráficos.
- **Integración con Chainlit**: Muestra los gráficos en la interfaz de chat.

### tool_factory.py

Implementa el patrón Factory para crear instancias de herramientas:

- **Registro de Herramientas**: Permite registrar diferentes tipos de herramientas.
- **Creación Dinámica**: Crea herramientas basadas en el tipo solicitado.
- **Extensibilidad**: Facilita la adición de nuevas herramientas.

### utility_tools.py

Contiene herramientas utilitarias generales:

- **Conteo de Tokens**: Para monitorear el uso de tokens.
- **Generación de Texto**: Herramientas para formatear y generar texto.
- **Herramientas de Sistema**: Para interactuar con recursos del sistema.

## Patrones de Diseño

1. **Factory Method**: Utilizado en `tool_factory.py` para crear herramientas.
2. **Template Method**: Implementado en `BaseTool` para definir el flujo de ejecución.
3. **Strategy**: Cada herramienta es una estrategia diferente para realizar una tarea.
4. **Composite**: Algunas herramientas pueden componerse de otras más simples.
5. **Decorator**: Utilizado con los decoradores de Chainlit para extender funcionalidad.

## Integración con OpenAI

Las herramientas están diseñadas para ser utilizadas como "funciones" por el asistente de OpenAI:

1. Las herramientas se registran en OpenAI con sus nombres y parámetros.
2. Cuando el asistente decide usar una herramienta, envía una solicitud con los parámetros.
3. El sistema ejecuta la herramienta correspondiente y devuelve los resultados.
4. El asistente recibe los resultados y los incorpora en su respuesta.

## Ejemplo de Uso

```python
from QAgent.tools import CUSTOM_TOOLS

# Las herramientas están disponibles a través de CUSTOM_TOOLS
data_tool = CUSTOM_TOOLS['get_data']

# Ejecutar una herramienta
result = await data_tool.execute(consulta="SELECT * FROM productos LIMIT 10")

# Los resultados pueden mostrarse directamente al usuario o procesarse más
``` 