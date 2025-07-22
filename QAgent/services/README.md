# Módulo de Servicios

El módulo `services` proporciona interfaces y clases para interactuar con servicios externos, principalmente con OpenAI. Encapsula toda la lógica necesaria para comunicarse con APIs externas, ocultando la complejidad y proporcionando una interfaz limpia para el resto de la aplicación.

## Estructura del Módulo

```
services/
├── __init__.py           # Exportación de servicios
└── openai_service.py     # Implementación del servicio de OpenAI
```

## Archivos Principales

### openai_service.py

Implementa `OpenAIService`, que maneja todas las interacciones con la API de OpenAI. Características principales:

- **Gestión de Hilos**: Crea y administra hilos de conversación en OpenAI.
- **Administración de Asistentes**: Accede y configura el asistente de OpenAI.
- **Manejo de Mensajes**: Añade y recupera mensajes en los hilos.
- **Ejecución de Hilos**: Inicia y monitorea la ejecución de hilos con instrucciones personalizadas.
- **Manejo de Errores**: Proporciona gestión de errores robusta para las llamadas a la API.

## Patrones de Diseño

1. **Facade**: El servicio actúa como una fachada, simplificando la interacción con la API de OpenAI.
2. **Singleton**: Se utiliza implícitamente al inicializar el servicio una vez y reutilizarlo.
3. **Async/Await**: Implementa operaciones asíncronas para mejorar el rendimiento en operaciones de E/S.
4. **Dependency Injection**: Recibe dependencias configuradas externamente.

## Funcionamiento

El servicio de OpenAI proporciona estas funcionalidades principales:

1. **Inicialización del Asistente**:
   - Carga el ID del asistente desde la configuración
   - Recupera la instancia del asistente de OpenAI
   - Inicializa las configuraciones necesarias

2. **Gestión de Hilos**:
   - Crea nuevos hilos para conversaciones
   - Añade mensajes a los hilos existentes
   - Recupera el historial de mensajes

3. **Ejecución de Instrucciones**:
   - Ejecuta el hilo con instrucciones personalizadas
   - Administra eventos generados durante la ejecución
   - Procesa las respuestas del asistente

## Ventajas

- **Abstracción**: Oculta los detalles de implementación de la API de OpenAI.
- **Mantenibilidad**: Centraliza el código de interacción con OpenAI.
- **Reutilización**: Proporciona una interfaz consistente para toda la aplicación.
- **Adaptabilidad**: Facilita cambios en la API subyacente sin afectar al resto del código.
- **Testabilidad**: Permite probar las interacciones con OpenAI de forma aislada.

## Ejemplo de Uso

```python
# Inicializar el servicio
service = OpenAIService()

# Crear un nuevo hilo
thread_id = await service.create_thread()

# Añadir un mensaje al hilo
await service.add_message_to_thread(thread_id, "¿Qué puedes decirme sobre este dataset?")

# Ejecutar el hilo con instrucciones personalizadas
await service.run_thread(
    thread_id=thread_id,
    instructions="Actúa como un analista de datos profesional",
    event_handler_creator=create_event_handler
)
``` 