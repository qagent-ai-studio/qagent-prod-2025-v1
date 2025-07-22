# Módulo de Eventos

El módulo `events` implementa un sistema flexible para manejar los eventos generados durante la interacción del usuario con el asistente. Utiliza los patrones Factory y Strategy para permitir diferentes implementaciones de manejo de eventos.

## Estructura del Módulo

```
events/
├── strategies/           # Implementaciones específicas de estrategias
│   ├── __init__.py       # Exportación de estrategias
│   └── openai_event_strategy.py # Estrategia para eventos de OpenAI
├── __init__.py           # Exportación de componentes clave
└── event_handler.py      # Implementación de manejadores de eventos
```

## Archivos Principales

### event_handler.py

Contiene la implementación del `EventHandlerFactory` y clases base para manejadores de eventos. Características principales:

- **Factory Method**: Implementa el patrón Factory para crear diferentes tipos de manejadores de eventos.
- **Registro de Estrategias**: Permite registrar diferentes estrategias de manejo de eventos.
- **Interfaces Abstractas**: Define interfaces comunes para todos los manejadores.

### strategies/openai_event_strategy.py

Implementa la estrategia específica para manejar eventos generados por OpenAI. Características:

- **Patrón Strategy**: Proporciona una implementación concreta de la estrategia para eventos de OpenAI.
- **Procesamiento Asíncrono**: Maneja eventos de forma asíncrona usando `async/await`.
- **Gestión de Mensajes**: Procesa diferentes tipos de eventos de OpenAI (texto, herramientas, etc.).

## Patrones de Diseño

1. **Factory Method**: Utilizado para crear instancias de manejadores de eventos basados en el tipo.
2. **Strategy**: Permite intercambiar diferentes implementaciones de manejo de eventos.
3. **Dependency Injection**: Las dependencias se inyectan en las estrategias.
4. **Template Method**: Define una estructura común para el procesamiento de eventos.

## Flujo de Trabajo

1. El `EventHandlerFactory` se inicializa y se registran las estrategias disponibles.
2. Cuando se necesita un manejador de eventos, se solicita al factory especificando el tipo.
3. El factory crea una instancia del manejador apropiado con la estrategia correspondiente.
4. El manejador procesa los eventos según la estrategia configurada.

## Ventajas

- **Extensibilidad**: Facilita la adición de nuevos tipos de manejadores y estrategias.
- **Desacoplamiento**: Separa la creación de manejadores de su uso.
- **Flexibilidad**: Permite cambiar fácilmente entre diferentes estrategias de manejo.
- **Mantenibilidad**: Cada estrategia puede modificarse independientemente.
- **Testabilidad**: Las estrategias pueden probarse de forma aislada.

## Ejemplo de Uso

```python
# Registrar estrategias
event_factory = EventHandlerFactory()
event_factory.register_strategy("openai", OpenAIEventStrategy)

# Crear un manejador de eventos
event_handler = event_factory.create_handler("openai", "assistant_name")

# Usar el manejador para procesar eventos
await event_handler.process_event(event_data)
``` 