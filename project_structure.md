# Estructura del Proyecto QAgent

Este proyecto implementa un asistente virtual interactivo utilizando Chainlit como interfaz y OpenAI Assistant como motor de inteligencia artificial. El proyecto sigue una arquitectura modular basada en patrones de diseño modernos para facilitar su mantenimiento y extensibilidad.

## Estructura General

```
.
├── QAgent/                # Módulo principal con toda la lógica de negocio
│   ├── config/            # Configuración centralizada 
│   ├── events/            # Manejo de eventos y estrategias
│   ├── repositories/      # Acceso a datos y persistencia
│   ├── services/          # Servicios externos (OpenAI)
│   ├── tools/             # Herramientas disponibles para el asistente
│   ├── utils/             # Utilidades generales
│   └── send_mail/         # Funcionalidad para envío de correos
├── app.py                 # Punto de entrada principal de la aplicación
├── requirements.txt       # Dependencias del proyecto
├── chainlit.md            # Documentación de Chainlit
└── README.md              # Documentación general del proyecto
```

## Archivos Principales

### app.py

El punto de entrada principal de la aplicación que integra Chainlit con OpenAI Assistant. Este archivo:

- Configura la autenticación de usuarios
- Inicializa los servicios necesarios (OpenAI, base de datos)
- Define los manejadores de eventos para la interfaz de chat
- Implementa la lógica de procesamiento de mensajes
- Gestiona las sesiones y la persistencia de conversaciones

El flujo principal incluye:
1. Inicio de sesión del usuario
2. Creación de un hilo de conversación
3. Procesamiento de mensajes del usuario
4. Ejecución de respuestas mediante OpenAI
5. Presentación de resultados en la interfaz de Chainlit

### requirements.txt

Lista todas las dependencias del proyecto, incluyendo:
- chainlit==2.0.0: Framework para crear interfaces de chat
- openai==1.59.4: Cliente oficial de OpenAI
- asyncpg==0.30.0: Cliente PostgreSQL asíncrono
- mysql-connector-python==9.1.0: Cliente MySQL para Python
- pandas==2.2.3 y plotly==5.24.1: Para análisis y visualización de datos

### README.md

Documentación general del proyecto con información sobre instalación, configuración y uso.

## Patrones de Diseño Utilizados

El proyecto implementa varios patrones de diseño:

1. **Singleton**: Utilizado en el ConfigManager para centralizar la configuración
2. **Factory Method**: Implementado en EventHandlerFactory para crear manejadores de eventos
3. **Strategy**: Utilizado en las estrategias de eventos para diferentes proveedores
4. **Repository**: Para abstraer el acceso a datos
5. **Dependency Injection**: Para inyectar dependencias en los servicios

## Flujo de Trabajo

1. El usuario accede a la interfaz web proporcionada por Chainlit
2. La autenticación se realiza mediante usuario/contraseña
3. Al iniciar un chat, se crea un nuevo hilo en OpenAI
4. Los mensajes del usuario se envían al hilo de OpenAI
5. Las respuestas se procesan y se muestran en la interfaz
6. Las herramientas personalizadas permiten que el asistente realice acciones específicas (consultas a base de datos, gráficos, etc.)

Este diseño modular permite una fácil extensión y mantenimiento del sistema, facilitando la adición de nuevas funcionalidades o la modificación de las existentes. 