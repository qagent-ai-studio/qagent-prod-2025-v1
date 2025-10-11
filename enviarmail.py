import requests


def enviar_mail(email: str, nombre: str, texto: str) -> str:
    """
    Envía un correo simple usando la API HTTP de Mailjet (equivalente a la llamada cURL).
    
    Args:
        email: Dirección de correo del destinatario
        nombre: Nombre del destinatario
        texto: Contenido del correo
    Returns:
        Mensaje de confirmación
    """
    try:
        api_key = "288c5c6fe3b9bcf3ae5571151fbecf46"
        api_secret = "f665f49a5eca8efc78b748daa7a3d880"

        if not api_key or not api_secret:
            return "Error: No se encontraron credenciales de Mailjet."

        url = "https://api.mailjet.com/v3.1/send"
        headers = {"Content-Type": "application/json"}

        data = {
            "Messages": [
                {
                    "From": {
                        "Email": "eduardo@qagent.cl",
                        "Name": "QAgent"
                    },
                    "To": [
                        {
                            "Email": email,
                            "Name": nombre
                        }
                    ],
                    "Subject": "Mensaje de QAgent test 4",
                    "TextPart": texto,
                    "HTMLPart": f"<p>{texto}</p>",
                    "CustomID": "QAgent-SimpleMail"
                }
            ]
        }

        response = requests.post(
            url,
            auth=(api_key, api_secret),
            headers=headers,
            json=data
        )

        sc = response.status_code
        print(f"sc:{sc}")
        body_text = response.text
        
        print(f"body_text:{body_text}")
          
        try:
            body_json = response.json()
            print(f"body_text JS:{body_json}")
        except Exception:
            body_json = None
        
        if response.status_code == 200:
            return f"Correo enviado a {nombre} <{email}>"
        else:
            return f"Error al enviar correo: {response.status_code} {response.text}"

    except Exception as e:
        return f"Excepción al enviar correo: {e}"
  
  
enviar_mail("emunizaga@makertools.cl","Eduardo", "Hola esto es un test" )