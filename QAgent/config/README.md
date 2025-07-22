# Módulo de Configuración

El módulo `config` implementa una solución centralizada para la gestión de configuraciones en toda la aplicación, utilizando el patrón de diseño Singleton para garantizar una única instancia de configuración.

## Estructura del Módulo

```
config/
├── __init__.py           # Exporta las clases principales
└── config_manager.py     # Implementación del gestor de configuración
```

## Archivos Principales

### __init__.py

Este archivo exporta la clase principal y la instancia Singleton del gestor de configuración, permitiendo que otros módulos importen y utilicen directamente la configuración.

### config_manager.py

Implementa el `ConfigManager`, una clase que sigue el patrón Singleton para gestionar todas las configuraciones de la aplicación. Sus principales características son:

- **Patrón Singleton**: Garantiza que solo existe una instancia de la configuración en toda la aplicación.
- **Carga desde Variables de Entorno**: Utiliza la biblioteca `dotenv` para cargar variables desde archivos `.env`.
- **Validación de Configuración**: Valida la presencia de configuraciones críticas.
- **Acceso Centralizado**: Proporciona un punto único de acceso a todas las configuraciones.

## Uso del Módulo

El módulo se utiliza en toda la aplicación para acceder a configuraciones, evitando la dispersión de valores de configuración en el código. Por ejemplo:

```python
from QAgent.config.config_manager import config

# Acceder a configuraciones
api_key = config.get('OPENAI_API_KEY')
db_uri = config.get('CHAINLIT_DB_URI')
```

## Patrones de Diseño

1. **Singleton**: El patrón más prominente en este módulo, asegura que solo existe una instancia de la configuración.
2. **Lazy Loading**: La configuración se carga solo cuando se necesita por primera vez.
3. **Encapsulación**: Los detalles de implementación están ocultos, exponiendo solo una interfaz simple para obtener valores.

## Ventajas

- **Consistencia**: Todas las partes de la aplicación acceden a los mismos valores de configuración.
- **Centralización**: Facilita los cambios en la configuración, ya que están en un solo lugar.
- **Mantenibilidad**: Mejora la claridad del código al separar claramente la configuración de la lógica.
- **Flexibilidad**: Permite cambiar fácilmente entre diferentes fuentes de configuración (variables de entorno, archivos, etc.). 