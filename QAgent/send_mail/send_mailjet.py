# -*- coding: utf-8 -*-

import logging
import os
import base64
import glob

from mailjet_rest import Client
from jinja2 import Template

logger = logging.getLogger(__name__)

def busca_excel():
    """
    Busca el archivo Excel más reciente en la carpeta .files
    
    Returns:
        Ruta relativa al archivo Excel
    """
    try:
        base_path = r"/Users/pablozunigavalenzuela/Documents/MCP/refactor_v1/.files"

        # Buscar la carpeta más reciente
        folders = [os.path.join(base_path, d) for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        if not folders:
            raise Exception("No se encontraron carpetas dentro de .files")

        latest_folder = max(folders, key=os.path.getmtime)

        # Buscar el Excel más reciente dentro de la carpeta
        excel_files = glob.glob(os.path.join(latest_folder, '*.xlsx')) + glob.glob(os.path.join(latest_folder, '*.xls'))
        if not excel_files:
            raise Exception(f"No se encontraron archivos Excel dentro de {latest_folder}")

        latest_excel = max(excel_files, key=os.path.getmtime)

        # Guardar la ruta en file_path
        file_path = latest_excel

        # Mostrar resultados
        folder_name = os.path.basename(latest_folder)
        file_name = os.path.basename(latest_excel)
        
        return f"{folder_name}/{file_name}"
    except Exception as e:
        logger.error(f"Error en busca_excel: {e}")
        return None


def conversion_excel():
    """
    Lee el archivo Excel y lo convierte a base64
    
    Returns:
        Contenido del archivo en base64
    """
    try:
        fp = busca_excel()
        if not fp:
            return None
            
        file_path = f"/Users/pablozunigavalenzuela/Documents/MCP/refactor_v1/.files/{fp}"   
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error en conversion_excel: {e}")
        return None


def enviar_mail(nombre, email, texto):
    """
    Envía un correo electrónico con un archivo Excel adjunto
    
    Args:
        nombre: Nombre del destinatario
        email: Dirección de correo del destinatario
        texto: Contenido del correo
    """
    try:
        from QAgent.config.config_manager import config
        
        api_key = config.get("MAIL_JET_KEY")
        api_secret = config.get("MAIL_JET_SECRET")
        
        if not api_key or not api_secret:
            logger.error("No se han configurado las credenciales de Mailjet")
            return False
        
        # Buscamos la plantilla de correo
        template_mail = "/Users/pablozunigavalenzuela/Documents/MCP/refactor_v1/QAgent/send_mail/mail.html"
        if not os.path.exists(template_mail):
            # Si no existe la plantilla, creamos una básica
            with open(template_mail, 'w', encoding='utf-8') as f:
                f.write("""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Correo de QAgent</title>
                </head>
                <body>
                    <div style="font-family: Arial, sans-serif; padding: 20px;">
                        <h2>Reporte generado por QAgent</h2>
                        <p>{{ texto }}</p>
                        <p>Adjunto encontrarás el archivo solicitado.</p>
                        <p style="color: #555; font-size: 12px;">Este es un correo automático, por favor no responder.</p>
                    </div>
                </body>
                </html>
                """)
        
        # Carga la plantilla HTML
        with open(template_mail, 'r', encoding='utf-8') as file:
            html_template = file.read()
      
        # Crea un objeto Template
        template = Template(html_template)

        # Datos a reemplazar
        datos = {
            "texto": texto,
        }

        # Renderiza la plantilla con los datos
        plantilla_mail = template.render(datos)
        
        # Convertir el Excel a base64
        excel_base64 = conversion_excel()
        
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        
        # Preparar la data del mensaje
        message_data = {
          "From": {
            "Email": "qagent@makertools.cl",
            "Name": "QAgent"
          },
          "To": [
            {
              "Email": email,
              "Name": nombre
            }
          ],
          "Subject": f"Reporte",
          "TextPart": "Adjunto encontrarás tu reporte en formato Excel.",
          "HTMLPart": plantilla_mail,
          "CustomID": "QAgent-Report"
        }
        
        # Agregar el adjunto si existe
        if excel_base64:
            message_data['Attachments'] = [
                {
                  "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                  "Filename": f"reporte.xlsx",
                  "Base64Content": excel_base64
                }
            ]
        
        # Enviar el mensaje
        data = {
          'Messages': [message_data]
        }
        
        result = mailjet.send.create(data=data)
        logger.info(f"Resultado del envío: {result.status_code}")
        
        return result.status_code == 200
        
    except Exception as e:
        logger.error(f"Error en enviar_mail: {e}")
        return False
