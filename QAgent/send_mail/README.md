# Módulo de Envío de Correos

El módulo `send_mail` proporciona funcionalidades para el envío de correos electrónicos desde la aplicación, utilizando el servicio Mailjet como proveedor principal. Este módulo permite la comunicación con usuarios y administradores a través de correo electrónico para notificaciones, alertas y reportes.

## Estructura del Módulo

```
send_mail/
├── __init__.py          # Exportación de funcionalidades
└── send_mailjet.py      # Implementación usando Mailjet
```

## Archivos Principales

### send_mailjet.py

Implementa la funcionalidad de envío de correos electrónicos utilizando la API de Mailjet. Características principales:

- **Conexión con API Mailjet**: Establece y gestiona la conexión con el servicio.
- **Plantillas de Correo**: Maneja plantillas para diferentes tipos de correos.
- **Personalización de Mensajes**: Permite personalizar los correos con datos dinámicos.
- **Adjuntos**: Soporta el envío de archivos adjuntos.
- **Gestión de Errores**: Maneja errores de conexión y envío.
- **Verificación de Entrega**: Verifica si los correos han sido entregados correctamente.

## Funcionalidades Principales

### Envío de Correos Simples

```python
async def send_simple_email(to_email, subject, text_content, html_content=None):
    """
    Envía un correo electrónico simple.
    
    Args:
        to_email: Dirección de correo del destinatario
        subject: Asunto del correo
        text_content: Contenido en texto plano
        html_content: Contenido HTML (opcional)
        
    Returns:
        Resultado del envío
    """
    # Implementación del envío de correo
```

### Envío de Correos con Plantillas

```python
async def send_template_email(to_email, template_id, variables):
    """
    Envía un correo utilizando una plantilla predefinida.
    
    Args:
        to_email: Dirección de correo del destinatario
        template_id: ID de la plantilla en Mailjet
        variables: Variables para personalizar la plantilla
        
    Returns:
        Resultado del envío
    """
    # Implementación del envío de correo con plantilla
```

### Envío de Reportes

```python
async def send_report(to_email, subject, report_data, report_file=None):
    """
    Envía un reporte por correo electrónico.
    
    Args:
        to_email: Dirección de correo del destinatario
        subject: Asunto del correo
        report_data: Datos del reporte
        report_file: Archivo de reporte adjunto (opcional)
        
    Returns:
        Resultado del envío
    """
    # Implementación del envío de reporte
```

## Integración con Mailjet

El módulo utiliza la API oficial de Mailjet para enviar correos:

1. Las credenciales de Mailjet se obtienen de la configuración.
2. Se establece una conexión con la API de Mailjet.
3. Se construye la estructura del mensaje según los parámetros.
4. Se envía el mensaje a través de la API.
5. Se procesa la respuesta y se maneja cualquier error.

## Configuración

El módulo obtiene la configuración necesaria del módulo `config`:

```python
from QAgent.config.config_manager import config

MAILJET_KEY = config.get('MAIL_JET_KEY')
MAILJET_SECRET = config.get('MAIL_JET_SECRET')
```

## Patrones y Principios

1. **Facade**: Proporciona una interfaz simplificada para la API de Mailjet.
2. **Adaptador**: Adapta la API externa a una interfaz coherente con el resto de la aplicación.
3. **Plantillas**: Utiliza plantillas para la generación de contenido de correos.
4. **Factory Method**: Para crear diferentes tipos de mensajes de correo.

## Uso del Módulo

```python
from QAgent.send_mail.send_mailjet import send_simple_email

# Enviar un correo de notificación
await send_simple_email(
    to_email="usuario@example.com",
    subject="Notificación Importante",
    text_content="Este es un mensaje importante sobre su cuenta.",
    html_content="<p>Este es un <strong>mensaje importante</strong> sobre su cuenta.</p>"
) 