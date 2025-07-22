# QAgent Refactorizado - FastAPI + Chainlit

## Versión de Python y Tecnologías

Este proyecto utiliza:

-   **Python 3.11.5** con entorno virtual creado con pyenv
-   **FastAPI** como framework web principal
-   **Chainlit 2.2.5** montado en FastAPI para la interfaz de chat
-   **PostgreSQL** como base de datos principal

## Descripción

Esta es una versión refactorizada del proyecto QAgent, un asistente basado en OpenAI para consultas de datos. La aplicación está construida con **FastAPI** y tiene **Chainlit montado** para proporcionar una interfaz de chat interactiva.

La refactorización se ha realizado aplicando varios patrones de diseño para mejorar la estructura, mantenibilidad y escalabilidad del código, además de integrar una interfaz web moderna para visualización de gráficos.

## Arquitectura de la Aplicación

La aplicación combina:

-   **FastAPI** como servidor principal con endpoints REST
-   **Chainlit** montado en la ruta raíz (`/`) para la interfaz de chat
-   **Endpoints personalizados** para funcionalidades específicas:
    -   `/graphs` - Página de visualización de gráficos
    -   `/api/pinned-graphs` - API para obtener gráficos fijados
    -   `/api/user` - API para información de usuario

Para más información sobre la integración FastAPI + Chainlit, consulta: [FastAPI - Chainlit Documentation](https://docs.chainlit.io/integrations/fastapi)

## Estructura de Directorios

```
refactor_v1/
├── main.py                    # Punto de entrada FastAPI principal
├── app.py                     # Aplicación Chainlit
├── requirements.txt           # Dependencias del proyecto
├── .env.example               # Plantilla para variables de entorno
├── public/                    # Archivos estáticos
│   ├── elements/              # Componentes JavaScript
│   │   └── GraphsPageNEW.js   # Página de gráficos con drag & drop
│   └── storage/               # Almacenamiento de gráficos
├── templates/                 # Plantillas HTML
│   └── graphs.html            # Template para página de gráficos
├── QAgent/
│   ├── __init__.py            # Mantiene compatibilidad con importaciones
│   ├── config/                # Configuración centralizada
│   │   ├── __init__.py
│   │   └── config_manager.py  # Singleton para gestión de configuración
│   ├── conexion.py            # Compatibilidad con código existente
│   ├── events/                # Manejo de eventos
│   │   ├── __init__.py
│   │   ├── event_handler.py   # Factory y clase base de manejadores
│   │   └── strategies/        # Implementaciones específicas de estrategias
│   │       ├── __init__.py
│   │       └── openai_event_strategy.py # Estrategia para eventos de OpenAI
│   ├── prompt.py              # Instrucciones para el asistente
│   ├── repositories/          # Acceso a datos
│   │   ├── __init__.py
│   │   ├── db_repository.py   # Interfaz abstracta para repositorios
│   │   ├── mysql_repository.py # Implementación para MySQL
│   │   └── postgres_repository.py # Implementación para PostgreSQL
│   ├── services/              # Servicios de la aplicación
│   │   ├── __init__.py
│   │   └── openai_service.py  # Servicio para interactuar con OpenAI
│   ├── tools/                 # Herramientas del asistente
│   │   ├── __init__.py        # Exporta CUSTOM_TOOLS compatible
│   │   ├── base_tool.py       # Clase base para herramientas
│   │   ├── data_tools.py      # Herramientas para datos (getdata)
│   │   ├── plotting_tools.py  # Herramientas para gráficos
│   │   ├── tool_factory.py    # Factory para crear herramientas
│   │   └── utility_tools.py   # Herramientas de utilidad (fecha, correo)
│   └── utils/                 # Utilidades generales
│       ├── __init__.py
│       └── logging_utils.py   # Configuración de logging y notificaciones
```

## Patrones de Diseño Aplicados

### 1. Singleton

-   **ConfigManager**: Centraliza la configuración y el acceso a variables de entorno
-   **OpenAIService**: Encapsula las interacciones con la API de OpenAI
-   **Repositorios**: Gestiona las conexiones a bases de datos
-   **ToolFactory**: Gestiona el registro y creación de herramientas

### 2. Repository

-   **DBRepository**: Interfaz abstracta para el acceso a datos
-   **MySQLRepository y PostgresRepository**: Implementaciones concretas para diferentes BBDD

### 3. Factory

-   **EventHandlerFactory**: Crea diferentes manejadores de eventos según la estrategia
-   **ToolFactory**: Crea y gestiona herramientas para el asistente

### 4. Strategy

-   **EventStrategy**: Define la interfaz para diferentes estrategias de manejo de eventos
-   **OpenAIEventStrategy**: Implementación específica para eventos de OpenAI

## Funcionalidades Principales

### 1. Interfaz de Chat (Chainlit)

-   Asistente conversacional para consultas de datos
-   Integración con OpenAI para procesamiento de lenguaje natural
-   Herramientas personalizadas para análisis de datos logísticos

### 2. Visualización de Gráficos

-   Página dedicada para visualizar gráficos guardados (`/graphs`)
-   Sistema de gráficos "fijados" que se pueden gestionar
-   Controles de redimensionamiento (1, 2, 3 columnas)
-   Sistema de reordenamiento con botones ↑ ↓
-   Persistencia local de configuración (tamaños y posiciones)

### 3. API REST

-   Endpoints para gestión de gráficos
-   Autenticación integrada con Chainlit
-   Acceso a datos de usuario

### 4. Documentación Automática de API

FastAPI incluye automáticamente documentación interactiva:

-   **Swagger UI**: Interfaz interactiva para probar endpoints en `/docs`
-   **ReDoc**: Documentación alternativa más detallada en `/redoc`
-   **OpenAPI Schema**: Esquema JSON disponible en `/openapi.json`
-   **Validación automática**: Tipos de datos y validación de requests/responses

## Instalación y Configuración

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Copia el archivo `.env.example` a `.env` y configura las variables según tu entorno:

```bash
cp .env.example .env
# Edita el archivo .env con tus valores
```

Variables principales:

```env
OPENAI_API_KEY=tu_api_key_aquí
CHAINLIT_DB_URI=postgresql+psycopg2://usuario:password@localhost/dbname
```

### 3. Ejecutar la Aplicación

La aplicación se ejecuta con **uvicorn** (no con `chainlit run`):

```bash
uvicorn main:app --reload --port 8000
```

La aplicación estará disponible en:

-   **Chat principal**: http://localhost:8000 (Chainlit)
-   **Página de gráficos**: http://localhost:8000/graphs
-   **API**: http://localhost:8000/api/\*
-   **Documentación API (Swagger)**: http://localhost:8000/docs
-   **Documentación API (ReDoc)**: http://localhost:8000/redoc

### Parámetros de uvicorn:

-   `--reload`: Recarga automática al detectar cambios en el código
-   `--port 8000`: Puerto de ejecución
-   `main:app`: Referencia al objeto FastAPI en main.py

### En caso de bloqueo de puerto

```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## Cambios Principales en esta Versión

1. **Migración a FastAPI**: La aplicación ahora usa FastAPI como framework principal
2. **Chainlit montado**: Chainlit se ejecuta como una aplicación montada en FastAPI
3. **Interfaz de gráficos mejorada**: Sistema completo de gestión de gráficos con persistencia
4. **API REST integrada**: Endpoints personalizados para funcionalidades específicas
5. **Configuración centralizada**: Las variables de entorno y configuraciones se gestionan desde un único punto
6. **Separación de responsabilidades**: Cada componente tiene una función específica y bien definida
7. **Mejora en el manejo de errores**: Gestión consistente y centralizada de errores

## Migración Gradual

Esta refactorización está diseñada para permitir una migración gradual desde la versión original:

1. Los módulos nuevos funcionan junto a los antiguos
2. La estructura mantiene compatibilidad con importaciones existentes
3. Las funciones exportadas mantienen las mismas firmas y nombres
4. Los repositorios se pueden activar uno a uno

## Desarrollo y Debugging

### Logs de la Aplicación

Los logs incluyen información detallada sobre:

-   Inicialización de componentes
-   Procesamiento de gráficos
-   Autenticación de usuarios
-   Errores y excepciones

### Modo de Desarrollo

Para desarrollo local, uvicorn proporciona:

-   Recarga automática con `--reload`
-   Logs detallados en consola
-   Manejo de errores mejorado

## Próximos Pasos

1. Implementar tests unitarios para cada componente
2. Mejorar la documentación con docstrings más detallados
3. Agregar nuevas estrategias de eventos para diferentes asistentes
4. Implementar más herramientas específicas para el dominio
5. Expandir la API REST con más endpoints
6. Agregar autenticación avanzada y gestión de usuarios
