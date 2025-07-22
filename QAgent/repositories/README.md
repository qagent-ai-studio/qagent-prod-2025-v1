# Módulo de Repositorios

El módulo `repositories` implementa el patrón de diseño Repository para abstraer y encapsular toda la lógica necesaria para acceder a fuentes de datos. Proporciona una capa de abstracción que media entre la lógica de negocio y las bases de datos, permitiendo un acceso estandarizado independientemente de la tecnología subyacente.

## Estructura del Módulo

```
repositories/
├── __init__.py              # Exportación de repositorios
├── db_repository.py         # Interfaz y base abstracta para repositorios
├── mysql_repository.py      # Implementación para MySQL
└── postgres_repository.py   # Implementación para PostgreSQL
```

## Archivos Principales

### db_repository.py

Define la interfaz base y clases abstractas para todos los repositorios de datos. Características:

- **Clases Abstractas**: Define interfaces comunes para todos los repositorios.
- **Métodos Genéricos**: Establece métodos estándar para operaciones CRUD.
- **Manejo de Transacciones**: Define patrones para la gestión de transacciones.

### mysql_repository.py

Implementa el repositorio específico para MySQL:

- **Conexiones Asíncronas**: Utiliza `aiomysql` para operaciones asíncronas.
- **Gestión de Conexiones**: Maneja pools de conexiones y recursos.
- **Operaciones CRUD**: Implementa operaciones específicas para MySQL.
- **Manejo de Errores**: Gestiona errores específicos de MySQL.

### postgres_repository.py

Implementa el repositorio específico para PostgreSQL:

- **Conexiones Asíncronas**: Utiliza `asyncpg` para operaciones asíncronas.
- **Optimizaciones**: Implementa características específicas de PostgreSQL.
- **Operaciones CRUD**: Proporciona métodos adaptados a PostgreSQL.
- **Gestión de Transacciones**: Maneja transacciones en PostgreSQL.

## Patrones de Diseño

1. **Repository**: El patrón principal, abstrae el acceso a datos.
2. **Factory Method**: Para crear instancias de repositorios específicos.
3. **Strategy**: Diferentes implementaciones para diferentes bases de datos.
4. **Template Method**: Define el flujo general en clases base con implementaciones específicas en subclases.

## Ventajas del Patrón Repository

- **Desacoplamiento**: Separa la lógica de negocio del acceso a datos.
- **Testabilidad**: Facilita las pruebas al permitir repositorios simulados (mocks).
- **Flexibilidad**: Permite cambiar la fuente de datos sin afectar la lógica de negocio.
- **Consistencia**: Proporciona una interfaz uniforme para acceder a diferentes fuentes de datos.
- **Centralización**: Centraliza la lógica de acceso a datos y manejo de errores.

## Uso del Módulo

Los repositorios se utilizan principalmente en las herramientas de datos y en otras partes del sistema que necesitan acceso a datos:

```python
from QAgent.repositories import MySQLRepository

# Crear un repositorio
repo = MySQLRepository(host, user, password, database)

# Ejecutar una consulta
results = await repo.execute_query("SELECT * FROM productos WHERE id = %s", (product_id,))

# Cerrar el repositorio cuando ya no se necesita
await repo.close()
```

## Transacciones

Los repositorios también soportan transacciones para operaciones que requieren integridad:

```python
async with repo.transaction() as tx:
    # Todas las operaciones dentro de este bloque son parte de la misma transacción
    await tx.execute("INSERT INTO pedidos (cliente_id, fecha) VALUES (%s, %s)", (1, "2023-05-01"))
    pedido_id = await tx.fetchval("SELECT LAST_INSERT_ID()")
    await tx.execute("INSERT INTO detalles_pedido (pedido_id, producto_id) VALUES (%s, %s)", (pedido_id, 101))
    # Si no hay excepciones, la transacción se confirma automáticamente
    # Si hay una excepción, la transacción se revierte
``` 