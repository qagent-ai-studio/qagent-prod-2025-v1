# Módulo QAgent

El módulo QAgent es el núcleo de la aplicación, conteniendo toda la lógica de negocio y la implementación de los diferentes componentes del sistema. Está estructurado siguiendo principios de arquitectura limpia y patrones de diseño modernos.

## Estructura del Módulo

```
QAgent/
├── config/               # Configuración centralizada
├── events/               # Manejo de eventos y estrategias
│   └── strategies/       # Implementaciones específicas de estrategias
├── repositories/         # Acceso a datos
├── services/             # Servicios externos
├── tools/                # Herramientas para el asistente
├── utils/                # Utilidades comunes
├── send_mail/            # Funcionalidad de correo
├── __init__.py           # Inicialización del módulo
├── prompt.py             # Instrucciones para el asistente
├── Qtools.py             # Definición adicional de herramientas
└── conexion.py           # Utilidades de conexión a bases de datos
```

## Archivos Principales

### __init__.py

Define las exportaciones principales del módulo, haciendo accesibles los componentes clave desde el exterior.

### prompt.py

Contiene las instrucciones detalladas para el asistente de OpenAI. Estas instrucciones definen el comportamiento, tono y capacidades del asistente, proporcionando el contexto necesario para responder adecuadamente a las consultas de los usuarios.

### Qtools.py

Define herramientas adicionales o específicas para la aplicación que complementan las herramientas base definidas en el directorio `tools/`.

### conexion.py

Proporciona funcionalidades de conexión a bases de datos, complementando las implementaciones más específicas en el directorio `repositories/`.

## Patrones de Diseño

El módulo QAgent implementa varios patrones de diseño que facilitan la modularidad, extensibilidad y mantenimiento:

1. **Modularidad**: Cada componente tiene una responsabilidad bien definida.
2. **Separación de Preocupaciones (SoC)**: Las diferentes funcionalidades están separadas en módulos específicos.
3. **Dependency Inversion**: Las dependencias apuntan hacia las abstracciones, no hacia las implementaciones concretas.
4. **Factory Method**: Para la creación de objetos, especialmente en las herramientas y manejadores de eventos.
5. **Strategy**: Para intercambiar diferentes implementaciones de comportamiento, particularmente en el manejo de eventos.

## Flujo de Datos

El flujo típico de datos en el módulo QAgent sigue estos pasos:

1. La configuración se carga desde el módulo `config/`
2. Los servicios (como OpenAI) se inicializan usando esta configuración
3. Cuando llega una solicitud del usuario, se maneja a través de eventos
4. Los manejadores de eventos utilizan las estrategias apropiadas para procesar la solicitud
5. Las herramientas se utilizan para realizar acciones específicas (consultas a BD, gráficos, etc.)
6. Los resultados se devuelven al usuario a través de la interfaz de Chainlit

Este diseño permite que cada componente se pruebe y mantenga de forma independiente, facilitando la evolución del sistema. 